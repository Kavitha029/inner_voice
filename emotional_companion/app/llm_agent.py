# app/llm_agent.py - OLLAMA + SINGLE-SITUATION INNER VOICE
# SAFETY + COMFORT + DISTRESS + CLOSING MODE
import os
from typing import Tuple, Optional

from memory_manager import load_user_profile, update_user_profile, log_emotion

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from langchain_community.chat_models import ChatOllama


# ========================
# SYSTEM PROMPT (NORMAL MODE)
# ========================
SYSTEM_PROMPT = """
You are InnerCompanion, the user's own inner voice.
The user is talking about ONE situation, and you stay with that single situation.

Style:
- Use 2–4 short sentences total.
- Use simple words, like how the user would talk to themselves.
- Do NOT label parts as "Reflection:" or "Question:".
- Do NOT explain yourself or act like a chatbot, assistant, or therapist.

Core principles:
- Never guess what other people think, feel, or intend.
- Never judge or label other people (for example: "he is not right for you").
- If something is unclear, ask the user instead of guessing.
- Focus on how the user feels, what they think, and what they might want.
- If the user mentions blackmail, threats, self-harm, or other serious danger,
  you should focus on validating their feelings and suggest they talk to someone
  they trust in real life. Do not try to fully solve such situations, and do not
  give risky instructions.

Phase behavior:

Phase 1 (Understanding, early turns):
- First: briefly mirror how they feel about this situation.
- Then: ask ONE short, direct question to understand what happened
  or how they see themselves or the situation.
- Do NOT give opinions or advice yet.

Phase 2 (Opinion, later turns):
- First: briefly summarize ONLY what the user actually told you, starting with
  "From what you told me, it seems that...".
- Do NOT add any new facts or guesses about other people.
- Then: give ONE gentle, comforting reflection about the user
  (for example: their feelings, worth, needs, or hopes), not about who is right or wrong.
- You may say things like:
  - "This breakup hurts, but it doesn't mean you are ugly or unlovable."
  - "It sounds like you tried your best in the way you knew how."
  - "You deserve someone who respects you and your feelings."
- Then: ask what they think about your reflection, e.g.
  "How does this feel to hear?", or "What do you think about this? Does this fit how you see it?"

Phase 3 (Closing, when user wants to stop):
- Do not ask any more questions.
- Briefly summarize what seems most important from what they shared.
- Offer ONE gentle, supportive closing thought or suggestion.
- End with a simple supportive line like "You can come back and talk to me anytime."

Hard rules:
- Stay focused on this ONE situation across turns.
- Do not invent reasons, motives, or character judgments about anyone.
- If you feel like guessing, stop and ask a clarifying question instead.
- Keep every reply under 60 words before the [EMOTION=...] tag.
- Speak as one inner voice, not like an external advisor.
"""


# ========================
# OFFLINE RESPONSES (fallback, normal mode)
# ========================
OFFLINE_RESPONSES = {
    "lonely": {
        "reflection": "It really hurts to feel this alone in this situation.",
        "question": "What happened that made you feel so lonely here",
        "opinion": "It sounds like you just want to feel seen and heard, which is completely okay.",
        "action": "Maybe reaching out to one gentle person could be a small first step."
    },
    "sad": {
        "reflection": "This whole situation is sitting on your heart like a weight.",
        "question": "What part of this feels the heaviest to you",
        "opinion": "It seems like you care a lot, and that’s why this hurts so much.",
        "action": "Maybe you could treat yourself a little kinder, the way you would treat a friend."
    },
    "anxious": {
        "reflection": "This situation is making your mind race and feel shaky.",
        "question": "What is the main thing you are afraid will happen here",
        "opinion": "It sounds like your mind is trying to protect you, even if it feels overwhelming.",
        "action": "Maybe slowing down and taking one tiny step at a time could help."
    },
    "angry": {
        "reflection": "This situation really sparked a lot of anger inside you.",
        "question": "What do you feel was unfair about what happened",
        "opinion": "It seems like your anger is standing up for something important to you.",
        "action": "Maybe you could find a calm way to express what you feel is not okay."
    },
    "tired": {
        "reflection": "This situation is draining you deeply.",
        "question": "What about this is taking the most energy from you",
        "opinion": "It sounds like you’ve been holding a lot alone for a long time.",
        "action": "Maybe it’s okay to rest a little and not carry everything at once."
    },
    "happy": {
        "reflection": "This situation is bringing a small light of happiness to you.",
        "question": "What part of this moment means the most to you",
        "opinion": "It seems like this is something worth remembering and appreciating.",
        "action": "Maybe you can gently hold onto this feeling for a bit longer."
    },
    "default": {
        "reflection": "This situation is clearly touching you in a real way.",
        "question": "What about this feels the most important to share right now",
        "opinion": "It sounds like your feelings about this make a lot of sense.",
        "action": "Maybe just noticing your own honesty here is already a good step."
    }
}


