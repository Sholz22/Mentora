from pymongo import MongoClient
from src.config import settings

client = MongoClient(settings.mongo_uri)
db = client[settings.user_profiles_collection]
profiles_col = db["user_profiles"]

def get_user_profile(username: str) -> dict:
    """Return current user profile dictionary for a given username."""
    profile = profiles_col.find_one({"username": username}, {"_id": 0, "username": 0})
    return profile or {}

def update_user_profile(username: str, key: str, value: str) -> bool:
    """Update or add a field in the user profile."""
    result = profiles_col.update_one(
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
