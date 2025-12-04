# app/memory_manager.py

import json
import os
from datetime import datetime

MEMORY_FILE = "memory/user_memory.json"

# Ensure memory folder & file exist
def init_memory():
    if not os.path.exists("memory"):
        os.makedirs("memory")
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f)


# Load entire memory file
def load_full_memory():
    init_memory()
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


# Save entire memory file
def save_full_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)


# Get memory for a specific user_id
def load_user_profile(user_id="default_user"):
    data = load_full_memory()
    return data.get(user_id, {
        "name": "",
        "age": "",
        "contexts": [],
        "helpful_actions": [],
        "last_session_summary": "",
        "emotion_log": []
    })


# Save a user's profile
def save_user_profile(profile, user_id="default_user"):
    data = load_full_memory()
    data[user_id] = profile
    save_full_memory(data)


# Update profile fields
def update_user_profile(name=None, age=None, context=None, helpful_action=None):
    profile = load_user_profile()

    if name:
        profile["name"] = name
    if age:
        profile["age"] = age
    if context and context not in profile["contexts"]:
        profile["contexts"].append(context)
    if helpful_action and helpful_action not in profile["helpful_actions"]:
        profile["helpful_actions"].append(helpful_action)

    save_user_profile(profile)


# Add an emotion log entry
def log_emotion(emotion):
    profile = load_user_profile()
    profile["emotion_log"].append({
        "emotion": emotion,
        "time": datetime.now().isoformat()
    })
    save_user_profile(profile)
