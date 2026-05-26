import os
import numpy as np
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from google import genai
from dotenv import load_dotenv
import datetime
import asyncio

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.get_database()

client_genai = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-2.0-flash-lite"


class ConversationalRAGEngine:
    def __init__(self):
        print("🧠 Initializing Conversational RAG Engine...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.vector_collection = db["vector_embeddings"]
        self.user_queries_collection = db["user_queries"]
        self.memory_collection = db["conversation_memory"]

    def cosine_similarity(self, v1, v2):
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    async def get_semantic_context(self, query, top_k=5):

        raw_vector = await asyncio.to_thread(self.model.encode, query)
        query_vector = raw_vector.tolist()

        all_vectors = await asyncio.to_thread(
            lambda: list(
                self.vector_collection.find(
                    {},
                    {
                        "embedding": 1,
                        "title": 1,
                        "content_preview": 1,
                        "source_url": 1,
                    },
                )
            )
        )

        if not all_vectors:
            return []

        results = []
        for v in all_vectors:
            if "embedding" not in v:
                continue
            sim = self.cosine_similarity(query_vector, v["embedding"])
            if sim > 0.15:
                results.append({**v, "similarity": sim})

        ranked = sorted(results, key=lambda x: x["similarity"], reverse=True)[:top_k]
        return ranked

    async def get_chat_history(self, session_id):
        history = await asyncio.to_thread(
            lambda: list(
                self.memory_collection.find({"session_id": session_id})
                .sort("timestamp", -1)
                .limit(5)
            )
        )
        history.reverse()
        return "\n".join([f"{h['role'].upper()}: {h['content']}" for h in history])

    async def get_answer(self, query, session_id="default"):
        import json

        context_items = await self.get_semantic_context(query)
        context_text_lines = []
        for c in context_items:
            enrichment_str = c.get("enrichment", "{}")
            try:
                if "```json" in enrichment_str:
                    enrichment_str = enrichment_str.split("```json")[1].split("```")[0]
                enrichment = json.loads(enrichment_str)
                summary = enrichment.get("ai_summary", c.get("content_preview", ""))
            except Exception:
                summary = c.get("content_preview", "")

            context_text_lines.append(
                f"--- CASE: {c.get('title', 'Unknown')} ---\nSUMMARY: {summary}\nSOURCE: {c.get('source_url', 'Unknown')}"
            )

        context_text = "\n\n".join(context_text_lines)
        history_text = await self.get_chat_history(session_id)

        prompt = f"""
        You are a Senior Legal Intelligence AI. You provide serious, grounded, and empathetic guidance based on verified data breaches and settlements.

        CONVERSATION HISTORY:
        {history_text}

        GROUNDED LEGAL CONTEXT (Verified Data from our Platform):
        {context_text if context_text else "No specific records found in our database for this exact query, but use your intelligence to guide based on general legal procedures."}

        INSTRUCTIONS:
        - NEVER be generic. Reference specific CASE NAMES and SOURCE URLs from the context.
        - If the user asks "what type of cases are here?", list several case names and their URLs from the context.
        - Structure your response with:
          1. 📜 Summary of relevant findings.
          2. 🔗 Verified Case Links (Name + URL).
          3. 💡 Strategic Suggestions / Next Steps.
        - Disclaimer: "Informational guidance only. Not legal advice."

        USER QUESTION: {query}

        AI ASSISTANT RESPONSE:
        """

        try:
            response = await client_genai.aio.models.generate_content(
                model=MODEL_NAME, contents=prompt
            )
            answer = response.text.strip()

            await asyncio.to_thread(
                self.user_queries_collection.insert_one,
                {
                    "session_id": session_id,
                    "question": query,
                    "answer": answer,
                    "timestamp": datetime.datetime.utcnow(),
                    "metadata": {
                        "source_count": len(context_items),
                        "model": MODEL_NAME,
                    },
                },
            )

            await asyncio.to_thread(
                self.memory_collection.insert_one,
                {
                    "session_id": session_id,
                    "role": "user",
                    "content": query,
                    "timestamp": datetime.datetime.utcnow(),
                },
            )
            await asyncio.to_thread(
                self.memory_collection.insert_one,
                {
                    "session_id": session_id,
                    "role": "assistant",
                    "content": answer,
                    "timestamp": datetime.datetime.utcnow(),
                    "retrieved_count": len(context_items),
                },
            )

            return {
                "answer": answer,
                "sources": [c["source_url"] for c in context_items],
                "confidence": "High" if len(context_items) > 0 else "Low",
            }

        except Exception as e:
            print(f"⚠️ RAG Reasoning Error: {e}")

            if context_items:

                top_titles = [c.get("title", "Unknown Case") for c in context_items[:3]]

                fallback_answer = f"""
Based on our local legal intelligence database, I found several relevant legal cases connected to your query.

Relevant cases:
- {top_titles[0] if len(top_titles) > 0 else "Unknown"}
- {top_titles[1] if len(top_titles) > 1 else "Unknown"}
- {top_titles[2] if len(top_titles) > 2 else "Unknown"}

Potential legal risks may include:
- Identity theft
- Financial fraud
- Privacy exposure
- Unauthorized account access

Recommended actions:
- Change passwords immediately
- Enable MFA on important accounts
- Monitor banking activity
- Review official settlement notices
- Consider credit monitoring services
"""

            return {
                "answer": fallback_answer,
                "sources": [c["source_url"] for c in context_items],
                "confidence": "Medium (Fallback)",
            }


if __name__ == "__main__":
    engine = ConversationalRAGEngine()

    user_input = "My SSN and banking data were leaked in a breach."

    res = asyncio.run(engine.get_answer(user_input))

    print(f"🤖 AI: {res['answer']}")
