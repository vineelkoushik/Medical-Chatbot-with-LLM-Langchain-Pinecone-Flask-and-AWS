from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("""
You are a medical assistant.

Use ONLY the context below to answer the question.
Remove any junk like page numbers, repeated headers, or random text.

If the answer is not present, say:
"I don't have enough medical data to answer this."

Context:
{context}

Question:
{input}

Answer:
""")