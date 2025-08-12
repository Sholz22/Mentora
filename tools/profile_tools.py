import streamlit as st
from langchain.tools import Tool
from memory.user_profile import update_user_profile, profile_to_text, get_user_profile

def get_active_username() -> str:
    return st.session_state.get("username", "guest")

def get_user_profile_fn(_: str = "") -> str:
    username = get_active_username()
    return profile_to_text(username)

get_user_profile_tool = Tool.from_function(
    func=get_user_profile_fn,
    name="GetUserProfile",
    description="Retrieves the user's current career profile."
)

def update_user_profile_fn(input_str: str) -> str:
    username = get_active_username()
    if "=" not in input_str:
        return "Invalid format. Use 'field=value'."
    key, value = input_str.split("=", 1)
    key, value = key.strip().lower(), value.strip()

    success = update_user_profile(username, key, value)
    if success:
        return f"✅ Updated {key} to '{value}'.\n\nCurrent profile:\n{profile_to_text(username)}"
    else:
        return "❌ Failed to update profile."

update_user_profile_tool = Tool.from_function(
    func=update_user_profile_fn,
    name="UpdateUserProfile",
    description="Updates the user's career profile. Input format: field=value"
)