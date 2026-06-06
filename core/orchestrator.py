import logging
from core.classifier import classify_query
from core.refusal import get_refusal_response
from core.retriever import retrieve_context
from core.generator import generate_response

logger = logging.getLogger(__name__)

def handle_query(query: str) -> dict:
    """
    Main orchestrator function for the Mutual Fund FAQ Assistant RAG Pipeline.
    
    Ties together:
    1. Query Classification (Guardrails)
    2. Refusal Handling
    3. Document Retrieval
    4. Grounded Response Generation
    
    Returns:
        dict: A structured dictionary containing response payload, status, and metadata.
    """
    logger.info(f"Orchestrating query: '{query}'")
    
    # Step 1: Classify Query (Factual vs Advisory)
    classification = classify_query(query)
    logger.info(f"Query classification: {classification}")
    
    if classification == "ADVISORY":
        # Step 2: Route to Refusal Handler
        refusal = get_refusal_response(query)
        return refusal
        
    # Step 3: Retrieve Context Chunks from Vector Store
    # We retrieve top 3 chunks
    chunks = retrieve_context(query, k=3)
    logger.info(f"Retrieved {len(chunks)} chunks from ChromaDB.")
    
    # Step 4: Generate Response using retrieved context
    response_payload = generate_response(query, chunks)
    
    # Attach retrieved chunks metadata for frontend rendering/transparency if desired
    response_payload["retrieved_chunks"] = [
        {
            "id": c["id"],
            "section": c["metadata"]["section"],
            "scheme_slug": c["metadata"]["scheme_slug"],
            "distance": float(c["distance"])
        }
        for c in chunks
    ]
    
    # Return formatted response
    response_payload["query"] = query
    
    return response_payload

if __name__ == "__main__":
    import json
    # Test Factual
    print("TESTING FACTUAL QUERY:")
    res_fact = handle_query("What is the expense ratio of HDFC Small Cap Fund?")
    print(json.dumps(res_fact, indent=4))
    
    print("\n" + "="*60 + "\n")
    
    # Test Advisory
    print("TESTING ADVISORY QUERY:")
    res_adv = handle_query("Should I buy HDFC Defence Fund?")
    print(json.dumps(res_adv, indent=4))
