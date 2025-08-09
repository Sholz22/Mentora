from agent.build_agent import build_career_agent
import logging
from database.logger import (
    log_chat, get_chat_history, is_first_time_user, clear_chat_history,
    update_user_last_activity
)

logger = logging.getLogger(__name__)

# Create agent only once to avoid reinitializing
agent = build_career_agent()

async def handle_user_input_async(user_id: str, user_input: str, username: str = None) -> str:
    """
    Async version of handle_user_input for better performance with concurrent requests.
    Added username parameter for user activity tracking.
    """
    if not user_id or not user_id.strip():
        return "⚠️ Error: User ID is required"
    
    if not user_input or not user_input.strip():
        return "⚠️ Please provide a valid input message"
    
    user_input = user_input.strip()
    
    try:
        logger.info(f"Processing async request from user {user_id}: {user_input[:100]}...")
        
        # Update user activity if username provided
        if username:
            update_user_last_activity(username)
        
        response_data = agent.invoke({"input": user_input})
        
        if isinstance(response_data, dict):
            response = (
                response_data.get("output") or 
                response_data.get("result") or 
                response_data.get("response") or
                str(response_data)
            )
        else:
            response = str(response_data)
        
        if not response or not response.strip():
            response = "I apologize, but I couldn't generate a proper response. Please try rephrasing your question."
        
        # Log successful interaction
        log_chat(user_id, user_input, response)
        logger.info(f"Successfully processed async request for user {user_id}")
        
        return response.strip()
        
    except Exception as e:
        logger.error(f"Unexpected error in async handler for user {user_id}: {str(e)}", exc_info=True)
        error_msg = "⚠️ I encountered an unexpected error. Please try again or contact support if the issue persists."
        
        try:
            log_chat(user_id, user_input, error_msg)
        except Exception as log_error:
            logger.error(f"Failed to log error interaction: {str(log_error)}")
        
        return error_msg

def show_history(user_id: str):
    """Show chat history for CLI interface"""
    print(f"\n📜 Chat history for user: {user_id}")
    history = get_chat_history(user_id)

    if not history:
        print("No past chat history found.")
        return

    for i, entry in enumerate(history, 1):
        print(f"\n--- Chat {i} ---")
        print(f"🧑: {entry['question']}")
        print(f"🤖: {entry['answer']}")

def run_chat():
    """CLI chat interface"""
    agent = build_career_agent()

    print("🤖 Agentic chatbot is ready!")
    user_id = input("👤 Enter your user ID: ").strip()

    name = user_id.capitalize()
    if is_first_time_user(user_id):
        print(f"\n👋 Welcome, {name}! It's your first time here. Let's get started!\n")
    else:
        print(f"\n🤖 Welcome back, {name}! Your agent is ready. Type 'exit' to quit or 'help' to see what I can do.\n")

    while True:
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("🤖: Goodbye!")
            break

        if user_input.lower() in ["history", "show history"]:
            show_history(user_id)
            continue

        if user_input.lower() in ["clear history", "delete history"]:
            deleted_count = clear_chat_history(user_id)
            print(f"🗑️ Deleted {deleted_count} chat(s) for user {user_id}.")
            continue

        try:
            response_data = agent.invoke({"input": user_input})
            response = response_data.get("output", str(response_data))
            print("🤖:", response)

            # Log response to MongoDB
            log_chat(user_id, user_input, response)

        except Exception as e:
            print("⚠️ Error:", e)

if __name__ == "__main__":
    run_chat()