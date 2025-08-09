import streamlit as st
import asyncio
import concurrent.futures
import os

# Set up event loop for the main thread before importing other modules
def setup_event_loop():
    """Set up an event loop for the current thread if one doesn't exist."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop

setup_event_loop()

# Import modules after event loop setup
from main import handle_user_input_async
from database.logger import (
    create_user, authenticate_user, 
    save_streamlit_chat_history, load_streamlit_chat_history
)

def load_css():
    """Load CSS from external file"""
    css_file = "styles.css"
    if os.path.exists(css_file):
        with open(css_file, "r") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        st.warning("CSS file not found. Using default styling.")

def run_async_in_thread(coro):
    """Run an async function in a separate thread with its own event loop."""
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_thread)
        return future.result()

def render_message(speaker, message, is_user=False):
    """Render a single chat message"""
    message_class = "user" if is_user else "bot"
    avatar = "👤" if is_user else "🤖"
    
    st.markdown(f"""
    <div class="message {message_class}">
        <div class="message-avatar">{avatar}</div>
        <div class="message-bubble">{message}</div>
    </div>
    """, unsafe_allow_html=True)

def render_welcome_message():
    """Render the welcome message with clickable feature items"""
    st.markdown(f"""
    <div class="welcome-message">
        <div class="welcome-title">👋 Welcome back, {st.session_state.username}!</div>
        <div class="welcome-features">
            <div class="feature-item clickable" onclick="setInput('How do I plan a career transition to a new field?')">
                🎯 Career planning and transitions
            </div>
            <div class="feature-item clickable" onclick="setInput('What skills should I develop for my career growth?')">
                📚 Skill development recommendations
            </div>
            <div class="feature-item clickable" onclick="setInput('What are the current job market trends in my industry?')">
                💼 Job market insights
            </div>
            <div class="feature-item clickable" onclick="setInput('Can you help me improve my resume and interview skills?')">
                📋 Resume and interview guidance
            </div>
            <div class="feature-item clickable" onclick="setInput('How should I approach salary negotiations?')">
                💰 Salary negotiations
            </div>
        </div>
        <div class="welcome-cta">Click on any topic above or start by asking me anything about your career!</div>
    </div>
    """, unsafe_allow_html=True)

def render_auth_form():
    """Render login/signup form"""
    st.markdown("""
    <div class="auth-container">
        <div class="auth-header">
            <div class="app-title">👔 Mentora – AI Career Advisor</div>
            <div class="app-subtitle">Your personalized AI assistant for career guidance</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.markdown("### Login to Your Account")
        with st.form("login_form"):
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            login_button = st.form_submit_button("Login", use_container_width=True)
            
            if login_button:
                if username and password:
                    if authenticate_user(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.user_id = username
                        # Load chat history
                        st.session_state.chat_history = load_streamlit_chat_history(username)
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid username or password!")
                else:
                    st.error("Please fill in all fields!")
    
    with tab2:
        st.markdown("### Create New Account")
        with st.form("signup_form"):
            new_username = st.text_input("Username", key="signup_username")
            new_email = st.text_input("Email", key="signup_email")
            new_password = st.text_input("Password", type="password", key="signup_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
            signup_button = st.form_submit_button("Sign Up", use_container_width=True)
            
            if signup_button:
                if new_username and new_email and new_password and confirm_password:
                    if new_password == confirm_password:
                        if len(new_password) >= 6:
                            success, message = create_user(new_username, new_email, new_password)
                            if success:
                                st.success(message)
                                st.info("Please login with your new account!")
                            else:
                                st.error(message)
                        else:
                            st.error("Password must be at least 6 characters long!")
                    else:
                        st.error("Passwords do not match!")
                else:
                    st.error("Please fill in all fields!")

def render_sidebar():
    """Render collapsible sidebar with chat controls"""
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h3>💬 Chat Controls</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # New Chat button
        if st.button("🆕 New Chat", use_container_width=True, key="new_chat_btn"):
            st.session_state.chat_history = []
            save_streamlit_chat_history(st.session_state.username, [])
            st.rerun()
        
        # Clear Chat button
        if st.session_state.chat_history:
            if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_chat_btn"):
                st.session_state.chat_history = []
                save_streamlit_chat_history(st.session_state.username, [])
                st.rerun()
        
        # Chat History Info
        if st.session_state.chat_history:
            st.markdown(f"""
            <div class="chat-info">
                <p>📊 Messages: {len(st.session_state.chat_history)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User Info
        st.markdown(f"""
        <div class="user-info">
            <h4>👤 {st.session_state.username}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            # Save chat history before logout
            save_streamlit_chat_history(st.session_state.username, st.session_state.chat_history)
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def render_main_interface():
    """Render the main chat interface for authenticated users"""
    # Render sidebar
    render_sidebar()
    
    # Main header - redesigned and compact
    st.markdown("""
    <div class="app-header-compact">
        <div class="title-container">
            <div class="mentora-title">
                <span class="title-icon">👔</span>
                <span class="title-text">Mentora</span>
                <span class="title-badge">AI</span>
            </div>
            <div class="title-subtitle">Career Guidance & Professional Growth</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat messages container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if st.session_state.chat_history:
        for speaker, message in st.session_state.chat_history:
            is_user = "You" in speaker
            render_message(speaker, message, is_user)
    else:
        render_welcome_message()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Processing indicator (positioned above input)
    if st.session_state.is_processing:
        st.markdown("""
        <div class="processing-indicator">
            <div class="spinner"></div>
            <span>Just a second...</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Fixed bottom input area - expanded width
    st.markdown('<div class="input-container-fixed">', unsafe_allow_html=True)
    
    # Create the input form
    with st.form(key="chat_form", clear_on_submit=True):
        input_col, button_col = st.columns([6, 1])
        
        with input_col:
            user_input = st.text_input(
                "Message",
                placeholder="Ask me about your career goals, skills, job market trends...",
                label_visibility="collapsed",
                key="user_input_field",
                disabled=st.session_state.is_processing
            )
        
        with button_col:
            submit_button = st.form_submit_button(
                "➤", 
                disabled=st.session_state.is_processing,
                use_container_width=True,
                help="Send message"
            )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return submit_button, user_input

def handle_chat_submission(user_input):
    """Handle chat form submission"""
    # Set processing state
    st.session_state.is_processing = True
    
    # Add user message to history
    st.session_state.chat_history.append(("👤 You", user_input))
    
    try:
        # Get response from agent (pass username for activity tracking)
        response = run_async_in_thread(
            handle_user_input_async(
                st.session_state.user_id, 
                user_input, 
                username=st.session_state.username
            )
        )
        
        # Add bot response to history
        st.session_state.chat_history.append(("🤖 Mentora", response))
        
        # Save to database
        save_streamlit_chat_history(st.session_state.username, st.session_state.chat_history)
        
    except Exception as e:
        error_message = f"⚠️ Sorry, I encountered an error: {str(e)}"
        st.session_state.chat_history.append(("🤖 Mentora", error_message))
        save_streamlit_chat_history(st.session_state.username, st.session_state.chat_history)
        st.error(f"Error: {e}")
    
    # Reset processing state
    st.session_state.is_processing = False

def initialize_session_state():
    """Initialize all session state variables"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "is_processing" not in st.session_state:
        st.session_state.is_processing = False

def main():
    """Main application function"""
    # Streamlit configuration
    st.set_page_config(
        page_title="Mentora - AI Career Advisor",
        page_icon="👔",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load external CSS
    load_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Route to appropriate interface
    if not st.session_state.authenticated:
        render_auth_form()
    else:
        submit_button, user_input = render_main_interface()
        
        # Process user input
        if submit_button and user_input and user_input.strip() and not st.session_state.is_processing:
            handle_chat_submission(user_input)
            st.rerun()

    # JavaScript for enhanced UX
    st.markdown("""
    <script>
    // Function to set input field value
    function setInput(text) {
        const inputField = document.querySelector('input[data-testid="stTextInput"]');
        if (inputField) {
            inputField.value = text;
            inputField.dispatchEvent(new Event('input', { bubbles: true }));
            inputField.focus();
        }
    }

    // Auto-scroll to bottom of chat
    function scrollToBottom() {
        const chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
    }

    // Auto-scroll and enhanced UX
    document.addEventListener('DOMContentLoaded', function() {
        // Add click handlers to feature items
        const featureItems = document.querySelectorAll('.feature-item.clickable');
        featureItems.forEach(item => {
            item.style.cursor = 'pointer';
            item.addEventListener('click', function() {
                const onclick = this.getAttribute('onclick');
                if (onclick) {
                    eval(onclick);
                }
            });
        });
        
        // Scroll to bottom on page load
        setTimeout(scrollToBottom, 100);
    });

    // Handle Enter key in input field
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            const inputField = document.querySelector('input[data-testid="stTextInput"]');
            if (inputField && document.activeElement === inputField) {
                const form = inputField.closest('form');
                if (form) {
                    const submitButton = form.querySelector('button[type="submit"]');
                    if (submitButton && !submitButton.disabled) {
                        event.preventDefault();
                        submitButton.click();
                    }
                }
            }
        }
    });

    // Auto-scroll when new messages are added
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                setTimeout(scrollToBottom, 100);
            }
        });
    });

    const targetNode = document.querySelector('.chat-container');
    if (targetNode) {
        observer.observe(targetNode, { childList: true, subtree: true });
    }
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()