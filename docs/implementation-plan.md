# Implementation Plan: Mutual Fund FAQ Assistant (Facts-Only Q&A)

This document provides a step-by-step roadmap for building the Mutual Fund FAQ RAG Assistant. The plan is organized into logical, sequential phases to ensure robust ingestion, strict compliance, accurate retrieval, and a polished user interface.

---

## Phase-Wise Implementation Roadmap

### Phase 0: Project Setup & Environment Setup
Establish the development workspace, directories, and configure required dependencies and environment variables.

- [ ] **Directory Structure**: Setup the workspace folders:
  ```text
  ├── data/
  │   ├── raw/                 # Store raw HTML scraped from Groww
  │   └── processed/           # Parsed and section-extracted text files
  ├── docs/                    # Architecture and project documentation
  ├── ingestion/               # Fetch, parse, tag, and embed pipeline code
  ├── core/                    # Retrieval, Classifier, and LLM orchestration
  ├── ui/                      # Streamlit application
  └── config/                  # Configuration files and schemas
  ```
- [ ] **Dependency Management**: Create a `requirements.txt` containing packages:
  - `requests`, `beautifulsoup4` (for scraping and parsing HTML)
  - `chromadb` (or `faiss-cpu`) (for vector database storage)
  - `openai` / `google-generativeai` (for embeddings and LLM generation)
  - `streamlit` (for the user interface)
  - `python-dotenv` (for loading environment variables)
- [ ] **Environment Configuration**: Set up a `.env` file for API keys and database paths.

---

### Phase 1: Ingestion, Scraping & Section Extraction
Implement scripts to download, clean, and categorize scheme page contents into logical sections.

- [x] **Task 1.1: Scraper/Fetcher (`ingestion/fetch.py`)**
  - Make HTTP GET requests to the 5 targeted Groww mutual fund URLs:
    - *HDFC Silver ETF FoF (Direct Growth)*
    - *HDFC Small Cap Fund (Direct Growth)*
    - *HDFC Defence Fund (Direct Growth)*
    - *HDFC Gold ETF Fund of Fund (Direct Plan Growth)*
    - *HDFC Mid-Cap Opportunities Fund (Direct Growth)*
  - Write raw HTML response to `data/raw/` with a standard naming convention and save a metadata JSON file containing the fetch timestamp.
- [x] **Task 1.2: Page Parser (`ingestion/parse.py`)**
  - Load raw HTML from `data/raw/` and strip layout boilerplates (navigation menus, headers, footer components, sidebars, interactive elements, scripts, ads).
  - Extract the main text contents cleanly to represent only the target scheme data.
- [x] **Task 1.3: Section Extraction & Tagging**
  - Implement a rule-based parser or structural tokenizer to segment and tag content blocks into the 9 key architectural sections:
    1. `overview`
    2. `expense_ratio`
    3. `exit_load`
    4. `minimum_investment`
    5. `benchmark`
    6. `tax`
    7. `fund_management`
    8. `investment_objective`
    9. `fund_house`
  - Output tagged segments as structured JSON or plain text files in `data/processed/`.
- [x] **Task 1.4: Chunking Strategy Formulation**
  - **Strategy**: Enforce **Section-Level Semantic Chunking** (1 Section = 1 Chunk).
  - **Details**: Since the maximum section size is only 1,566 characters (~350 tokens), set character overlap to `0` and split chunks strictly by section boundaries. This guarantees complete semantic integrity for tables, rules, and bios, and enables precise metadata-driven filtering to eliminate query confusion.

---

### Phase 2: Embedding & Vector DB Storage
Convert text chunks into vector embeddings and index them with metadata.

- [x] **Task 2.1: Vector DB Setup (`ingestion/vector_store.py`)**
  - Initialized local persistent **ChromaDB** storage database at `data/vectordb`.
- [x] **Task 2.2: Embedding Generator**
  - Implemented local embedding generation utilizing **BAAI/bge-small-en-v1.5** via the `sentence-transformers` library (running completely free and offline).
- [x] **Task 2.3: DB Loader**
  - Programmed standard upserts for the 45 sections with metadata tags: `scheme_slug`, `section`, `source_url`, and `last_updated`.
- [x] **Task 2.4: Unified Pipeline Script (`ingestion/run_pipeline.py`)**
  - Built a wrapper script `ingestion/run_pipeline.py` that coordinates the entire fetch -> parse -> tag -> embed -> load pipeline.

---

### Phase 3: Scheduler Integration
Automate the ingestion process to execute daily.

- [x] **Task 3.1: Daily Scheduler Config**
  - Set up a automation wrapper (e.g., using python-based `apscheduler`, Cron, or a GitHub Actions runner) to execute `ingestion/run_pipeline.py` every 24 hours.
  - Ensure logging is enabled to capture run success and record any parsing or fetching failures.

---

### Phase 4: Query Guardrails & Retrieval Pipeline
Classify queries to prevent compliance/advisory violations and retrieve candidate documents.

- [x] **Task 4.1: Guardrails Classifier (`core/classifier.py`)**
  - Implement a quick classification step using a lightweight prompt or regex pattern to identify non-factual, comparative, or investment advice questions (e.g. *"Which fund should I buy?"*, *"Is HDFC Small Cap better than Mid Cap?"*).
- [x] **Task 4.2: Refusal Handler (`core/refusal.py`)**
  - If a query is flagged as advisory, immediately halt pipeline execution and return a polite disclaimer message.
  - Append an educational URL (e.g., AMFI or SEBI Investor Education Resources).
- [x] **Task 4.3: Context Retriever (`core/retriever.py`)**
  - Convert factual queries to embeddings.
  - Perform vector search in ChromaDB using cosine similarity to fetch the Top-K chunks.
  - Parse query keywords to apply metadata filters (e.g. restrict search to a specific scheme if the user mentions *"HDFC Defence"*).

---

### Phase 5: RAG Prompt & Response Generation
Inject context into the prompt, invoke the LLM, and enforce factual constraints.

- [x] **Task 5.1: LLM Prompts (`core/generator.py`)**
  - Implement prompt engineering with system instructions:
    - Answer questions using **only** the provided retrieved context.
    - If the context does not contain the answer, refuse to speculate.
    - Keep responses concise (maximum of **3 sentences**).
    - Provide **exactly one citation link** matching the source Groww URL.
- [x] **Task 5.2: Output Formatting & Post-Processing**
  - format final response text.
  - Append the footer: `Last updated from sources: <date>` where date is retrieved from chunk metadata.

---

### Phase 6: Streamlit UI Development
Provide a clean, elegant web experience.

- [x] **Task 6.1: Layout Design (`app.py`)**
  - Build the Streamlit interface matching modern design guidelines.
  - Add a prominent, static disclaimer: *"Facts-only. No investment advice."*
- [x] **Task 6.2: Interaction & Example Questions**
  - Add query pills / example buttons for quick trial questions (e.g. expense ratios, exit loads, fund managers).
  - Implement the chat history state loop and connect input text box to the `core/` pipeline.

---

### Phase 7: Evaluation & Hardening
Validate correctness, accuracy, and refusal behavior.

- [x] **Task 7.1: QA Test Suite**
  - Run a set of test queries (factual vs. advisory) and log performance.
  - Verify that:
    - No query generates financial advice or comparisons.
    - All citations are present and correct.
    - Source dates are correctly populated.
- [x] **Task 7.2: Final Documentation**
  - Write a comprehensive `README.md` file summarizing setup instructions, project architecture, and execution details.
