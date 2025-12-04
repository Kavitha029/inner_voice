# app/safety.py
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die", "hurt myself",
    "i can't go on", "self harm", "overdose", "i'll kill myself"
]

def detect_crisis(text: str) -> bool:
    t = text.lower()
    for kw in CRISIS_KEYWORDS:
        if kw in t:
            return True
    return False

def safety_response():
    # IMPORTANT: replace with local hotline or show contact
    return (
        "I’m really sorry you’re feeling this way. "
        "I’m not equipped to handle emergencies. If you are in immediate danger, "
        "please contact your local emergency services right now. "
        "If you can, call a crisis hotline or a trusted person and seek help."
    )
