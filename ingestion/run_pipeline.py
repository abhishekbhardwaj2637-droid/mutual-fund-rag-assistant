import os
import sys
import time

# Append current working directory to Python path for import compatibility
sys.path.append(os.getcwd())

def run_ingestion_pipeline():
    print("=" * 60)
    print("STARTING MUTUAL FUND INGESTION & INDEXING PIPELINE")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. Fetch
    print("\n--- STEP 1: Fetching Raw HTML from Groww ---")
    try:
        from ingestion.fetch import fetch_all
        fetch_all()
    except Exception as e:
        print(f"CRITICAL ERROR in fetcher: {e}", file=sys.stderr)
        sys.exit(1)
        
    # 2. Parse & Tag
    print("\n--- STEP 2: Parsing HTML & Extracting Section Tags ---")
    try:
        from ingestion.parse import parse_all
        parse_all()
    except Exception as e:
        print(f"CRITICAL ERROR in parser: {e}", file=sys.stderr)
        sys.exit(1)
        
    # 3. Vector DB Loader
    print("\n--- STEP 3: Embedding & Loading Chunks into ChromaDB ---")
    try:
        from ingestion.vector_store import load_processed_data_to_db
        load_processed_data_to_db()
    except Exception as e:
        print(f"CRITICAL ERROR in database loader: {e}", file=sys.stderr)
        sys.exit(1)
        
    print("\n" + "=" * 60)
    print("PIPELINE EXECUTED SUCCESSFULLY. VECTOR STORE IS READY.")
    print("=" * 60)

if __name__ == "__main__":
    run_ingestion_pipeline()
