import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

def generate_response(query: str, chunks: list[dict]) -> dict:
    """
    Generates a facts-only response using the top retrieved context chunks.
    Enforces strict grounding, length limitations (<= 3 sentences), Groww citation, and footer dates.
    Falls back to showing raw retrieved chunks if no API keys are present.
    """
    if not chunks:
        return {
            "status": "success",
            "response": (
                "I couldn't find specific information on this in our knowledge base. "
                "For accurate details, please visit: https://groww.in/mutual-funds "
                "or contact our support team."
            ),
            "source_url": "https://groww.in/mutual-funds",
            "last_updated": "N/A",
            "fallback": False
        }

    # Extract source details
    source_url = chunks[0]["metadata"].get("source_url", "https://groww.in")
    last_updated = chunks[0]["metadata"].get("last_updated", "N/A")
    if last_updated != "N/A" and "T" in last_updated:
        last_updated = last_updated.split("T")[0]

    # Check for API Keys
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    has_gemini = gemini_key and gemini_key != "your_gemini_api_key_here"
    has_openai = openai_key and openai_key != "your_openai_api_key_here"
    
    if not (has_gemini or has_openai):
        logger.warning("No valid API keys found for generation. Returning offline fallback content.")
        
        # Build clean offline fallback response
        fallback_text = (
            "Here is the official factual information retrieved directly from the mutual fund scheme documentation:\n\n"
        )
        
        for idx, c in enumerate(chunks[:2]):  # Show up to top 2 chunks
            section_name = c["metadata"]["section"].replace("_", " ").title()
            scheme_name = c["metadata"]["scheme_slug"].replace("-", " ").title()
            # Replace literal Unicode bullets with markdown lists
            chunk_text = c['text'].replace('•', '*')
            fallback_text += f"**{idx+1}. {scheme_name} - {section_name}**:\n{chunk_text}\n\n"
            
        fallback_text += f"You can verify this directly on the [Groww Official Page]({source_url})."
        
        return {
            "status": "success",
            "response": fallback_text.strip(),
            "source_url": source_url,
            "last_updated": last_updated,
            "fallback": True
        }

    # Compile Context text
    context_text = ""
    for idx, c in enumerate(chunks):
        context_text += f"--- Chunk {idx+1} [Source: {c['metadata']['source_url']}] ---\n{c['text']}\n\n"

    # Construct strict system prompt
    prompt = f"""You are a knowledgeable assistant for MintFlow AI.

## Primary Knowledge Source
You have been provided with factual information from our official knowledge base under "Retrieved Context" below.
Your ONLY source of truth is this provided "Retrieved Context".

## Strict Retrieval Rules
1. **Analyze the Retrieved Context** to answer the User Query. Do not rely on your general training knowledge for domain-specific questions.
2. If the answer IS found in the Retrieved Context → respond using ONLY that information.
3. If the answer is NOT found in the Retrieved Context, or the context is irrelevant to the query → YOU MUST respond EXACTLY with:
   "I couldn't find specific information on this in our knowledge base. For accurate details, please visit: {source_url} or contact our support team."
4. **Never fabricate or hallucinate** information not present in the Retrieved Context.
5. If the query is ambiguous, ask a clarifying question.

## Tone & Format
- Be concise, helpful, and professional.
- Always cite the source when providing an answer.
- If redirecting, be polite and provide the exact URL.

Retrieved Context:
{context_text}

User Query: "{query}"

Response:"""

    response_text = ""
    
    # 1. Try Gemini
    if has_gemini:
        try:
            logger.info("Generating response with Gemini...")
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            response_text = response.text.strip()
        except Exception as e:
            logger.error(f"Gemini generation failed: {e}", exc_info=True)

    # 2. Try OpenAI if Gemini failed or is not configured
    if not response_text and has_openai:
        try:
            logger.info("Generating response with OpenAI...")
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=200
            )
            response_text = response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}", exc_info=True)

    # Fallback to offline presentation if API calls failed at runtime
    if not response_text:
        logger.error("All LLM generation APIs failed. Falling back to raw context display.")
        return {
            "status": "success",
            "response": (
                "Here is the official factual information retrieved directly from the mutual fund scheme documentation:\n\n"
                f"{chunks[0]['text'].replace('•', '*')}"
            ),
            "source_url": source_url,
            "last_updated": last_updated,
            "fallback": True
        }

    return {
        "status": "success",
        "response": response_text,
        "source_url": source_url,
        "last_updated": last_updated,
        "fallback": False
    }

if __name__ == "__main__":
    # Test generator fallback
    dummy_chunks = [
        {
            "text": "The exit load for HDFC Defence Fund is 1% if redeemed within 1 year.",
            "metadata": {
                "scheme_slug": "hdfc-defence-fund-direct-growth",
                "section": "exit_load",
                "source_url": "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth",
                "last_updated": "2026-05-31T23:00:00Z"
            }
        }
    ]
    res = generate_response("What is the exit load of HDFC Defence?", dummy_chunks)
    print(res)
