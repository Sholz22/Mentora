import streamlit as st
import asyncio
import threading
import concurrent.futures

# Set up event loop for the main thread before importing other modules
def setup_event_loop():
    """Set up an event loop for the current thread if one doesn't exist."""
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            # If the loop is closed, create a new one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        # No event loop exists, create one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop

# Set up the event loop before importing modules that need it
setup_event_loop()

# Now import your modules
from main import handle_user_input_async

def run_async_in_thread(coro):
    """Run an async function in a separate thread with its own event loop."""
    def run_in_thread():
        # Create a new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_thread)
        return future.result()

# Streamlit configuration
st.set_page_config(page_title="Mentora", layout="centered")

st.title("👔 Mentora – AI Career Advisor")
st.markdown("Ask me about career advice, job opportunities, skill development, or industry trends.")

# Chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("You:", key="user_input")

if st.button("Ask") or user_input:
    if user_input.strip():
        with st.spinner("Thinking..."):
            try:
                # Generate a user_id for the session (you can customize this)
                if "user_id" not in st.session_state:
                    import uuid
                    st.session_state.user_id = str(uuid.uuid4())
                
                # Use the thread-based approach to handle async
                response = run_async_in_thread(
                    handle_user_input_async(st.session_state.user_id, user_input)
                )
                st.session_state.chat_history.append(("👩🏽‍🌾 You", user_input))
                st.session_state.chat_history.append(("🤖 Mentora", response))

            except Exception as e:
                st.error(f"Error: {e}")
                st.error(f"Error type: {type(e).__name__}")

# Display conversation
st.markdown("### Conversation History")
for speaker, msg in st.session_state.chat_history:
    if speaker.startswith("👩🏽‍🌾"):
        st.markdown(f"**{speaker}:** {msg}")
    else:
        st.markdown(f"**{speaker}:** {msg}")
        st.markdown("---")

# Add a clear chat button
if st.button("Clear Chat History"):
    st.session_state.chat_history = []
    st.rerun()