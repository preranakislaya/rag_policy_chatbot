import faiss
import numpy as np
import pickle

def create_vectorstore(embeddings):
    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))

    return index

def save_vectorstore(index, path):
    faiss.write_index(index, path)

def load_vectorstore(path):
    return faiss.read_index(path)

# UPDATE-1
def search_vectorstore(index, query_embedding, top_k = 5):
    D, I = index.search(
        np.array(query_embedding).astype('float32'), top_k
        )
    return I[0]




