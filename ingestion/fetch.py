import os
import sys
import json
import requests
from datetime import datetime

# URL configuration
GROWW_URLS = [
    "https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth",
    "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
]

DATA_RAW_DIR = os.path.join("data", "raw")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_scheme_slug(url):
    return url.split("/")[-1]

def fetch_all():
    ensure_dir(DATA_RAW_DIR)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    for url in GROWW_URLS:
        slug = get_scheme_slug(url)
        html_path = os.path.join(DATA_RAW_DIR, f"{slug}.html")
        meta_path = os.path.join(DATA_RAW_DIR, f"{slug}_metadata.json")
        
        print(f"Fetching: {url} ...")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Save HTML
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            
            # Save Metadata
            metadata = {
                "url": url,
                "scheme_slug": slug,
                "fetched_at": datetime.utcnow().isoformat() + "Z",
                "status_code": response.status_code,
                "html_file": html_path
            }
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=4)
                
            print(f"Successfully saved {slug}.html and metadata.")
            
        except Exception as e:
            print(f"Error fetching {url}: {e}", file=sys.stderr)

if __name__ == "__main__":
    fetch_all()
