from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from datetime import datetime
import hashlib
import streamlit as st
from src.config import settings

# Connect to MongoDB
try:
    client = MongoClient(settings.mongo_uri)
    db = client[settings.mongo_db]
    
    # Collections
    collection = db[settings.mongo_collection]  # Original chat logs
    users_collection = db[settings.users_collection]  # User accounts
    chat_history_collection = db[settings.chat_history_collection]  # Streamlit chat history
    
    # Test connection
    client.admin.command('ping')
    
    # Create indexes for users collection
    users_collection.create_index("username", unique=True)
    users_collection.create_index("email", unique=True)
    
    # Create index for chat history
    chat_history_collection.create_index([("username", 1), ("timestamp", 1)])
    
except Exception as e:
    st.error(f"MongoDB connection failed: {e}")
    client = None

def is_first_time_user(user_id: str) -> bool:
    """
    Returns True if user has no chat history in the database.
    """
    if not client:
        return True
    return collection.count_documents({"user_id": user_id}) == 0

def log_chat(user_id: str, question: str, answer: str):
    """Log chat interaction (original function)"""
    if not client:
        return
    
    doc = {
        "user_id": user_id,
        "timestamp": datetime.now(),
        "question": question,
        "answer": answer
    }
    collection.insert_one(doc)

def get_chat_history(user_id: str, limit: int = 10):
    """
    Returns the last `limit` chat entries for the given user, sorted from newest to oldest.
    """
    if not client:
        return []
    
    cursor = (
        collection.find({"user_id": user_id})
        .sort("timestamp", -1)  
        .limit(limit)
    )
    return list(cursor)

def clear_chat_history(user_id: str):
    """Clear chat history for a user"""
    if not client:
        return 0
    
    result = collection.delete_many({"user_id": user_id})
    return result.deleted_count

# NEW USER AUTHENTICATION FUNCTIONS

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """Create a new user"""
    if not client:
        return False, "Database connection failed!"
    
    try:
        password_hash = hash_password(password)
        user_doc = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "created_at": datetime.now(),
            "last_login": None
        }
        
        users_collection.insert_one(user_doc)
        return True, "Account created successfully!"
        
    except DuplicateKeyError as e:
        if "username" in str(e):
            return False, "Username already exists!"
        elif "email" in str(e):
            return False, "Email already exists!"
        else:
            return False, "Account with this information already exists!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user login"""
    if not client:
        return False
    
    try:
        password_hash = hash_password(password)
        user = users_collection.find_one({
            "username": username,
            "password_hash": password_hash
        })
        
        if user:
            # Update last login
            users_collection.update_one(
                {"username": username},
                {"$set": {"last_login": datetime.now()}}
            )
            return True
        else:
            return False
            
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return False

def save_streamlit_chat_history(username: str, chat_history: list) -> bool:
    """Save Streamlit chat history to MongoDB"""
    if not client:
        return False
    
    try:
        # Clear existing history for this user
        chat_history_collection.delete_many({"username": username})
        
        # Save new history
        if chat_history:
            chat_docs = []
            for speaker, message in chat_history:
                chat_docs.append({
                    "username": username,
                    "speaker": speaker,
                    "message": message,
                    "timestamp": datetime.now()
                })
            
            chat_history_collection.insert_many(chat_docs)
        
        return True
        
    except Exception as e:
        st.error(f"Error saving chat history: {e}")
        return False

def load_streamlit_chat_history(username: str) -> list:
    """Load Streamlit chat history from MongoDB"""
    if not client:
        return []
    
    try:
        # Get chat history ordered by timestamp
        chat_docs = chat_history_collection.find(
            {"username": username}
        ).sort("timestamp", 1)
        
        results = [(doc["speaker"], doc["message"]) for doc in chat_docs]
        return results if results else []
        
    except Exception as e:
        st.error(f"Error loading chat history: {e}")
        return []

def get_user_info(username: str) -> dict:
    """Get user information"""
    if not client:
        return {}
    
    try:
        user = users_collection.find_one(
            {"username": username}, 
            {"password_hash": 0}  # Exclude password hash
        )
        return user if user else {}
    except Exception as e:
        st.error(f"Error getting user info: {e}")
        return {}

def update_user_last_activity(username: str):
    """Update user's last activity timestamp"""
    if not client:
        return
    
    try:
        users_collection.update_one(
            {"username": username},
            {"$set": {"last_activity": datetime.now()}}
        )
    except Exception as e:
        pass  # Silent fail for this non-critical operation

    # Profiles collection
profiles_collection = db["user_profiles_collection"]
profiles_collection.create_index("username", unique=True)

def get_user_profile(username: str) -> dict:
    """Return current user profile dictionary."""
    profile_doc = profiles_collection.find_one({"username": username}, {"_id": 0, "username": 0})
    return profile_doc or {}

def update_user_profile(username: str, key: str, value: str) -> bool:
    """Update or add a field in the user profile."""
    result = profiles_collection.update_one(
        {"username": username},
        {"$set": {key: value}},
        upsert=True
    )
    return result.acknowledged

def profile_to_text(username: str) -> str:
    """Convert the profile dict to a text block for prompts."""
    profile = get_user_profile(username)
    if not profile:
        return "No profile information collected yet."
    return "\n".join([f"{k.capitalize()}: {v}" for k, v in profile.items()])
