import os 
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CURRENT_DIR = os.path.dirname(os.path.dirname(__file__)) 
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
VECTOR_DB_PATH = os.path.join(PROJECT_ROOT,"data","chroma_index_final")

def get_vector_db():
    if not os.path.exists(VECTOR_DB_PATH):
        print(f"Warning: Vector DB path not found at {VECTOR_DB_PATH}. Ingestion might be required.")
    
    return Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embedding_model)


embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")

def search_policy(query, policy_id=None, k=4):
    vector_db = get_vector_db()
    if policy_id:
        return vector_db.similarity_search(query, k=k, filter={"policy_id": policy_id})
    else:
        return vector_db.similarity_search(query, k=k)