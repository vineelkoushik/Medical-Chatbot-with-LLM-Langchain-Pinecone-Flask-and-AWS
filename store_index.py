from dotenv import load_dotenv
import os
import json

from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

from src.helper import (
    load_pdf_file,
    filter_to_minimal_docs,
    text_split,
    download_hugging_face_embeddings
)

# ---------------- LOAD ENV ---------------- #
load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "medical-chatbot"

# ---------------- LOAD PDF DATA ---------------- #
print("📄 Loading PDFs...")
pdf_docs = load_pdf_file("data/")
pdf_docs = filter_to_minimal_docs(pdf_docs)
pdf_chunks = text_split(pdf_docs)

# ---------------- LOAD WIKIPEDIA DATA ---------------- #
print("🌍 Loading Wikipedia dataset...")

wiki_chunks = []

if os.path.exists("medical_1000_dataset.json"):
    with open("medical_1000_dataset.json", "r", encoding="utf-8") as f:
        wiki_data = json.load(f)

    for item in wiki_data:
        wiki_chunks.append(item["content"])
else:
    print("⚠️ Wikipedia dataset not found!")

# ---------------- CONVERT EVERYTHING TO TEXT ---------------- #
all_texts = []

# PDF chunks (Document objects → text)
for doc in pdf_chunks:
    all_texts.append(doc.page_content)

# Wikipedia chunks (already text)
for text in wiki_chunks:
    all_texts.append(text)

print(f"📊 Total chunks ready: {len(all_texts)}")

# ---------------- EMBEDDINGS ---------------- #
print("🧠 Loading embeddings...")
embeddings = download_hugging_face_embeddings()

# ---------------- CREATE INDEX IF NOT EXISTS ---------------- #
existing_indexes = pc.list_indexes().names()

if index_name not in existing_indexes:
    print("🚀 Creating index...")
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
else:
    print("✅ Index already exists")

# ---------------- CONNECT TO INDEX ---------------- #
index = pc.Index(index_name)

vectorstore = PineconeVectorStore(
    index=index,
    embedding=embeddings
)

# ---------------- UPLOAD DATA ---------------- #
print("📦 Uploading medical knowledge to Pinecone...")

vectorstore.add_texts(
    texts=all_texts,
    metadatas=[{"source": "pdf"} for _ in pdf_chunks] +
               [{"source": "wikipedia"} for _ in wiki_chunks]
)

print("✅ Upload complete (PDF + Wikipedia merged successfully)!")