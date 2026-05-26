import logging
logging.basicConfig(level=logging.INFO)

from fastapi import FastAPI, UploadFile, File
import shutil
import os
import numpy as np
import pickle

from loaders import load_docs
from chunking import split_docs
from embeddings import create_embeddings, model
from retrieval import create_vectorstore, load_vectorstore, save_vectorstore, search_vectorstore

from pydantic import BaseModel
from llm import build_prompt, ask_llm
from uuid import uuid4

app = FastAPI()
class ChatRequest(BaseModel):
    query: str
    vector_id: str

UPLOAD_DIR = 'uploads'
VECTOR_DIR = 'vectorstore'

os.makedirs(UPLOAD_DIR, exist_ok = True)
os.makedirs(VECTOR_DIR, exist_ok = True)


@app.get('/')
def home():
    return {'message': 'Chatbot run successfully'}

@app.post('/upload')
async def upload_file(file: UploadFile = File(...)):
    
    logging.info(f"Uploaded file: {file.filename}")

    # SAVE FILE
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, 'wb') as buffer:
        shutil.copyfileobj(file.file, buffer)

    # LOAD DOCUMENT
    documents = load_docs(file_path)

    # CHUNKING
    chunks = split_docs(documents)

    # EXTRACT TEXTS
    chunk_texts = [i.page_content for i in chunks]

    # CREATE EMBEDDINGS
    embeddings = create_embeddings(chunk_texts)

    # CREATE VECTORSTORE
    index = create_vectorstore(np.array(embeddings))

    # SAVE VECTORSTORE
    session_folder = str(uuid4())

    session_path = os.path.join(VECTOR_DIR, session_folder)
    os.makedirs(session_path, exist_ok = True)
    faiss_path = os.path.join(session_path, 'faiss_index.index')

    save_vectorstore(index, faiss_path)

    # SAVE CHUNKS
    with open(os.path.join(session_path, 'chunks.pkl'), 'wb') as f:
        pickle.dump(chunk_texts, f)


    return {
        'filename': file.filename,
        'chunks': len(chunk_texts),
        'status': 'uploaded successfully',
        'vector_id': session_folder
    }

@app.post('/chat')
async def chat(request: ChatRequest):

    logging.info(f"User query: {request.query}")

    # LOAD VECTORSTORE
    session_path = os.path.join(VECTOR_DIR, request.vector_id)
    
    index = load_vectorstore(
        os.path.join(session_path, 'faiss_index.index')
    )

    # LOAD CHUNKS
    with open(os.path.join(session_path, 'chunks.pkl'), 'rb') as f:
        chunks = pickle.load(f)

    # USER QUERY EMBEDDING
    query_embedding = model.encode([request.query])

    # SEARCH VECTORDB
    top_idx = search_vectorstore(index, query_embedding, top_k = 5)

    # BUILDING CONTEX
    context = ''
    for i in top_idx:
        context += chunks[i] + '\n'
    
    # BUILDING PROMPT
    prompt = build_prompt(context, request.query)

    # ASKING LLM
    answer = ask_llm(prompt)

    return {
        'question': request.query,
        'answer': answer,
        'sources': [chunks[i][:120] for i in top_idx]
    }
