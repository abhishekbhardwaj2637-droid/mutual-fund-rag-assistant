import os
import re
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Map query keywords to scheme slugs
SCHEME_MAPPING = {
    "silver": "hdfc-silver-etf-fof-direct-growth",
    "small": "hdfc-small-cap-fund-direct-growth",
    "defence": "hdfc-defence-fund-direct-growth",
    "defense": "hdfc-defence-fund-direct-growth",
    "gold": "hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "mid": "hdfc-mid-cap-fund-direct-growth"
}

def detect_scheme_slug(query: str) -> str:
    """
    Scans the query to identify if it references a specific mutual fund scheme.
    Returns the slug if found, else None.
    """
    query_lower = query.lower()
    for keyword, slug in SCHEME_MAPPING.items():
        if keyword in query_lower:
            logger.info(f"Detected keyword '{keyword}' in query. Filtering to scheme: {slug}")
            return slug
    return None

_embedding_fn = None

def retrieve_context(query: str, k: int = 3) -> list[dict]:
    """
    Queries ChromaDB and returns the top-k matches.
    If a specific scheme is mentioned in the query, applies metadata filtering.
    """
    global _embedding_fn
    from ingestion.vector_store import get_chroma_client, BGEEmbeddingFunction
    
    client = get_chroma_client()
    if _embedding_fn is None:
        _embedding_fn = BGEEmbeddingFunction()
    embedding_fn = _embedding_fn
    
    # Get the collection
    collection = client.get_or_create_collection(
        name="mutual_funds",
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"}
    )
    
    # Detect if we need to filter by a specific scheme
    slug_filter = detect_scheme_slug(query)
    metadata_filter = None
    if slug_filter:
        metadata_filter = {"scheme_slug": slug_filter}
        logger.info(f"Applying metadata filter: {metadata_filter}")
    else:
        logger.info("No scheme keyword detected in query. Searching globally across all schemes.")
        
    try:
        results = collection.query(
            query_texts=[query],
            n_results=k,
            where=metadata_filter
        )
    except Exception as e:
        logger.error(f"Error querying ChromaDB: {e}", exc_info=True)
        return []
        
    chunks = []
    if not results or not results.get("documents") or not results["documents"][0]:
        return chunks
        
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0] if "distances" in results else [0.0] * len(documents)
    ids = results["ids"][0]
    
    for i in range(len(documents)):
        chunks.append({
            "id": ids[i],
            "text": documents[i],
            "metadata": metadatas[i],
            "distance": distances[i]
        })
        
    return chunks

if __name__ == "__main__":
    # Test queries
    import json
    print("Testing retrieval for 'exit load of Small Cap':")
    res1 = retrieve_context("What is the exit load of HDFC Small Cap?")
    for r in res1:
         print(f"ID: {r['id']}, Slug: {r['metadata']['scheme_slug']}, Section: {r['metadata']['section']}, Dist: {r['distance']:.4f}")