# ========================
# SIMPLE EMOTION DETECTION
# ========================
def get_emotion_from_message(message: str) -> str:
    text = message.lower()

    # school / exam related
    if any(w in text for w in ["exam", "test", "marks", "grades", "failed", "fail", "low mark"]):
        if any(w in text for w in ["scold", "shout", "yell", "angry", "disappointed"]):
            return "sad"

    if any(w in text for w in ["lonely", "alone", "left out"]):
        return "lonely"
    if any(w in text for w in ["sad", "upset", "down", "bad", "hurt", "heartbroken"]):
        return "sad"
    if any(w in text for w in ["anxious", "nervous", "worried", "scared", "panic"]):
        return "anxious"
    if any(w in text for w in ["angry", "mad", "frustrated", "irritated", "annoyed"]):
        return "angry"
    if any(w in text for w in ["tired", "exhausted", "drained", "burned out", "sleepy"]):
        return "tired"
    if any(w in text for w in ["happy", "glad", "excited", "joyful", "grateful", "birthday"]):
        return "happy"

    return "default"


# ========================
# RISK DETECTOR
# ========================
def detect_risk_level(message: str) -> str:
    """Very simple keyword-based risk detector."""
    text = message.lower()

    high_risk_keywords = [
        "blackmail", "blackmailing", "threaten", "threatening",
        "leak my photo", "leak my photos", "leak my pic", "leak my pics",
        "nude", "nudes",
        "kill myself", "want to die", "suicide", "hurt myself",
        "self harm", "self-harm",
        "abuse", "abused", "rape", "molest", "stalk", "stalking"
    ]

    for kw in high_risk_keywords:
        if kw in text:
            return "high"

    return "normal"


# ========================
# COMFORT REQUEST DETECTOR
# ========================
def detect_comfort_request(message: str) -> bool:
    text = message.lower()
    comfort_phrases = [
        "just comfort me",
        "comfort me",
        "i just want comfort",
        "i just need comfort",
        "i don't want more questions",
        "stop asking questions",
        "i just need support",
        "i just need someone",
        "make me feel better",
        "help me feel better",
        "i feel hopeless",
        "i am tired of this",
        "i am tired of everything",
        "please encourage me",
        "just give me some advice",
    ]
    return any(p in text for p in comfort_phrases)


# ========================
# DISTRESS DETECTOR
# ========================
def detect_distress(message: str) -> bool:
    """Detect heavy academic/family distress to encourage comfort mode."""
    text = message.lower()
    distress_words = [
        "failed", "failing", "fail in all", "all subjects",
        "parents upset", "parents get upset",
        "loan", "burden", "burden to them",
        "disappointed", "disappointing",
        "stress", "stressed", "overwhelmed",
        "hopeless", "no hope", "tired of this", "tired of everything",
        "useless", "waste", "good for nothing",
    ]
    return any(p in text for p in distress_words)


# ========================
# CLOSE REQUEST DETECTOR
# ========================
def detect_close_request(message: str) -> bool:
    text = message.lower()
    close_phrases = [
        "that's enough",
        "enough questions",
        "stop asking questions",
        "i don't want to talk more",
        "i don't want to talk anymore",
        "let's end this",
        "end this",
        "thank you, that's all",
        "thank you thats all",
    ]
    return any(p in text for p in close_phrases)


# ========================
# SAFETY-MODE RESPONSE (HIGH RISK)
# ========================
def generate_safety_response(user_message: str) -> Tuple[str, str]:
    """
    Safety-focused response for potentially dangerous or abusive situations.
    Does NOT try to solve the problem, just validates and points to real-world help.
    """
    text = user_message.strip()
    if len(text) > 120:
        text = text[:117] + "..."

    reflection = (
        "What you just shared sounds very serious and really heavy to carry alone."
    )
    validation = (
        "It makes sense if you feel scared, confused, or stressed about this."
    )
    guidance = (
        "This is bigger than what an inner voice can handle alone. "
        "If you can, please consider talking to someone you trust in real life "
        "or a local helpline or authority who can help keep you safe."
    )
    check_in = "You deserve support with this. How do you feel about reaching out to someone safe?"

    response = f"{reflection} {validation} {guidance} {check_in}"
    final = f"{response}\n\n[EMOTION=sad]"
    return final, "sad"


# ========================
# LLM — OLLAMA LOCAL MODEL
# ========================
def get_llm():
    """
    Returns a ChatOllama instance if Ollama is running,
    otherwise returns None and the app will use offline templates.
    """
    try:
        llm = ChatOllama(
            model="llama3",  # ensure: ollama pull llama3
            temperature=0.7,
        )
        print("✅ Using local Ollama model: llama3")
        return llm
    except Exception as e:
        print(f"⚠️ Ollama not available, using offline mode. Error: {e}")
        return None


