import os
from django.shortcuts import render
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from django.conf import settings
from groq import Groq

# Constants
UPLOADS_FOLDER = os.path.join(settings.BASE_DIR, 'uploads')
CHUNK_SIZE = 2048
OVERLAP = 512

# Ensure uploads folder exists
os.makedirs(UPLOADS_FOLDER, exist_ok=True)

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
embedding_size = embedding_model.get_sentence_embedding_dimension()
faiss_index = faiss.IndexFlatL2(embedding_size)
chunks = []
embeddings_added = False
chat_history = []

# Load the Groq client
GROQ_API_KEY = "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"  # Replace with your actual Groq API key
client = Groq(api_key=GROQ_API_KEY)


# Function to load documents
def load_documents():
    documents = []
    files = os.listdir(UPLOADS_FOLDER)
    for file_name in files:
        file_path = os.path.join(UPLOADS_FOLDER, file_name)
        if file_name.endswith('.pdf'):
            try:
                reader = PdfReader(file_path)
                text = "".join(page.extract_text() for page in reader.pages if page.extract_text())
                documents.append(text)
            except Exception as e:
                print(f"Error reading PDF {file_name}: {e}")
        elif file_name.endswith('.txt'):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    documents.append(text)
            except Exception as e:
                print(f"Error reading TXT {file_name}: {e}")
    return documents


# Function to chunk documents
def process_and_chunk_documents():
    documents = load_documents()
    doc_chunks = []
    for doc in documents:
        for i in range(0, len(doc), CHUNK_SIZE - OVERLAP):
            doc_chunks.append(doc[i:i + CHUNK_SIZE])
    return doc_chunks


# Function to add chunks to FAISS index
def add_chunks_to_faiss_index(chunks):
    embeddings = embedding_model.encode(chunks, convert_to_numpy=True).astype('float32')
    faiss_index.add(embeddings)
    return True


# Initialize FAISS index if not already initialized
if not embeddings_added:
    chunks = process_and_chunk_documents()
    embeddings_added = add_chunks_to_faiss_index(chunks)


# Chatbot interface
def chat_page(request):
    global chat_history, chunks

    if request.method == "POST":
        user_prompt = request.POST.get("user_prompt")
        assistant_response = ""

        if user_prompt:
            # Check if embeddings are added and chunks exist
            if not embeddings_added or not chunks:
                assistant_response = "No documents are available for answering questions."
            else:
                try:
                    # Retrieve relevant chunks using FAISS
                    query_embedding = embedding_model.encode([user_prompt], convert_to_numpy=True).astype('float32')
                    distances, indices = faiss_index.search(query_embedding, k=5)
                    retrieved_chunks = [chunks[idx] for idx in indices[0] if 0 <= idx < len(chunks)]
                    context_text = "\n\n".join(retrieved_chunks)

                    # Query Llama model
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "system", "content": f"Relevant excerpts from documents:\n{context_text}"},
                            {"role": "user", "content": user_prompt}
                        ]
                    )
                    assistant_response = response.choices[0].message.content

                except Exception as e:
                    assistant_response = f"Error: {str(e)}"

            # Update chat history
            chat_history.append({"role": "user", "content": user_prompt})
            chat_history.append({"role": "assistant", "content": assistant_response})

    return render(request, "chat_app/chat.html", {"chat_history": chat_history})
