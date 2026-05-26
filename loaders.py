import pandas as pd
import os
from langchain_community.document_loaders import (PyPDFLoader, CSVLoader, Docx2txtLoader)

def load_docs(file_path):
    file = os.path.splitext(file_path)[1].lower()

    if file == '.pdf':
        loader = PyPDFLoader(file_path)
        docs = loader.load()
    elif file == '.docx':
        loader = Docx2txtLoader(file_path)
        docs = loader.load()
    elif file == '.csv':
        loader = CSVLoader(file_path)
        docs = loader.load()
    elif file == '.xlsx':
        df = pd.read_excel(file_path)
        docs = [{'page_content': df.to_string(), 'metadata': {'source': file_path}}]

    else:
        raise ValueError("Unsupported file format")
    
    return docs
