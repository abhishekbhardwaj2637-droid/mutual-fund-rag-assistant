import os
import re
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

# Heuristic lists for advisory/comparative classification
ADVISORY_PATTERNS = [
    # Advice / Recommendations
    r"should\s+i\s+(buy|invest|sell|choose|pick)",
    r"which\s+fund\s+is\s+(better|best|good|recommended)",
    r"recommend\s+me",
    r"where\s+should\s+i\s+invest",
    r"is\s+it\s+safe\s+to\s+invest",
    r"is\s+it\s+good\s+to\s+buy",
    r"should\s+i\s+choose",
    r"buy\s+or\s+sell",
    r"investment\s+advice",
    r"suggest\s+a\s+fund",
    r"which\s+(one|fund)\s+should\s+i",
    # Comparisons
    r"\bbetter\b",
    r"\bvs\b",
    r"compare",
    r"comparison",
    r"difference\s+between",
    # Speculation / Predictions
    r"future\s+performance",
    r"expected\s+return",
    r"how\s+much\s+return",
    r"predict",
    r"double",
    r"will\s+.*grow",
    r"profit\s+forecast"
]

def classify_by_heuristics(query: str) -> str:
    """
    Classify a query as ADVISORY or FACTUAL using pre-defined regex patterns.
    """
    query_lower = query.lower().strip()
    
    for pattern in ADVISORY_PATTERNS:
        if re.search(pattern, query_lower):
            logger.info(f"Heuristics classified query as ADVISORY matching pattern: {pattern}")
            return "ADVISORY"
            
    return "FACTUAL"

def classify_by_llm(query: str) -> str:
    """
    Classify a query using Gemini or OpenAI API if keys are configured.
    Returns "FACTUAL" or "ADVISORY".
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    # Check if keys are placeholders or not set
    has_gemini = gemini_key and gemini_key != "your_gemini_api_key_here"
    has_openai = openai_key and openai_key != "your_openai_api_key_here"
    
    if not (has_gemini or has_openai):
        logger.warning("No valid LLM API keys found. Defaulting to heuristic classification.")
        return classify_by_heuristics(query)
        
    prompt = f"""You are a compliance guardrail classifier for a Mutual Fund facts-only Q&A system.
Your job is to classify the user's query into one of two categories:
1. FACTUAL: The query is asking for objective, verifiable facts about a mutual fund scheme (e.g. expense ratios, exit loads, fund managers, minimum investment amounts, benchmark indices, taxation rules, NAV, AUM, launch date, etc.).
2. ADVISORY: The query is asking for investment advice, recommendations, buy/sell decisions, comparison between funds, future return speculations, or subjective opinions (e.g. "which fund should I buy?", "is small cap better than mid cap?", "will HDFC defence give good returns?").

User Query: "{query}"

Output ONLY "FACTUAL" or "ADVISORY". Do not include any other text or explanation."""

    if has_gemini:
        try:
            logger.info("Using Gemini to classify query compliance...")
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            result = response.text.strip().upper()
            if result in ["FACTUAL", "ADVISORY"]:
                return result
            logger.warning(f"Unexpected classification result from Gemini: {result}")
        except Exception as e:
            logger.error(f"Gemini classification failed: {e}", exc_info=True)
            
    if has_openai:
        try:
            logger.info("Using OpenAI to classify query compliance...")
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=5
            )
            result = response.choices[0].message.content.strip().upper()
            if result in ["FACTUAL", "ADVISORY"]:
                return result
            logger.warning(f"Unexpected classification result from OpenAI: {result}")
        except Exception as e:
            logger.error(f"OpenAI classification failed: {e}", exc_info=True)
            
    # Ultimate fallback if LLM calls fail
    return classify_by_heuristics(query)

def classify_query(query: str) -> str:
    """
    Classifies a query as ADVISORY (seeking advice/recommendation/comparison)
    or FACTUAL (seeking objective facts).
    """
    # 1. Run heuristics first (covers most obvious cases instantly)
    heuristic_res = classify_by_heuristics(query)
    if heuristic_res == "ADVISORY":
        return "ADVISORY"
        
    # 2. Run LLM check if keys are configured
    return classify_by_llm(query)

if __name__ == "__main__":
    # Test queries
    test_queries = [
        "What is the exit load of HDFC Small Cap?",
        "Should I buy HDFC Defence Fund?",
        "Compare HDFC Mid Cap and HDFC Small Cap",
        "Who is the manager of HDFC Gold ETF?",
        "Is HDFC Gold better than HDFC Silver?"
    ]
    for q in test_queries:
        print(f"Query: '{q}' -> Classification: {classify_query(q)}")
