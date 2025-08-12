import streamlit as st
import asyncio
import concurrent.futures
import os
import base64
import time
from io import StringIO
import PyPDF2
import docx
from pathlib import Path
from styles import StreamlitChatTheme, ThemePresets

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

def get_base64_of_bin_file(bin_file):
    """Get base64 encoding of binary file."""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def load_css():
    """Load CSS from external file"""
    css_file = "style.css"
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

def extract_text_from_pdf(file_bytes):
    """Extract text from PDF file."""
    try:
        from io import BytesIO
        pdf_reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_docx(file_bytes):
    """Extract text from DOCX file."""
    try:
        from io import BytesIO
        doc = docx.Document(BytesIO(file_bytes))
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

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
    # Background with overlay
    st.markdown("""
    <div class="auth-page-background">
        <div class="auth-overlay">
            <div class="auth-title-section">
                <div class="app-title">👔 Mentora – AI Career Advisor</div>
                <div class="app-subtitle">Your personalized AI assistant for career guidance</div>
            </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.markdown("### Login to Your Account")
        st.markdown('<div class="auth-help-text">Welcome back! Please enter your credentials to continue.</div>', unsafe_allow_html=True)
        
        with st.form("login_form"):
            username = st.text_input(
                "Username", 
                key="login_username",
                placeholder="Enter your username",
                help="Your unique username"
            )
            
            password = st.text_input(
                "Password", 
                type="password", 
                key="login_password",
                placeholder="Enter your password",
                help="Your account password"
            )
            
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
        st.markdown('<div class="auth-help-text">Join Mentora today! Fill in the details below to get started with your AI career advisor.</div>', unsafe_allow_html=True)
        
        with st.form("signup_form"):
            new_username = st.text_input(
                "Username", 
                key="signup_username",
                placeholder="Choose a unique username",
                help="This will be your unique identifier"
            )
            new_email = st.text_input(
                "Email", 
                key="signup_email",
                placeholder="your.email@example.com",
                help="We'll use this for account recovery"
            )
            
            new_password = st.text_input(
                "Password", 
                type="password", 
                key="signup_password",
                placeholder="Create a strong password (min. 6 characters)",
                help="Use a mix of letters, numbers, and symbols"
            )
            
            confirm_password = st.text_input(
                "Confirm Password", 
                type="password", 
                key="confirm_password",
                placeholder="Re-enter your password",
                help="Must match the password above"
            )
            
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
    
    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render collapsible sidebar with chat controls"""
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-header">
            <h3>💬 Chat Controls</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # File upload section
        st.markdown("### 📎 Upload Documents")
        uploaded_file = st.file_uploader(
            "Upload PDF or Word document",
            type=['pdf', 'docx', 'doc'],
            help="Upload your resume, cover letter, or any career-related document"
        )
        
        if uploaded_file is not None:
            if st.button("📄 Analyze Document", use_container_width=True):
                with st.spinner("Processing document..."):
                    file_bytes = uploaded_file.read()
                    
                    if uploaded_file.type == "application/pdf":
                        extracted_text = extract_text_from_pdf(file_bytes)
                    elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
                        extracted_text = extract_text_from_docx(file_bytes)
                    else:
                        extracted_text = "Unsupported file type"
                    
                    # Add document analysis to chat
                    if not extracted_text.startswith("Error"):
                        analysis_prompt = f"Please analyze this document and provide career advice:\n\n{extracted_text[:2000]}..."
                        st.session_state.pending_analysis = analysis_prompt
                        st.success(f"Document '{uploaded_file.name}' processed successfully!")
                    else:
                        st.error(extracted_text)
        
        st.markdown("---")
        
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
    
    # Main header - redesigned and compact with FIXED LAYOUT
    st.markdown("""
    <div class="app-header-compact">
        <button class="sidebar-toggle" onclick="toggleSidebar()">☰</button>
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
    st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)
    
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

    # Fixed bottom input area - USING NEW CLASS NAME
    # st.markdown('<div class="chat-input-fixed">', unsafe_allow_html=True)

    # Voice input section
    st.markdown("""
    <div class="voice-section">
        <button class="voice-button" id="voice-btn" onclick="toggleVoiceRecording()">
            🎤 Voice Input
        </button>
        <span id="voice-status" class="voice-status"></span>
    </div>
    """, unsafe_allow_html=True)

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

    # Close fixed bottom div
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
    if "pending_analysis" not in st.session_state:
        st.session_state.pending_analysis = None
    if "sidebar_collapsed" not in st.session_state:
        st.session_state.sidebar_collapsed = False

def main():
    """Main application function"""
    # Streamlit configuration
    st.set_page_config(
        page_title="Mentora - AI Career Advisor",
        page_icon="👔",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # theme = StreamlitChatTheme(ThemePresets.green_farm_theme())
    # theme.apply_theme()

    # Load external CSS
    load_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Handle pending document analysis
    if st.session_state.pending_analysis and st.session_state.authenticated:
        handle_chat_submission(st.session_state.pending_analysis)
        st.session_state.pending_analysis = None
        st.rerun()
    
    # Route to appropriate interface
    if not st.session_state.authenticated:
        render_auth_form()
    else:
        submit_button, user_input = render_main_interface()
        
        # Process user input
        if submit_button and user_input and user_input.strip() and not st.session_state.is_processing:
            handle_chat_submission(user_input)
            st.rerun()

    # JavaScript for enhanced UX - COMPLETE AND ENHANCED
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

    // ENHANCED SIDEBAR TOGGLE FUNCTIONALITY
    function toggleSidebar() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        const sidebarContent = document.querySelector('.stSidebar');
        
        if (sidebar || sidebarContent) {
            const element = sidebar || sidebarContent;
            
            // Toggle collapsed class
            if (element.classList.contains('collapsed')) {
                element.classList.remove('collapsed');
                element.style.transform = 'translateX(0)';
                element.style.transition = 'transform 0.3s ease';
            } else {
                element.classList.add('collapsed');
                element.style.transform = 'translateX(-100%)';
                element.style.transition = 'transform 0.3s ease';
            }
        }
    }

    // Voice recording functionality
    let isRecording = false;
    let recognition = null;
    
    function toggleVoiceRecording() {
        const voiceBtn = document.getElementById('voice-btn');
        const voiceStatus = document.getElementById('voice-status');
        
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            voiceStatus.textContent = 'Voice recognition not supported';
            voiceStatus.style.color = '#ef4444';
            return;
        }
        
        if (!isRecording) {
            startRecording();
        } else {
            stopRecording();
        }
    }
    
    function startRecording() {
        const voiceBtn = document.getElementById('voice-btn');
        const voiceStatus = document.getElementById('voice-status');
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        
        recognition.onstart = function() {
            isRecording = true;
            voiceBtn.textContent = '🔴 Stop Recording';
            voiceBtn.style.background = '#ef4444';
            voiceStatus.textContent = 'Listening...';
            voiceStatus.style.color = '#10b981';
        };
        
        recognition.onresult = function(event) {
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                }
            }
            
            if (finalTranscript) {
                const inputField = document.querySelector('input[data-testid="stTextInput"]');
                if (inputField) {
                    inputField.value = finalTranscript;
                    inputField.dispatchEvent(new Event('input', { bubbles: true }));
                }
                stopRecording();
            }
        };
        
        recognition.onerror = function(event) {
            voiceStatus.textContent = 'Error: ' + event.error;
            voiceStatus.style.color = '#ef4444';
            stopRecording();
        };
        
        recognition.start();
    }
    
    function stopRecording() {
        const voiceBtn = document.getElementById('voice-btn');
        const voiceStatus = document.getElementById('voice-status');
        
        if (recognition) {
            recognition.stop();
        }
        
        isRecording = false;
        voiceBtn.textContent = '🎤 Voice Input';
        voiceBtn.style.background = '';
        voiceStatus.textContent = '';
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
        
        // Initialize sidebar state
        const sidebar = document.querySelector('[data-testid="stSidebar"]') || 
                      document.querySelector('.stSidebar');
        if (sidebar) {
            // Ensure sidebar starts expanded on desktop
            if (window.innerWidth > 768) {
                sidebar.classList.remove('collapsed');
                sidebar.style.transform = 'translateX(0)';
            } else {
                // On mobile, start collapsed
                sidebar.classList.add('collapsed');
                sidebar.style.transform = 'translateX(-100%)';
            }
        }
        
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
    
    // Enhanced cursor visibility for input fields
    const addCursorStyles = function() {
        if (!document.getElementById('cursor-styles')) {
            const style = document.createElement('style');
            style.id = 'cursor-styles';
            style.textContent = `
                input[type="text"], input[type="password"], input[type="email"] {
                    caret-color: #3b82f6 !important;
                    caret-width: 2px !important;
                }
                input:focus {
                    caret-color: #1d4ed8 !important;
                }
            `;
            document.head.appendChild(style);
        }
    };
    
    // Add cursor styles on load and after DOM changes
    document.addEventListener('DOMContentLoaded', addCursorStyles);
    setTimeout(addCursorStyles, 1000);

    // Handle window resize for responsive sidebar
    window.addEventListener('resize', function() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]') || 
                      document.querySelector('.stSidebar');
        if (sidebar) {
            if (window.innerWidth <= 768) {
                // On mobile, sidebar should be collapsed by default
                sidebar.classList.add('collapsed');
                sidebar.style.transform = 'translateX(-100%)';
            } else {
                // On desktop, sidebar should be expanded by default
                sidebar.classList.remove('collapsed');
                sidebar.style.transform = 'translateX(0)';
            }
        }
    });

    // Ensure smooth transitions
    setTimeout(function() {
        const sidebar = document.querySelector('[data-testid="stSidebar"]') || 
                      document.querySelector('.stSidebar');
        if (sidebar) {
            sidebar.style.transition = 'transform 0.3s ease';
        }
    }, 100);
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()