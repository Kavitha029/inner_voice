Project Title:MENTAL WELLNESS IDEATION – InnerCompanion

Project Overview:
InnerCompanion is a supportive mental wellness assistant designed to help users navigate emotional stress such as exam pressure, loneliness, relationship issues, family expectations, and self-doubt. It speaks like a gentle, caring inner voice rather than a formal chatbot, guiding users through reflection, simple grounding suggestions, and self-understanding.
This project was developed as part of the MENTAL WELLNESS IDEATION academic initiative to explore how local large language models, combined with custom dialogue logic, can support emotional wellbeing in a safe and responsible way.

InnerCompanion focuses on:
Short, human-like replies that feel like your own thoughts
Understanding the user’s situation over multiple turns
Offering gentle, friend-like reflections and tiny suggestions
Being cautious and safety-aware in sensitive or high‑risk situations

Key Features:
Inner-voice conversation style
2–4 short sentences per reply
Simple, everyday language
No formal “AI assistant” tone; feels like talking to your own mind

Three-phase conversation flow:
Understanding phase: Reflects what the user feels and asks one focused question to understand the situation
Opinion / Comfort phase: Summarizes what the user shared, offers one gentle, positive reflection about the user (worth, needs, hopes), then asks how it feels or what they think
Closing phase: When the user wants to stop, avoids more questions and gives a short, supportive closing message

Emotion-aware responses:
Lightweight emotion detection (e.g., lonely, sad, anxious, angry, tired, happy)
Adapts reflection and questions to match the user’s emotional tone

Comfort & distress handling:
Detects explicit comfort requests such as “just comfort me”, “help me feel better”, “stop asking questions”
Detects distress patterns like exam failure, parents being upset, loans, burden or hopelessness
Shifts from continuous questioning to reassuring, encouraging responses

Safety mode for high‑risk cases:
Identifies phrases related to blackmail, threats, self-harm, abuse, or other danger
Switches to a safety-focused response that:
      Acknowledges seriousness
      Validates the user’s feelings
      Encourages reaching out to trusted people or local helplines/authorities
Avoids risky instructions or pretending to “fix” dangerous situations

Local LLM integration:
Uses a locally hosted model (e.g., via Ollama and llama3)
No external cloud API is required at runtime
More control over privacy and latency

Lightweight memory:
Stores recent user–bot messages for short-term context
Logs detected emotions for basic emotional trend tracking within a session.

System Architecture
Frontend:
    Chat-style UI with user input box and scrollable conversation view
Backend Logic (InnerCompanion engine):
    Phase manager: understanding, opinion/comfort, closing
    Emotion detector: maps text to simple emotional categories
    Risk detector: checks messages for self-harm, blackmail, threats, abuse keywords
    Comfort/distress detector: identifies when the user needs reassurance instead of continued questioning
    Offline fallback responses for when the local model is not available
Model Layer:
    Local LLM served through Ollama (e.g., llama3)
    Prompt design carefully constrains length, style, and safety behavior
Data / Storage:
    Minimal profile and context storage in local files (recent message history, emotion log)
    No long-term sensitive data is required for basic usage
Getting Started:
Prerequisites:
    Update this section according to your actual stack. For this project, you are using:
    Python 3.8+
    Streamlit
    LangChain
    Ollama installed and configured locally
    llama3 (or your chosen model) pulled in Ollama
    Dependencies listed in requirements.txt
Installation & Setup:
Adjust paths and commands to match your repository.

STEP 1:Clone the repository: 
git clone <https://github.com/Kavitha029/inner_voice>
cd <https://github.com/Kavitha029/inner_voice>
STEP 2:Install backend dependencies:
pip install -r requirements.txt
STEP 3:Set up the local model with Ollama
ollama pull llama3
ollama serve
STEP 4:Run the application
streamlit run app.py
Stores recent user–bot messages for short-term context
Logs detected emotions for basic emotional trend tracking within a session

Usage
Once the application is running:
    Open the Streamlit app in your browser (typically shown in the terminal, for example Local URL: <http://localhost:8502>
  Network URL: <http://192.168.31.31:8502>).
    (Optional) Enter basic information like your name or mood if your UI supports it.
    Type how you are feeling or what you are going through in the input box.
    Read the short responses, reflect, and continue the conversation at your own pace.
The assistant will:
    Start by reflecting your feelings and asking simple, focused questions
    Move into comfort mode when you express distress or explicitly request comfort
    Switch to safety mode if you mention dangerous or abusive situations
    Allow you to end gently with closing statements like “that’s enough” or “I don’t want to talk anymore”
    
Example Interaction Scenarios
1. Feeling Lonely
User: “I am feeling really lonely right now.”
User: “No one is talking to me these days.”

InnerCompanion reflects the loneliness and asks a soft question about what happened or how this feels for you.
3. Exams, Parents, and Loan Pressure
User: “I failed in almost all my subjects.”
User: “My parents are very upset with me.”
User: “They took a loan for my fees and I still failed.”
User: “I feel like a burden to them now.”
User: “I don’t know what to do, I just want some comfort.”

Here the system detects distress and comfort requests. It moves away from repeated questioning and offers a brief summary plus a gentle, hopeful reflection about your worth and future.
3. Breakup and Self‑Worth
User: “My boyfriend broke up with me.”
User: “He said I look ugly and wants someone better.”
User: “Just comfort me, I don’t want to talk about him.”

InnerCompanion avoids judging the other person and instead focuses on how much it hurts and how this does not define your value.
4. Sensitive / High‑Risk Situation
User: “My ex is blackmailing me with my photos and I’m scared.”
High‑risk safety mode is triggered. The assistant acknowledges the seriousness, validates fear, and gently suggests reaching out to trusted people or official support, without giving risky instructions.

5. Closing the Conversation
User: “That’s enough, I don’t want to talk anymore.”
InnerCompanion briefly summarizes what seems most important, offers one supportive closing thought, and stops asking questions.

Contributing:
If teammates or other contributors want to extend the project:
    Fork the repository on GitHub
    Create a new feature branch:

STEP 1:
git checkout -b feature/add-new-enhancement
Make your changes and commit:
STEP 2:
git commit -m "Add: new enhancement to InnerCompanion"
Push to your fork:
STEP 3:
git push origin feature/add-new-enhancement
Open a Pull Request to the main repository with a clear description of your changes.

Contact:
For questions, feedback, or collaboration:
Team Name: MENTAL WELLNESS IDEATION – InnerCompanion Team
Team Members :
Member 1: KAVITHA A
Member 2: MITHRA M
Member 3: MONICASHREE R
Email: <kavitha13112005@gmail.com>
Project Repository: <https://github.com/Kavitha029/inner_voice>

Acknowledgements:
We would like to express our sincere gratitude to:
    **Ollama, Streamlit, LangChain and LLM Communities – For tools, libraries, and documentation that enabled the technical foundation of this project.
    **Teammates & Testers – For continuous collaboration, testing different emotional scenarios, and refining the conversational flow and safety logic.
    **Mental Health Research & Practices – Ideas like reflective listening, grounding techniques, and self-awareness frameworks inspired the design and behavior of InnerCompanion.
    **InnerCompanion is created as a learning project, with responsibility and care, aiming to offer gentle emotional support, self-reflection, and a sense of being heard to users who need a quiet inner space to talk.
