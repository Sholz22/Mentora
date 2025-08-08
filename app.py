import streamlit as st
import asyncio
import threading
import concurrent.futures
import uuid
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

from main import handle_user_input_async

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
    """Render the welcome message when no chat history exists"""
    st.markdown("""
    <div class="welcome-message">
        <div class="welcome-title">👋 Welcome to Mentora!</div>
        <div class="welcome-features">
            <div class="feature-item">🎯 Career planning and transitions</div>
            <div class="feature-item">📚 Skill development recommendations</div>
            <div class="feature-item">💼 Job market insights</div>
            <div class="feature-item">📋 Resume and interview guidance</div>
            <div class="feature-item">💰 Salary negotiations</div>
        </div>
        <div class="welcome-cta">Start by asking me anything about your career!</div>
    </div>
    """, unsafe_allow_html=True)

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
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# Main container
# st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="app-header">
    <div class="app-title">👔 Mentora – AI Career Advisor</div>
    <div class="app-subtitle">Your personalized AI assistant for career guidance, skill development, and professional growth.</div>
</div>
""", unsafe_allow_html=True)

# Clear button
if st.session_state.chat_history:
    st.markdown("""
    <div class="clear-button-container">
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 8])
    with col1:
        if st.button("Clear", key="clear_btn", help="Clear chat history"):
            st.session_state.chat_history = []
            st.rerun()

# Chat messages container
# st.markdown('<div class="chat-messages">', unsafe_allow_html=True)

if st.session_state.chat_history:
    for speaker, message in st.session_state.chat_history:
        is_user = "You" in speaker
        render_message(speaker, message, is_user)
else:
    render_welcome_message()

st.markdown('</div>', unsafe_allow_html=True)

# Add some space before the fixed input
# st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)

# Fixed bottom input area
st.markdown("""
<div class="input-container">
    <div class="input-wrapper">
    </div>
</div>
""", unsafe_allow_html=True)

# Create the input form that will be positioned at the bottom
input_container = st.container()
with input_container:
    # Use columns to center the input
    col1, col2, col3 = st.columns([1, 6, 1])
    
    with col2:
        # Create the form for input
        with st.form(key="chat_form", clear_on_submit=True):
            input_col, button_col = st.columns([4, 1])
            
            with input_col:
                user_input = st.text_input(
                    "Message",
                    placeholder="e.g., How do I transition to data science?",
                    label_visibility="collapsed",
                    key="user_input_field",
                    disabled=st.session_state.is_processing
                )
            
            with button_col:
                submit_button = st.form_submit_button(
                    "Send", 
                    disabled=st.session_state.is_processing,
                    use_container_width=True
                )

# Process user input
if submit_button and user_input and user_input.strip() and not st.session_state.is_processing:
    # Set processing state
    st.session_state.is_processing = True
    
    # Add user message to history
    st.session_state.chat_history.append(("👤 You", user_input))
    
    # Show processing state
    with st.spinner("Just a second..."):
        try:
            # Get response from agent
            response = run_async_in_thread(
                handle_user_input_async(st.session_state.user_id, user_input)
            )
            
            # Clean up response
            if response.startswith("⚠️"):
                response_type = "error"
            else:
                response_type = "success"
            
            # Add bot response to history
            st.session_state.chat_history.append(("🤖 Mentora", response))
            
        except Exception as e:
            error_message = f"⚠️ Sorry, I encountered an error: {str(e)}"
            st.session_state.chat_history.append(("🤖 Mentora", error_message))
            st.error(f"Error: {e}")
    
    # Reset processing state
    st.session_state.is_processing = False
    
    # Rerun to update the chat display
    st.rerun()

# Close main container
st.markdown('</div>', unsafe_allow_html=True)

# Add JavaScript for auto-scroll and better UX
st.markdown("""
<script>
// Auto-scroll to bottom when new messages are added
function scrollToBottom() {
    const chatMessages = document.querySelector('.chat-messages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Run on page load
document.addEventListener('DOMContentLoaded', scrollToBottom);

// Also run when content changes (Streamlit updates)
const observer = new MutationObserver(scrollToBottom);
const chatContainer = document.querySelector('.chat-messages');
if (chatContainer) {
    observer.observe(chatContainer, { childList: true, subtree: true });
}

// Handle Enter key in input field
document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        const form = document.querySelector('form[data-testid="stForm"]');
        if (form) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && !submitButton.disabled) {
                event.preventDefault();
                submitButton.click();
            }
        }
    }
});
</script>
""", unsafe_allow_html=True)









# import streamlit as st
# import asyncio
# import threading
# import concurrent.futures

# # Set up event loop for the main thread before importing other modules
# def setup_event_loop():
#     """Set up an event loop for the current thread if one doesn't exist."""
#     try:
#         # Try to get the current event loop
#         loop = asyncio.get_event_loop()
#         if loop.is_closed():
#             # If the loop is closed, create a new one
#             loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(loop)
#     except RuntimeError:
#         # No event loop exists, create one
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#     return loop

# # Set up the event loop before importing modules that need it
# setup_event_loop()

# # Now import your modules
# from main import handle_user_input_async

# def run_async_in_thread(coro):
#     """Run an async function in a separate thread with its own event loop."""
#     def run_in_thread():
#         # Create a new event loop for this thread
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         try:
#             return loop.run_until_complete(coro)
#         finally:
#             loop.close()
    
#     with concurrent.futures.ThreadPoolExecutor() as executor:
#         future = executor.submit(run_in_thread)
#         return future.result()

# # Streamlit configuration
# st.set_page_config(page_title="Mentora", layout="centered")

# st.title("👔 Mentora – AI Career Advisor")
# st.markdown("Ask me about career advice, job opportunities, skill development, or industry trends.")

# # Chat history
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# user_input = st.text_input("You:", key="user_input")

# if st.button("Ask") or user_input:
#     if user_input.strip():
#         with st.spinner("Thinking..."):
#             try:
#                 # Generate a user_id for the session (you can customize this)
#                 if "user_id" not in st.session_state:
#                     import uuid
#                     st.session_state.user_id = str(uuid.uuid4())
                
#                 # Use the thread-based approach to handle async
#                 response = run_async_in_thread(
#                     handle_user_input_async(st.session_state.user_id, user_input)
#                 )
#                 st.session_state.chat_history.append(("👩🏽‍🌾 You", user_input))
#                 st.session_state.chat_history.append(("🤖 Mentora", response))

#             except Exception as e:
#                 st.error(f"Error: {e}")
#                 st.error(f"Error type: {type(e).__name__}")

# # Display conversation
# st.markdown("### Conversation History")
# for speaker, msg in st.session_state.chat_history:
#     if speaker.startswith("👩🏽‍🌾"):
#         st.markdown(f"**{speaker}:** {msg}")
#     else:
#         st.markdown(f"**{speaker}:** {msg}")
#         st.markdown("---")

# # Add a clear chat button
# if st.button("Clear Chat History"):
#     st.session_state.chat_history = []
#     st.rerun()