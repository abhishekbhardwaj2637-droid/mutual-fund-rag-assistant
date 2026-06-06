import os
import json
from dotenv import load_dotenv
import chromadb
from chromadb import EmbeddingFunction, Documents, Embeddings
from sentence_transformers import SentenceTransformer

# Load environment variables
load_dotenv()

# Vector DB configuration
VECTOR_DB_DIR = os.getenv("VECTOR_DB_DIR", os.path.join("data", "vectordb"))
DATA_PROCESSED_DIR = os.getenv("DATA_PROCESSED_DIR", os.path.join("data", "processed"))

class BGEEmbeddingFunction(EmbeddingFunction):
    """
    Custom embedding function for ChromaDB wrapping BAAI/bge-small-en-v1.5 model locally.
    """
    def __init__(self, model_name="BAAI/bge-small-en-v1.5"):
        print(f"Loading local SentenceTransformer model '{model_name}'...")
        # Will download the model locally on first instantiation
        self.model = SentenceTransformer(model_name)
        print("Model loaded successfully.")

    def __call__(self, input: Documents) -> Embeddings:
        # Encode documents directly (without query search prefix)
        embeddings = self.model.encode(list(input), normalize_embeddings=True)
        return embeddings.tolist()

def get_chroma_client():
    if not os.path.exists(VECTOR_DB_DIR):
        os.makedirs(VECTOR_DB_DIR)
    return chromadb.PersistentClient(path=VECTOR_DB_DIR)

def load_processed_data_to_db():
    client = get_chroma_client()
    embedding_fn = BGEEmbeddingFunction()
    
    # Get or create the collection
    collection = client.get_or_create_collection(
        name="mutual_funds",
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"} # Use cosine similarity
    )
    
    # Read processed files
    if not os.path.exists(DATA_PROCESSED_DIR):
        print(f"Processed directory '{DATA_PROCESSED_DIR}' does not exist. Run parser first.")
        return
        
    processed_files = [f for f in os.listdir(DATA_PROCESSED_DIR) if f.endswith("_processed.json")]
    if not processed_files:
        print("No processed JSON files found in processed folder.")
        return
        
    ids = []
    documents = []
    metadatas = []
    
    for file_name in processed_files:
        file_path = os.path.join(DATA_PROCESSED_DIR, file_name)
        slug = file_name.replace("_processed.json", "")
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        meta = data.get("metadata", {})
        source_url = meta.get("source_url", "N/A")
        fetched_at = meta.get("fetched_at", "N/A")
        
        # Loop through each section key
        for key, val in data.items():
            if key == "metadata" or not val.strip():
                continue
                
            chunk_id = f"{slug}_{key}"
            ids.append(chunk_id)
            documents.append(val)
            metadatas.append({
                "scheme_slug": slug,
                "section": key,
                "source_url": source_url,
                "last_updated": fetched_at
            })
            
    if ids:
        print(f"Upserting {len(ids)} document chunks into ChromaDB...")
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        print("ChromaDB update complete.")
    else:
        print("No document chunks prepared for ingestion.")

if __name__ == "__main__":
    load_processed_data_to_db()
