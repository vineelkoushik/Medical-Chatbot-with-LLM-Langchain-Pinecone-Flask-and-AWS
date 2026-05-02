from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import random
from datetime import datetime

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq

app = Flask(__name__)

# ---------------- ENV ---------------- #
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("medical-chatbot")

# ---------------- EMBEDDINGS ---------------- #
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = PineconeVectorStore(
    index=index,
    embedding=embeddings
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# ---------------- LLM ---------------- #
llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model_name="llama-3.1-8b-instant"
)

# ---------------- GREETING ---------------- #
def greet():
    hour = datetime.now().hour

    morning = [
        "🌅 Good morning! How can I help you medically today?",
        "🌞 Good morning! Ask your health question.",
        "🌤️ Morning! I’m here for your medical doubts."
    ]

    afternoon = [
        "☀️ Good afternoon! What do you need help with?",
        "👨‍⚕️ Afternoon! Ask your medical question.",
        "🏥 Good afternoon! I’m ready to assist you."
    ]

    evening = [
        "🌙 Good evening! How can I help you medically?",
        "🌆 Evening! Ask your health concern.",
        "🩺 Good evening! I’m here to help."
    ]

    if hour < 12:
        return random.choice(morning)
    elif hour < 18:
        return random.choice(afternoon)
    else:
        return random.choice(evening)

# ---------------- THANK YOU SYSTEM ---------------- #
def is_thanks(msg):
    q = msg.lower()
    return any(x in q for x in [
        "thanks", "thank you", "thankyou", "thx", "tnx", "thank u", "ty"
    ])

def thanks():
    return random.choice([
        "You're welcome 😊",
        "Happy to help 🏥",
        "Anytime 🙏",
        "Stay healthy 💙",
        "Glad I could help 😊",
        "Take care of your health 🩺",
        "Always here for you 🏥",
        "Wishing you good health 💊",
        "Feel free to ask again 😊",
        "You're welcome! Stay safe 💙"
    ])

# ---------------- SPECIALTY ---------------- #
def get_specialty(q):
    q = q.lower()

    if any(x in q for x in ["eye", "vision", "blur"]):
        return "ophthalmology"
    if any(x in q for x in ["skin", "acne", "rash"]):
        return "dermatology"
    if any(x in q for x in ["heart", "chest"]):
        return "cardiology"
    return "general_medicine"

# ---------------- RISK ---------------- #
def get_risk(q):
    q = q.lower()

    if any(x in q for x in ["stroke", "heart attack"]):
        return "HIGH"
    if any(x in q for x in ["chest pain", "fever"]):
        return "MEDIUM"
    return "LOW"

# ---------------- MODE DECIDER (FIXED) ---------------- #
def decide_mode(query):
    q = query.lower().strip()
    words = q.split()

    if len(words) == 1:
        return "full"

    if any(x in q for x in [
        "what is", "define", "meaning", "explain", "definition"
    ]):
        return "definition"

    if any(x in q for x in [
        "treatment", "cure", "therapy", "medicine",
        "drug", "how to treat", "manage", "management"
    ]):
        return "treatment"

    if any(x in q for x in [
        "cause", "why", "reason", "etiology"
    ]):
        return "cause"

    return "full"

# ---------------- PROMPT ENGINE (FIXED STRICT VERSION) ---------------- #
def build_prompt(context, question, specialty, risk, mode):

    if mode == "definition":
        return f"""
You are a medical assistant.

RULES:
- Only 2–3 line definition
- No treatment or diagnosis

Context:
{context}

Question:
{question}

Answer:
"""

    elif mode == "treatment":
        return f"""
You are a hospital medical assistant.

RULES:
- ONLY treatment
- NO symptoms or causes

FORMAT:

💊 Treatment:
👨‍⚕️ Specialist:
🔗 Related Conditions (keywords only):

Context:
{context}

Question:
{question}

Answer:
"""

    elif mode == "cause":
        return f"""
You are a medical assistant.

RULES:
- ONLY causes
- No treatment

Format:

🧾 Causes:
👨‍⚕️ Specialist:

Context:
{context}

Question:
{question}

Answer:
"""

    else:
        return f"""
You are a strict hospital medical assistant.

RULES:
- Only relevant medical response
- No unnecessary expansion

Format:

🧠 Condition Summary:
⚠️ Symptoms:
🧾 Causes:
💊 Treatment:
👨‍⚕️ Specialist:
📊 Risk Level: {risk}

Context:
{context}

Question:
{question}

Answer:
"""

# ---------------- CORE ENGINE ---------------- #
def get_response(msg):

    docs = retriever.invoke(msg)

    if not docs:
        return "No medical information found."

    context = "\n\n".join([d.page_content for d in docs[:3]])

    specialty = get_specialty(msg)
    risk = get_risk(msg)
    mode = decide_mode(msg)

    prompt = build_prompt(context, msg, specialty, risk, mode)

    response = llm.invoke(prompt)

    return response.content

# ---------------- ROUTES ---------------- #
@app.route("/")
def home():
    return render_template("chat.html")

@app.route("/get", methods=["POST"])
def chat():
    msg = request.form.get("msg")

    if not msg:
        return "Empty message"

    m = msg.lower().strip()

    # greetings
    if m in ["hi", "hello", "hey"]:
        return greet()

    # thank you
    if is_thanks(m):
        return thanks()

    return get_response(msg)

# ---------------- RUN ---------------- #
if __name__ == "__main__":
    app.run(debug=True)