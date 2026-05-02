# Medical-Chatbot-with-LLM-Langchain-Pinecone-Flask-and-AWS
# Medical Chatbot 🏥

## About

This is a simple medical chatbot project I built using Python.
It can answer basic medical questions by using AI and some stored data.

I used Groq (LLaMA model) for generating answers and Pinecone to store and search data.

---

## What it does

* User asks a medical question
* Bot searches related info from stored data
* Then AI gives a short answer

---

## Tech Used

* Python
* Flask
* LangChain
* Pinecone
* Groq API
* HTML, CSS

---

## How to run

1. Clone the repo

```bash
git clone https://github.com/vineelkoushik/Medical-Chatbot-with-LLM-Langchain-Pinecone-Flask-and-AWS.git
cd Medical-Chatbot-with-LLM-Langchain-Pinecone-Flask-and-AWS
```

2. Install requirements

```bash
pip install -r requirements.txt
```

3. Create `.env` file and add keys

```
PINECONE_API_KEY=your_key
GROQ_API_KEY=your_key
```

4. Run the app

```bash
python app.py
```

---

## Example questions

* What is acne?
* What is diabetes?
* What is treatment for fever?

---

## Note

This project is only for learning purpose.
Don’t use it for real medical decisions.

---

## Author

Vineel Koushik
