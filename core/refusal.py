def get_refusal_response(query: str) -> dict:
    """
    Returns a structured compliance refusal response with disclaimers and educational resources.
    """
    return {
        "status": "refused",
        "query": query,
        "response": (
            "I am a Facts-Only RAG Assistant. I cannot provide investment advice, buy/sell recommendations, "
            "comparative fund evaluations, or performance speculations. My scope is strictly limited to retrieving "
            "factual metrics from official mutual fund documents.\n\n"
            "For professional advisory services, please consult with a SEBI-registered Investment Advisor, "
            "or review investor awareness guidelines on official regulatory portals:"
        ),
        "links": [
            {
                "name": "SEBI Investor Education Portal",
                "url": "https://investor.sebi.gov.in/",
                "icon": "verified_user"
            },
            {
                "name": "AMFI Investor Awareness Corner",
                "url": "https://www.amfiindia.com/investor-corner",
                "icon": "account_balance_wallet"
            }
        ]
    }

if __name__ == "__main__":
    import json
    print(json.dumps(get_refusal_response("should i invest?"), indent=4))
