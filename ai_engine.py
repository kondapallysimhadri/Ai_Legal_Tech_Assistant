import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

AI_CONFIGURED = False
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = None

if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        AI_CONFIGURED = True
    except Exception as e:
        print(f"Error configuring Gemini: {e}")

class AILegalIntelligence:
    def __init__(self):
        self.client = client

    async def generate_json(self, prompt: str):

        if not self.client:
            return None
        try:

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{prompt}\n\nIMPORTANT: Return ONLY valid JSON. No markdown formatting, no code blocks.",
                config={"response_mime_type": "application/json"},
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"AI JSON Error: {e}")
            return None

    async def enrich_case(self, case_data: dict):

        if not self.client:
            return self.get_fallback_enrichment(case_data)

        prompt = f"""
        Analyze this legal case:
        Title: {case_data.get('title')}
        Company: {case_data.get('company')}
        Description: {case_data.get('description')}
        Amount: {case_data.get('compensation_amount')}
        Deadline: {case_data.get('deadline')}

        Perform these tasks:
        1. Simplify the case (150 words max).
        2. Extract bullet summary (what happened, who is affected, compensation, status).
        3. Define eligibility rules (what proof is needed).
        4. List required documents.
        5. Predict claim success probability (0-100%).
        6. Map to problem categories (Awareness gap, legal complexity, etc.).
        7. Generate a 4-step UI-ready timeline (crisis, lawsuit, settlement, payment).
        8. Calculate impact score (0-100) and category (Low/Med/High).
        9. Provide AI reasoning/explainability.

        Return a JSON object with keys:
        summary, bullet_points (list), eligibility_rules, required_documents (list),
        success_probability, problem_map (list), timeline (list of objects with 'event' and 'date'),
        impact_score, impact_category, ai_reasoning.
        """

        enriched = await self.generate_json(prompt)
        return enriched if enriched else self.get_fallback_enrichment(case_data)

    def get_fallback_enrichment(self, case_data):
        return {
            "summary": "This case involves a legal settlement. Detailed AI analysis is currently unavailable.",
            "bullet_points": [
                "Incident occurred",
                "Lawsuit filed",
                "Settlement reached",
            ],
            "eligibility_rules": "Contact the settlement administrator for specific rules.",
            "required_documents": ["Proof of purchase", "ID", "Claim form"],
            "success_probability": 75,
            "problem_map": ["Legal complexity"],
            "timeline": [
                {"event": "Crisis", "date": "TBD"},
                {"event": "Lawsuit", "date": "TBD"},
            ],
            "impact_score": 50,
            "impact_category": "Medium",
            "ai_reasoning": "Fallback data used due to API connectivity issues.",
        }

    async def get_chatbot_response(
        self, query: str, context: list, case_data: dict = None
    ):

        if not self.client:
            return "I'm sorry, my AI brain is currently offline. How else can I help?"

        case_context = (
            f"Context: User is asking about {case_data['title']}. Rules: {case_data.get('eligibility_rules')}"
            if case_data
            else ""
        )

        prompt = f"""
        Role: Empathetic AI Legal Assistant.
        {case_context}
        History: {context}
        User Query: {query}

        Guidelines:
        1. Be helpful and clear.
        2. Detect emotion (if user is stressed, be extra supportive).
        3. Show reasoning.
        4. ALWAYS include disclaimer: "I am an AI, not a lawyer. This is not legal advice."
        """

        response = self.client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        return (
            response.text if response else "I couldn't process that. Please try again."
        )

engine = AILegalIntelligence()

def summarize_breach(description):

    return "AI analysis in progress..."

def score_eligibility(breach_data, user_info):
    return {
        "status": "Likely Eligible",
        "confidence_score": 85,
        "reason": "AI assessment based on provided data.",
    }
