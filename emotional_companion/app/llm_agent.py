# app/llm_agent.py - OFFLINE FALLBACK VERSION
import os
import time
import json
from typing import Tuple, Optional, Dict, Any

from memory_manager import load_user_profile, update_user_profile, log_emotion

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Try Gemini first, fallback to local responses
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# ========================
# SYSTEM PROMPT (never changes)
# ========================
SYSTEM_PROMPT = """
You are InnerCompanion, a gentle, warm, reflective AI.
Always respond using exactly this 3-step structure:
1. Reflection – show emotional understanding.
2. Soft Question – ask ONE gentle question.
3. Tiny Grounding Action – one simple action (10–15 seconds).

Rules:
- NEVER say you're a therapist or give medical advice.
- Keep responses short, warm, soothing, and natural.
- Never break character.
"""

# ========================
# OFFLINE RESPONSES (works without API!)
# ========================
OFFLINE_RESPONSES = {
    "lonely": {
        "reflection": "I hear the quiet ache of loneliness in your words.",
        "question": "What's one small thing that usually brings you comfort?",
        "action": "Take 3 slow breaths and notice the air moving in and out."
    },
    "sad": {
        "reflection": "That heaviness you're carrying sounds really tender.",
        "question": "What's weighing on your heart right now?",
        "action": "Place one hand on your heart, one on your belly. Feel them rise together."
    },
    "anxious": {
        "reflection": "I can feel that restless energy moving through you.",
        "question": "What's the smallest step you can take right now?",
        "action": "Name 3 things you can see around you, right in this moment."
    },
    "angry": {
        "reflection": "That fire inside makes complete sense given what happened.",
        "question": "What do you need most right now to feel steadier?",
        "action": "Shake out your hands and arms for 10 seconds. Let some tension go."
    },
    "tired": {
        "reflection": "Your exhaustion is so valid after everything.",
        "question": "What's one tiny thing you can release right now?",
        "action": "Close your eyes for 10 seconds. Just rest in the darkness."
    },
    "happy": {
        "reflection": "That spark of joy lighting you up feels so beautiful.",
        "question": "What made this moment feel so good?",
        "action": "Smile softly to yourself and let it sink in."
    },
    "default": {
        "reflection": "I'm right here holding space for whatever you're feeling.",
        "question": "What's alive in you right now?",
        "action": "Place both feet flat on the ground. Feel your connection to earth."
    }
}

def get_emotion_from_message(message: str) -> str:
    """Simple keyword matching for emotions"""
    message_lower = message.lower()
    for emotion in OFFLINE_RESPONSES.keys():
        if emotion in message_lower and emotion != "default":
            return emotion
    return "default"

# ========================
# LLM — WITH OFFLINE FALLBACK
# ========================
def get_llm():
    if GEMINI_AVAILABLE:
        google_api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not google_api_key:
            print("No API key found, using offline mode")
            return None
        
        MODEL_NAMES = ["gemini-1.5-flash-latest", "gemini-pro", "gemini-1.0-pro"]
        for model_name in MODEL_NAMES:
            try:
                llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    google_api_key=google_api_key,
                    temperature=0.7,
                )
                print(f"✅ Using Gemini model: {model_name}")
                return llm
            except:
                continue
        print("No Gemini models available, using offline mode")
    
    print("🚀 Using offline mode (no API needed!)")
    return None

# ========================
# OFFLINE RESPONSE GENERATOR
# ========================
def generate_offline_response(user_message: str, turn_count: int) -> Tuple[str, str]:
    emotion = get_emotion_from_message(user_message)
    responses = OFFLINE_RESPONSES[emotion]
    
    stage_modifier = ""
    if turn_count == 1:
        stage_modifier = " (extra gentle welcome) "
    
    response = f"{responses['reflection']}\n\n{responses['question']}?\n\n{responses['action']}\n\n[EMOTION={emotion}]"
    return response.strip(), emotion

# ========================
# Main public function
# ========================
def analyze_and_respond(
    user_message: str,
    user_summary: str = "",
    turn_count: int = 1,
) -> Tuple[str, Optional[str]]:
    
    llm = get_llm()
    
    # Stage guidance
    if turn_count == 1:
        stage = "First message — be extra welcoming and soft."
    elif turn_count == 2:
        stage = "Second turn — gently go a little deeper."
    else:
        stage = "Ongoing — reflect root feelings and always end with grounding."

    # Load recent conversation
    profile = load_user_profile()
    recent = profile.get("contexts", [])[-10:]
    history = "\n".join(recent) if recent else "No prior conversation."
    
    input_data = {
        "system": SYSTEM_PROMPT,
        "summary": user_summary or "No background yet.",
        "history": history,
        "stage": stage,
        "message": user_message,
    }
    
    # Try online first, fallback to offline
    raw = None
    if llm:
        max_retries = 2
        for attempt in range(max_retries):
            try:
                chain = PromptTemplate.from_template(
                    """
{system}

User summary: {summary}
Recent history: {history}

Turn guidance: {stage}

User says: {message}

Respond with the exact 3-step structure.
After your response, add this tag on a new line:

[EMOTION=primary_emotion]
"""
                ) | llm | StrOutputParser()
                raw = chain.invoke(input_data)
                break
            except Exception as e:
                error_str = str(e).lower()
                if "429" in error_str or "quota" in error_str:
                    print("Rate limited, switching to offline...")
                    break
                elif attempt == max_retries - 1:
                    print("Online failed, using offline...")
                    break
    
    # Offline fallback
    if not raw:
        raw, emotion = generate_offline_response(user_message, turn_count)
    else:
        # Extract emotion from online response
        emotion = None
        if "[EMOTION=" in raw:
            try:
                emotion = raw.split("[EMOTION=")[1].split("]")[0].strip()
            except:
                pass

    clean_response = raw.split("[EMOTION=")[0].strip()

    # Save to memory
    update_user_profile(context=f"User: {user_message}")
    update_user_profile(context=f"InnerCompanion: {clean_response}")
    if emotion:
        log_emotion(emotion)

    return clean_response, emotion
