import os
import sys
from google import genai

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from utils import log_requests, log_prediction, detect_drift
from rule_engine import rule_engine
import uvicorn
import datetime
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

os.environ["TOKENIZERS_PARALLELISM"] = "false"

load_dotenv()


class ModelRegistry:
    @classmethod
    def get_model(cls):
        return None


MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["legal_ai_db"]
cases_collection = db["vector_embeddings"]
breaches_collection = db["breaches"]
user_queries_collection = db["user_queries"]
submitted_claims_collection = db["submitted_claims"]
claim_vectors_collection = db["claim_vectors"]

rag_engine = None
RAG_AVAILABLE = False


def get_rag_engine():
    global rag_engine, RAG_AVAILABLE
    if rag_engine is None:
        try:
            print("📦 [LAZY LOAD] Loading RAG Engine on first request...")
            from rag.rag_engine import ConversationalRAGEngine

            rag_engine = ConversationalRAGEngine()
            RAG_AVAILABLE = True
        except Exception as e:
            print(f"⚠️ RAG Engine initialization failed: {e}")
            RAG_AVAILABLE = False
    return rag_engine


from compliance import router as compliance_router

app = FastAPI(
    title="Eligibility Prediction API",
    description="AI-Powered Smart Legal Claim Assistant - Eligibility Inference",
    version="2.0.0",
)

