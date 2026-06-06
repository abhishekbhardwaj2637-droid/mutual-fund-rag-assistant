# Mutual Fund FAQ Assistant (Facts-Only RAG)

A compliance-hardened, Retrieval-Augmented Generation (RAG) assistant for querying factual mutual fund scheme data from official sources (Groww scheme pages and underlying AMC documents). Designed to answer factual questions while strictly preventing investment advice, fund comparisons, and performance speculations.

---

## ⚡ Key Features
- **Strict Compliance Classifier**: Hybrid heuristic-regex and LLM compliance classifier filters out advisory, comparative, or speculative queries.
- **Resilient Ingestion Scheduler**: Automates the scraping and loading pipeline. Executes in isolated processes to prevent memory leaks and scheduler crashes.
- **Isolated Document Retrieval**: Metadata-level database filtering restricts searches strictly to the queried fund scheme, avoiding cross-scheme data contamination.
- **Grounded Prompt Generator**: Enforces maximum response lengths (<= 3 sentences) and exactly one citation.
- **Obsidian Mint Dashboard**: A high-end Streamlit UI built with a glassmorphic dark-mode style, pill query triggers, active fund highlights, and redirect links to regulatory websites (SEBI / AMFI).
- **Offline Fallback Mode**: Works completely offline out of the box. If API keys are absent, it retrieves database facts and formats them cleanly rather than throwing errors.

---

## 🛠️ Folder Structure
```text
├── data/
│   ├── raw/                 # Raw HTML pages scraped from Groww
│   ├── processed/           # Parsed section-level JSON and Markdown chunks
│   └── vectordb/            # Local persistent ChromaDB database files
├── docs/                    # System architecture and implementation plans
├── ingestion/
│   ├── fetch.py             # Scraper to fetch Groww HTML pages
│   ├── parse.py             # Parser to extract and tag the 9 core sections
│   ├── vector_store.py      # Embedding generator and ChromaDB loader
│   ├── run_pipeline.py      # Unified wrapper script to run ingestion
│   └── scheduler.py         # Subprocess-protected daily timer loop
├── core/
│   ├── classifier.py        # Compliance guardrails query classifier
│   ├── refusal.py           # Advisory refusal disclaimer formatter
│   ├── retriever.py         # Cached local BGE retriever with metadata filtering
│   ├── generator.py         # Grounded LLM response compiler
│   └── orchestrator.py      # Core RAG pipeline controller
├── tests/
│   └── run_qa_tests.py      # QA test suite and evaluation script
├── setup_scheduler.ps1      # Windows Task Scheduler automation script
├── app.py                   # Streamlit web dashboard
└── requirements.txt         # Package dependencies
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.14.5)
- Standard internet connection (for initial model downloading and page fetching)

### 2. Install Dependencies
Clone the repository, open your terminal, and install the packages:
```bash
py -m pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file in the project root (you can copy `.env.template`):
```text
# API Keys (Optional: Leave as placeholders to run in Offline Fallback Mode)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Vector DB & Data paths
VECTOR_DB_DIR=d:/Abhishek PM/PROJECT 2 - MF WITH RAG/data/vectordb
DATA_RAW_DIR=d:/Abhishek PM/PROJECT 2 - MF WITH RAG/data/raw
DATA_PROCESSED_DIR=d:/Abhishek PM/PROJECT 2 - MF WITH RAG/data/processed
```

---

## 🚀 Running the System

### 1. Sync the Database (Ingestion Pipeline)
Run the pipeline once to fetch the latest details from the 5 supported schemes:
```bash
py ingestion/run_pipeline.py
```
This fetches Groww pages, segments them into 9 sections (overview, exit load, expense ratio, benchmark, minimum investment, tax, fund management, objective, fund house), generates `BAAI/bge-small-en-v1.5` embeddings locally, and loads them into ChromaDB.

### 2. Start the Daily Scheduler
#### Option A: Running the Python daemon loop (Shell)
```bash
py ingestion/scheduler.py
```
This loop executes the pipeline immediately on startup and schedules it to run every 24 hours.

#### Option B: Registering a Windows Task Scheduler (Recommended)
Open PowerShell as **Administrator** and execute:
```powershell
Set-ExecutionPolicy Bypass -Scope Process
.\setup_scheduler.ps1
```
This registers a native Windows task named `MutualFundFAQ_IngestionPipeline` that triggers the pipeline every day at **10:00 AM** without consuming any system resources while idle.

### 3. Run the Streamlit Dashboard
```bash
py -m streamlit run app.py
```
Access the dashboard in your web browser at: [http://localhost:8501](http://localhost:8501).

---

## 🧪 Running the QA Test Suite
The QA suite tests 10 diverse queries (factual, advisory, out-of-scope) and asserts correct compliance classification, metadata filters, citations, and lengths.
Run:
```bash
py tests/run_qa_tests.py
```
The suite outputs results to:
- JSON Report: `data/qa_test_report.json`
- Markdown Report: `data/qa_test_report.md`

---

## 🔒 Compliance & Safety Guidelines
The assistant strictly implements SEBI / AMFI guidelines:
- **Zero Advisory Bias**: Subjective comparison queries (*"which is better?"*) and purchase advice (*"should I buy?"*) are refused with redirect buttons to the SEBI Investor Portal and AMFI corner.
- **Strict Grounding**: Generates responses using only context facts. Speculative returns prediction is refused.
- **Privacy Protection**: Does not ask for, capture, or store any sensitive data (OTPs, accounts, PAN, email).
