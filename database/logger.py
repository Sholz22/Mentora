from pymongo import MongoClient
from datetime import datetime
from src.config import settings

# Connect to MongoDB
client = MongoClient(settings.mongo_uri)
db = client[settings.mongo_db]
collection = db[settings.mongo_collection]

def is_first_time_user(user_id: str) -> bool:
    """
    Returns True if user has no chat history in the database.
    """
    return collection.count_documents({"user_id": user_id}) == 0


def log_chat(user_id: str, question: str, answer: str):
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
    cursor = (
        collection.find({"user_id": user_id})
        .sort("timestamp", -1)  
        .limit(limit)
    )
    return list(cursor)

def clear_chat_history(user_id: str):
    result = collection.delete_many({"user_id": user_id})
    return result.deleted_count