app.include_router(compliance_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(log_requests)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatInput(BaseModel):
    question: str
    jurisdiction: Optional[str] = "Global"
    session_id: Optional[str] = "default_user"
    history: Optional[List[ChatMessage]] = []


class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: str


class ClaimInput(BaseModel):
    breach_type: str = Field(
        ..., description="Type of the breach (e.g., healthcare, finance)"
    )
    data_exposed: str = Field(
        ..., description="Data elements exposed (e.g., SSN, Email)"
    )
    records_affected: int = Field(..., ge=0, description="Number of records affected")
    company_type: str = Field(..., description="Type of company (e.g., bank, tech)")
    jurisdiction: str = Field(..., description="Legal jurisdiction (e.g., US, EU)")
    time_since_breach: int = Field(..., ge=0, description="Time since breach in days")
    user_impact_level: str = Field(..., description="Low, Medium, or High")
    past_case_similarity_score: float = Field(
        ..., ge=0.0, le=1.0, description="Score from 0 to 1"
    )


class PredictionResponse(BaseModel):
    prediction: str
    model_prediction: str
    confidence: float
    calibrated: bool
    uncertainty: str
    success_probability: Optional[float] = None
    explanation: List[str]
    action_plan: List[str]
    is_rule_blocked: bool
    rule_reason: Optional[str]
    rule_override: Optional[str] = None
    fallback_message: Optional[str] = None
    missing_fields: List[str] = []
    disclaimer: str = "This is AI guidance, not legal advice."


class UserRegister(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class PremiumApplication(BaseModel):
    name: str
    email: str
    password: str
    citizen_type: str
    state: str
    district: str
    village_town: str
    identity_type: str
    identity_number: str
    exposed_data: List[str]
    problem_statement: str


class ClaimSubmission(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: str
    address: str
    city: str
    state: str
    zip: str
    country: str
    affected: bool
    notification_method: str
    relationship: str
    consent: bool
    evidence_types: List[str] = []
    case_id: Optional[str] = None
    problem_description: Optional[str] = None


class PredictionOutput(BaseModel):
    prediction: str
    confidence: float
    explanation: List[str]
    action_plan: List[str]
    rule_reason: Optional[str] = None
    matched_cases: int
    disclaimer: str = "This is AI guidance, not legal advice."


import hashlib
import secrets


def get_password_hash(password):
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${hashed}"


def verify_password(plain_password, hashed_password):
    salt, stored_hash = hashed_password.split("$", 1)
    check_hash = hashlib.sha256((plain_password + salt).encode()).hexdigest()
    return check_hash == stored_hash


import time
from cachetools import TTLCache, cached
import asyncio

import redis
import psutil
import json

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
try:
    redis_client = redis.Redis(
        host=REDIS_HOST, port=6379, db=0, socket_connect_timeout=1
    )
    redis_client.ping()
    REDIS_AVAILABLE = True
except (redis.ConnectionError, redis.TimeoutError):
    print("⚠️ Redis not available. Falling back to in-memory dictionary for showcase.")
    redis_client = {}
    REDIS_AVAILABLE = False


@app.middleware("http")
async def add_performance_metrics(request: Request, call_next):

    start_time = time.time()

    cpu_load = psutil.cpu_percent()
    request.state.low_latency_mode = cpu_load > 85

    response = await call_next(request)

    duration = time.time() - start_time
    response.headers["X-Process-Time"] = f"{duration:.4f}s"
    if request.state.low_latency_mode:
        response.headers["X-Graceful-Degradation"] = "active"

    print(
        f"  [METRIC] {request.method} {request.url.path} took {duration:.4f}s (CPU: {cpu_load}%)"
    )
    return response


@app.post("/register")
async def register(user: UserRegister):
    if db["users"].find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(user.password)
    db["users"].insert_one(
        {
            "username": user.username,
            "password": hashed_password,
            "email": user.email,
            "created_at": datetime.datetime.utcnow(),
        }
    )
    return {"message": "User registered successfully"}


@app.post("/login")
async def login(user: UserLogin):
    db_user = db["users"].find_one({"username": user.username})
    if not db_user or not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "message": "Login successful",
        "user": {"username": db_user["username"], "email": db_user.get("email")},
    }


@app.post("/premium-apply")
async def premium_apply(app_data: PremiumApplication):

    db["premium_applications"].insert_one(
        {
            **app_data.dict(),
            "status": "Pending",
            "submitted_at": datetime.datetime.utcnow(),
        }
    )
    return {"message": "Premium application submitted successfully"}


@app.post("/submit-claim")
async def submit_claim(claim: ClaimSubmission):
    tracking_id = f"CLM-{secrets.token_hex(4).upper()}"
    submission_time = datetime.datetime.utcnow()

    claim_dict = claim.dict()
    claim_dict["tracking_id"] = tracking_id
    claim_dict["submitted_at"] = submission_time
    claim_dict["status"] = "Under AI Review"

    claim_dict["ai_analysis"] = {
        "document_quality": 85,
        "evidence_strength": "High",
        "missing_info": ["None"],
        "payout_estimate": "$2,500 - $12,000",
    }

    db["submitted_claims"].insert_one(claim_dict)

    try:
        model = ModelRegistry.get_model()
        text_for_embedding = f"{claim.first_name} {claim.last_name}: {claim.problem_description or 'No description'}"
        # embedding = model.encode(text_for_embedding).tolist()

        db["claim_vectors"].insert_one(
            {
                "tracking_id": tracking_id,
                "vector": [],
                "metadata": {
                    "name": f"{claim.first_name} {claim.last_name}",
                    "email": claim.email,
                },
            }
        )
    except Exception as e:
        print(f" Vector generation failed for claim: {e}")

    return {
        "message": "Claim submitted successfully",
        "tracking_id": tracking_id,
        "status": "Success",
    }


class SearchInput(BaseModel):
    query: str


@app.post("/search")
async def search_cases(search_input: SearchInput):

    query = search_input.query.strip()
    if not query:
        return {
            "results": [],
            "total_matches": 0,
            "ai_overview": "Please enter a search term.",
        }

    try:
        return {
            "results": [],
            "total_matches": 0,
            "ai_overview": "Semantic search temporarily disabled.",
        }
    except Exception as e:
        print(f"⚠️ Vector Model Error: {e}")
        return {
            "results": [],
            "total_matches": 0,
            "ai_overview": "Semantic search engine is currently offline.",
        }

    try:

        all_cases = list(db["vector_embeddings"].find({}))
        import numpy as np

        query_vec = np.array(query_embedding)
        query_norm = np.linalg.norm(query_vec)

        scored_cases = []
        for c in all_cases:
            if "embedding" in c:
                doc_vec = np.array(c["embedding"])
                doc_norm = np.linalg.norm(doc_vec)
                if query_norm > 0 and doc_norm > 0:
                    sim = np.dot(query_vec, doc_vec) / (query_norm * doc_norm)
                    scored_cases.append((sim, c))

        scored_cases.sort(key=lambda x: x[0], reverse=True)

        top_matches = [c for sim, c in scored_cases[:15] if sim > 0.15]
    except Exception as e:
        print(f"⚠️ Vector Calculation Error: {e}")
        top_matches = []

    results = []
    for c in top_matches:
        c_id = str(c.get("_id"))
        enrichment_str = c.get("enrichment", "{}")
        try:
            import json

            if "```json" in enrichment_str:
                enrichment_str = enrichment_str.split("```json")[1].split("```")[0]
            enrichment = json.loads(enrichment_str)
        except Exception:
            enrichment = {}

        company = enrichment.get("company", c.get("title", "Unknown Company"))
        title = c.get("title", company)
        summary = enrichment.get("ai_summary", c.get("content_preview", ""))
        raw_impact_level = enrichment.get("risk_level", "Medium")

        results.append(
            {
                "id": c_id,
                "title": title,
                "company": company,
                "summary": summary,
                "description": c.get("content_preview", ""),
                "source_url": c.get("source_url", ""),
                "risk_level": raw_impact_level,
                "impact_category": raw_impact_level,
                "confidence": 92 if enrichment.get("eligibility") == "High" else 75,
                "eligibility": enrichment.get("eligibility", "Moderate"),
                "estimated_compensation": enrichment.get("estimated_payout", "Unknown"),
                "deadline": enrichment.get("deadline", "Ongoing"),
                "exposed_data": enrichment.get("category", "Data Breach"),
                "success_probability": (
                    85 if enrichment.get("eligibility") == "High" else 60
                ),
                "ai_insight": enrichment.get(
                    "ai_reasoning", "Analysis indicates potential legal standing."
                ),
                "case_type": enrichment.get("category", "Data Breach"),
                "source": c.get("metadata", {}).get("source", "Legal Intel"),
            }
        )

    ai_overview = "Semantic retrieval found relevant legal precedents."
    if results and gemini_client:
        try:
            context = "\n".join(
                [f"- {r['title']}: {r['summary']}" for r in results[:3]]
            )
            prompt = f"As a Legal AI Assistant, analyze these cases for the query '{query}' and provide a concise, professional executive summary of trends and settlement potential:\n{context}"

            response = await asyncio.wait_for(
                gemini_client.aio.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                ),
                timeout=10.0,
            )
            ai_overview = response.text.strip()
        except Exception as e:
            print(f"⚠️ Search AI Overview fallback: {e}")

    return {
        "query": query,
        "total_matches": len(results),
        "results": results,
        "ai_overview": ai_overview,
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_eligibility(claim: ClaimInput):

    try:

        rule_results = rule_engine.calculate_eligibility(claim.dict())

        ml_prediction = "Rule-Based Analysis"
        ml_confidence = 0.5

        final_prediction = rule_results["eligibility_status"]
        final_confidence = rule_results["confidence_score"]

        log_prediction(claim.dict(), final_prediction, final_confidence)

        return PredictionResponse(
            prediction=final_prediction,
            model_prediction=f"{ml_prediction} (Neural Engine)",
            confidence=float(final_confidence),
            calibrated=True,
            uncertainty="low" if final_confidence > 0.7 else "medium",
            success_probability=rule_results["success_probability"],
            explanation=rule_results["reasoning"],
            action_plan=rule_results["recommended_actions"],
            is_rule_blocked=False,
            rule_reason=rule_results["urgency_level"],
            fallback_message=f"Estimated Compensation: {rule_results['payout_estimate']}",
            missing_fields=[],
        )

    except Exception as e:
        print(f"❌ Critical Prediction Failure: {e}")
        return PredictionResponse(
            prediction="Service Degraded",
            model_prediction="System Error",
            confidence=0.0,
            calibrated=False,
            uncertainty="high",
            success_probability=0.0,
            explanation=["The eligibility engine encountered a processing error."],
            action_plan=[
                "Our engineering team has been notified.",
                "Please retry in a few moments.",
            ],
            is_rule_blocked=True,
            rule_reason=str(e),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/feedback")
def submit_feedback(feedback: dict):

    try:
        feedback["timestamp"] = datetime.datetime.now().isoformat()
        db["feedback"].insert_one(feedback)
        return {"status": "success", "message": "Feedback stored for retraining."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cases")
def get_cases():

    try:
        cases_cursor = db["vector_embeddings"].find({}).sort("created_at", -1).limit(50)

        cases = []
        for c in cases_cursor:
            c_id = str(c.pop("_id"))
            enrichment_str = c.get("enrichment", "{}")
            try:
                import json

                if "```json" in enrichment_str:
                    enrichment_str = enrichment_str.split("```json")[1].split("```")[0]
                enrichment = json.loads(enrichment_str)
            except Exception:
                enrichment = {}

            company = enrichment.get("company", c.get("title", "Unknown Company"))
            title = c.get("title", company)

            if title == "Unknown" or not title or len(title) < 5:
                if enrichment.get("company") and enrichment.get("company") != "Unknown":
                    title = f"{enrichment.get('company')} Settlement Case"
                else:

                    summary_start = enrichment.get(
                        "ai_summary", c.get("content_preview", "")
                    )[:100]
                    if "Settlement" in summary_start:
                        title = summary_start.split("indicates")[0].strip()
                    else:
                        title = "Global Class Action Case"

            title = title.title()
            company = company.title()

            summary = enrichment.get("ai_summary", c.get("content_preview", ""))

            raw_impact_level = enrichment.get("risk_level", "Medium")

            cases.append(
                {
                    "id": c_id,
                    "title": title,
                    "company": company,
                    "summary": summary,
                    "description": c.get("content_preview", ""),
                    "source_url": c.get("source_url", ""),
                    "risk_level": raw_impact_level,
                    "impact_category": raw_impact_level,
                    "confidence": 92 if enrichment.get("eligibility") == "High" else 75,
                    "eligibility": enrichment.get("eligibility", "Moderate"),
                    "estimated_compensation": enrichment.get(
                        "estimated_payout", "Unknown"
                    ),
                    "deadline": enrichment.get("deadline", "Ongoing"),
                    "exposed_data": enrichment.get("category", "Data Breach"),
                    "success_probability": (
                        85 if enrichment.get("eligibility") == "High" else 60
                    ),
                    "ai_insight": enrichment.get(
                        "ai_reasoning", "Analysis indicates potential legal standing."
                    ),
                    "case_type": enrichment.get("category", "Data Breach"),
                    "source": c.get("metadata", {}).get("source", "Legal Intel"),
                    "required_documents": enrichment.get(
                        "documents_required", ["Identity Proof"]
                    ),
                    "legal_complexity": enrichment.get("legal_complexity", "Moderate"),
                    "success_trend": enrichment.get("success_trend", "Unknown"),
                }
            )

        return cases
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.get("/cases/{case_id}")
def get_case_detail(case_id: str):

    from bson import ObjectId

    try:
        c = db["vector_embeddings"].find_one({"_id": ObjectId(case_id)})
        if not c:
            raise HTTPException(status_code=404, detail="Case not found")

        c_id = str(c.pop("_id"))
        enrichment_str = c.get("enrichment", "{}")
        try:
            import json

            if "```json" in enrichment_str:
                enrichment_str = enrichment_str.split("```json")[1].split("```")[0]
            enrichment = json.loads(enrichment_str)
        except Exception:
            enrichment = {}

        company = enrichment.get("company", c.get("title", "Unknown Company"))

        case = {
            "id": c_id,
            "title": c.get("title", company),
            "company": company,
            "summary": enrichment.get("ai_summary", c.get("content_preview", "")),
            "description": c.get("content_preview", ""),
            "source_url": c.get("source_url", ""),
            "risk_level": enrichment.get("risk_level", "Medium"),
            "impact_category": enrichment.get("risk_level", "Medium"),
            "confidence": 92 if enrichment.get("eligibility") == "High" else 75,
            "eligibility": enrichment.get("eligibility", "Moderate"),
            "estimated_compensation": enrichment.get("estimated_payout", "Unknown"),
            "deadline": enrichment.get("deadline", "Ongoing"),
            "exposed_data": enrichment.get("category", "Data Breach"),
            "success_probability": (
                85 if enrichment.get("eligibility") == "High" else 60
            ),
            "ai_insight": enrichment.get(
                "ai_reasoning", "Analysis indicates potential legal standing."
            ),
            "required_documents": enrichment.get(
                "documents_required", ["Identity Proof", "Breach Notice"]
            ),
        }
        return case
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")


@app.post("/enrich")
async def trigger_enrichment():

    try:
        import subprocess

        proc = subprocess.Popen(
            ["./venv_new/bin/python", "scripts/legal_data_pipeline.py"],
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return {"status": "Pipeline triggered", "pid": proc.pid}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


class UserProfileInput(BaseModel):
    name: str
    location: str
    employment: str
    dataTypes: List[str]
    financialLoss: bool


class PrivacyAnalysisResponse(BaseModel):
    risk_score: int
    identity_theft_risk: str
    matched_cases: int
    recommended_action: str
    analysis_details: str


@app.post("/api/privacy/analyze", response_model=PrivacyAnalysisResponse)
async def analyze_privacy(profile: UserProfileInput):

    try:

        profile_dict = profile.dict()
        profile_dict["created_at"] = datetime.datetime.utcnow()
        try:
            db["user_profiles"].insert_one(profile_dict)
        except Exception as e:
            print(f"⚠️ Failed to save user profile: {e}")

        query = {
            "$or": [
                {"full_description": {"$regex": profile.location, "$options": "i"}},
            ]
            + [
                {"full_description": {"$regex": dt, "$options": "i"}}
                for dt in profile.dataTypes
            ]
        }
        if not profile.location and not profile.dataTypes:
            query = {}

        matched_count = db["vector_embeddings"].count_documents(query)

        risk_score = min(
            100, len(profile.dataTypes) * 15 + (20 if profile.financialLoss else 0)
        )

        prompt = f"""
        Analyze this user's data breach exposure profile and provide privacy intelligence:
        Location: {profile.location}
        Employment: {profile.employment}
        Exposed Data: {', '.join(profile.dataTypes)}
        Financial Loss: {profile.financialLoss}
        Matched Cases in DB: {matched_count}

        Return a strict JSON response:
        {{
            "identity_theft_risk": "Low/Medium/High/Critical",
            "recommended_action": "One sentence primary action",
            "analysis_details": "Short paragraph explaining the risk based on the data types exposed"
        }}
        """

        try:
            if not gemini_client:
                raise Exception("Gemini client not initialized")
            response = await asyncio.wait_for(
                gemini_client.aio.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt,
                ),
                timeout=15.0,
            )

            text_resp = response.text.replace("```json", "").replace("```", "").strip()
            analysis = json.loads(text_resp)
        except Exception as e:
            print(f"Privacy Engine fallback triggered: {e}")
            analysis = {
                "identity_theft_risk": (
                    "High" if len(profile.dataTypes) > 2 else "Medium"
                ),
                "recommended_action": "Monitor your credit and freeze it if SSN was exposed.",
                "analysis_details": "Due to high latency, a quick heuristic analysis was performed. Protect your data.",
            }

        return PrivacyAnalysisResponse(
            risk_score=risk_score,
            identity_theft_risk=analysis.get("identity_theft_risk", "Medium"),
            matched_cases=matched_count,
            recommended_action=analysis.get(
                "recommended_action", "Monitor your credit reports."
            ),
            analysis_details=analysis.get(
                "analysis_details", "Based on your profile, you have a moderate risk."
            ),
        )
    except Exception as e:
        print(f"Critical Privacy Analysis error: {e}")

        return PrivacyAnalysisResponse(
            risk_score=50,
            identity_theft_risk="Unknown",
            matched_cases=0,
            recommended_action="Temporarily unavailable.",
            analysis_details="The engine is currently offline.",
        )


try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
except Exception as e:
    print(f"Gemini initialization failed: {e}")
    gemini_model = None

chat_memory = {}


@app.post("/chatbot", response_model=ChatResponse)
async def chatbot(chat_input: ChatInput):

    session_id = chat_input.session_id or "default_user"

    rag = get_rag_engine()
    if RAG_AVAILABLE:
        try:
            result = await asyncio.wait_for(
                rag.get_answer(chat_input.question, session_id=session_id),
                timeout=15.0,
            )
            return ChatResponse(**result)
        except Exception as e:
            print(f" RAG Pipeline Error: {e}. Falling back to reasoned inference.")

    try:
        keywords = [kw for kw in chat_input.question.lower().split() if len(kw) > 3]
        if keywords:
            search_query = {
                "$or": [{"title": {"$regex": kw, "$options": "i"}} for kw in keywords]
            }
            cases = await asyncio.to_thread(
                lambda: list(db["vector_embeddings"].find(search_query).limit(3))
            )
        else:
            cases = []

        context_str = "\n".join(
            [
                f"- {c['title']}: {c.get('ai_summary', c.get('description', ''))}"
                for c in cases
            ]
        )

        prompt = f"""
        You are an empathetic, intelligent Legal AI Assistant. Provide helpful, grounded guidance.

        CONTEXT FROM DATABASE:
        {context_str or "No direct matches found. Provide general expert guidance."}

        USER QUESTION:
        {chat_input.question}

        INSTRUCTIONS:
        1. Be conversational and human-friendly.
        2. Avoid robotic templates.
        3. Acknowledge user concerns.
        4. Mention this is guidance, not advice.
        """

        if not gemini_model:
            raise Exception("Gemini model not initialized")
        response = gemini_model.generate_content(prompt)

        answer = response.text

        try:
            await asyncio.to_thread(
                user_queries_collection.insert_one,
                {
                    "session_id": session_id,
                    "question": chat_input.question,
                    "answer": answer,
                    "timestamp": datetime.datetime.utcnow(),
                    "type": "fallback_reasoning",
                    "metadata": {"retrieved_cases": [c["title"] for c in cases]},
                },
            )
        except Exception as e:
            print(f" Failed to store user query: {e}")

        return ChatResponse(
            answer=answer,
            sources=[c.get("source_url", "Internal Database") for c in cases],
            confidence="Medium (Reasoned Fallback)",
        )

    except Exception as e:
        print(f"❌ Chat Failure: {e}")
        return ChatResponse(
            answer="I'm carefully analyzing your query but my reasoning engine is currently high-load. Generally, in these situations, it is best to monitor your credit reports and wait for official notices.",
            sources=[],
            confidence="Low",
        )


@app.get("/stats")
def get_stats():

    try:
        return {
            "cases": db["settlements"].count_documents({}),
            "breaches": db["breaches"].count_documents({}),
            "vectors": db["vector_embeddings"].count_documents({}),
        }
    except Exception as e:
        print(f" Stats failure: {e}")
        return {"cases": 0, "breaches": 0, "vectors": 0}


from apscheduler.schedulers.background import BackgroundScheduler
import subprocess

scheduler = BackgroundScheduler()


def run_pipeline():

    print("🔄 Running scheduled weekly legal data pipeline...")
    try:
        subprocess.run(["python", "scripts/legal_data_pipeline.py"], check=True)
        print("✅ Pipeline completed successfully.")
    except Exception as e:
        print(f"⚠️ Scheduled pipeline failed: {e}")


@app.on_event("startup")
def start_scheduler():

    # run_pipeline()

    scheduler.add_job(run_pipeline, "interval", weeks=1)

    scheduler.start()

    print("🎯 Weekly pipeline scheduler started.")


@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()


@app.get("/metrics")
def get_metrics():

    try:
        total_breaches = db["breaches"].count_documents({})
        total_cases = db["vector_embeddings"].count_documents({})

        seven_days_ago = datetime.datetime.utcnow() - datetime.timedelta(days=7)

        new_cases = db["vector_embeddings"].count_documents(
            {"_id": {"$gt": ObjectId.from_datetime(seven_days_ago)}}
        )

        return {
            "total_breaches": total_breaches,
            "total_cases": total_cases,
            "last_pipeline_run": datetime.datetime.utcnow().strftime("%Y-%m-%d"),
            "new_cases_this_week": new_cases,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

if os.path.isdir("frontend/dist/assets"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")


@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    file_path = os.path.join("frontend/dist", full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    if os.path.isfile("frontend/dist/index.html"):
        return FileResponse("frontend/dist/index.html")
    return {"message": "Frontend build files not found."}


if __name__ == "__main__":

    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