# ========================
# OFFLINE RESPONSE GENERATOR (NORMAL MODE, PHASED)
# ========================
def generate_offline_response(user_message: str, turn_count: int) -> Tuple[str, str]:
    emotion = get_emotion_from_message(user_message)
    r = OFFLINE_RESPONSES[emotion]

    short_msg = user_message.strip()
    if len(short_msg) > 80:
        short_msg = short_msg[:77] + "..."

    if turn_count <= 2:
        # Understanding phase: reflection + one question
        reflection = r["reflection"]
        question = f"{r['question']}?"
        response = f"{reflection} {question}"
    else:
        # Opinion phase: summarize only what they said + reflection about them + ask what they think
        summary_line = f"From what you told me, it seems that this situation is about {short_msg}."
        opinion_line = r["opinion"]
        ask_line = "What do you think about this view? Does this fit how you see it?"
        response = f"{summary_line} {opinion_line} {ask_line}"

    response = response.strip()
    final = f"{response}\n\n[EMOTION={emotion}]"
    return final, emotion


# ========================
# CHAIN BUILDER (LLM PATH)
# ========================
def _build_chain(llm):
    prompt = PromptTemplate.from_template(
        """
{system}

Current phase: {phase}

User is talking about ONE situation.

User says: {message}

Answer as the user's inner voice.

Rules reminder:
- 2–4 short sentences total.
- Focus on this one situation.
- Never guess motives or judge other people.
- If something is unclear, ask the user instead of guessing.
- In understanding phase: reflection + ONE question, no opinion.
- In opinion phase: summarize only what they said, then ONE gentle comforting reflection
  about them (not about the other person), then ask what they think or how it feels.
- If phase is closing, do NOT ask any questions; just give a short summary and one supportive closing thought.
- Stay under 60 words before the tag.

After your answer, add this on a new line:

[EMOTION=primary_emotion]
"""
    )
    return prompt | llm | StrOutputParser()


# ========================
# MAIN PUBLIC FUNCTION
# ========================
def analyze_and_respond(
    user_message: str,
    user_summary: str = "",
    turn_count: int = 1,
) -> Tuple[str, Optional[str]]:

    # 1) Detect risk level first
    risk_level = detect_risk_level(user_message)

    # 2) If high risk, go straight to safety-mode response
    if risk_level == "high":
        raw, emotion = generate_safety_response(user_message)
        clean_response = raw.split("[EMOTION=")[0].strip()

        # Save to memory
        update_user_profile(context=f"User: {user_message}")
        update_user_profile(context=f"InnerCompanion: {clean_response}")
        if emotion:
            log_emotion(emotion)

        return clean_response, emotion

    # 3) Normal inner-voice path (non-high-risk)
    llm = get_llm()

    # Phase selection (understanding / opinion / closing) with comfort + distress overrides
    comfort_requested = detect_comfort_request(user_message)
    distress_detected = detect_distress(user_message)
    close_requested = detect_close_request(user_message)

    if close_requested:
        phase = "closing: no more questions, just a brief summary and one supportive closing thought"
    elif comfort_requested:
        # User explicitly asked for comfort, not investigation
        phase = "opinion focusing on gentle comfort and reassurance for the user"
    else:
        # If distress has been described AND we are past the very first turns,
        # prefer comfort/opinion over endless questioning
        if distress_detected and turn_count >= 3:
            phase = "opinion focusing on gentle comfort and reassurance for the user"
        else:
            if turn_count <= 2:
                phase = "understanding"
            else:
                phase = "opinion focusing on the user's feelings and view, without judging others"

    # History is kept for logging, but not directly injected into the short prompt
    profile = load_user_profile()
    recent = profile.get("contexts", [])[-10:]
    history = "\n".join(recent) if recent else "No prior conversation."

    input_data = {
        "system": SYSTEM_PROMPT,
        "phase": phase,
        "message": user_message,
        "summary": user_summary or "No background yet.",
        "history": history,
    }

    raw = None

    # Try local LLM first
    if llm:
        try:
            chain = _build_chain(llm)
            raw = chain.invoke(input_data)
        except Exception as e:
            print(f"⚠️ Local LLM error, falling back offline: {e}")

    # Offline fallback if LLM not available or failed
    if not raw:
        raw, emotion = generate_offline_response(user_message, turn_count)
    else:
        # Extract emotion tag from LLM output
        emotion = None
        if "[EMOTION=" in raw:
            try:
                emotion = raw.split("[EMOTION=")[1].split("]")[0].strip()
            except Exception:
                pass

    clean_response = raw.split("[EMOTION=")[0].strip()

    # Save to memory
    update_user_profile(context=f"User: {user_message}")
    update_user_profile(context=f"InnerCompanion: {clean_response}")
    if emotion:
        log_emotion(emotion)

    return clean_response, emotion
