# app/main.py
import streamlit as st
from dotenv import load_dotenv

# Local imports
from llm_agent import analyze_and_respond
from safety import detect_crisis, safety_response
from memory_manager import load_user_profile, update_user_profile, log_emotion

load_dotenv()

st.set_page_config(page_title="InnerCompanion", page_icon="🤍", layout="centered")

st.title("🤍 InnerCompanion")
st.markdown(
    """
    A gentle, warm, reflective companion.  
    Always here to listen, reflect, and offer tiny grounding steps.  
    *This is a prototype — never a replacement for professional support.*
    """
)

# -----------------------------------------
# Sidebar — Persistent Profile
# -----------------------------------------
with st.sidebar:
    st.header("Your Space (saved forever)")
    
    name = st.text_input("Name (optional)", placeholder="e.g. Alex")
    age = st.text_input("Age (optional)", placeholder="e.g. 24")
    context = st.text_area(
        "Anything you want me to remember",
        placeholder="e.g. exam stress, breakup, feeling lost...",
        height=120
    )
    
    if st.button("💾 Save gently", use_container_width=True):
        update_user_profile(name=name or None, age=age or None, context=context or None)
        st.success("Saved with care 🤍")

# Build user summary
user_profile = load_user_profile()
user_summary = ""
if user_profile.get("name"):
    user_summary += f"Name: {user_profile['name']}. "
if user_profile.get("age"):
    user_summary += f"Age: {user_profile['age']}. "
if user_profile.get("context"):
    user_summary += f"Background: {user_profile['context']}."

# Initialize conversation & turn count
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "turn_count" not in st.session_state:
    st.session_state.turn_count = 0

# -----------------------------------------
# Chat Interface
# -----------------------------------------
st.markdown("### I'm here. What's on your heart today?")

# The fix: use a regular variable + st.empty() placeholder for controlled clearing
user_input = st.text_area(
    "",
    placeholder="Share whatever feels true right now...",
    height=130,
    label_visibility="collapsed",
    key="user_input_widget"   # Streamlit manages this key internally
)

col1, col2 = st.columns([1, 6])
with col1:
    send = st.button("Send", use_container_width=True)

if send and user_input.strip():
    st.session_state.turn_count += 1
    message = user_input.strip()

    # Safety first
    if detect_crisis(message):
        response = safety_response()
        emotion = "crisis"
    else:
        response, emotion = analyze_and_respond(
            user_message=message,
            user_summary=user_summary or "First-time user.",
            turn_count=st.session_state.turn_count
        )

    if emotion and emotion != "crisis":
        log_emotion(emotion)

    # Append to history
    st.session_state.conversation.append(("You", message))
    st.session_state.conversation.append(("InnerCompanion", response))

    # Critical fix: rerun to clear the text_area (Streamlit's proper way)
    st.rerun()

# -----------------------------------------
# Display Conversation
# -----------------------------------------
if st.session_state.conversation:
    st.markdown("---")
    for speaker, text in st.session_state.conversation:
        if speaker == "You":
            st.markdown(f"**You:** {text}")
        else:
            st.markdown(f"**🤍 InnerCompanion:**\n{text}\n")

    # Auto-scroll to bottom
    st.markdown(
        "<script>window.parent.document.querySelector('.main').scrollTop = document.body.scrollHeight;</script>",
        unsafe_allow_html=True
    )