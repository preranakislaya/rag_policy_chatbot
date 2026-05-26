from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BAAI/bge-small-en-v1.5')

def create_embeddings(texts):
    embeddings = model.encode(texts)
    return embeddings