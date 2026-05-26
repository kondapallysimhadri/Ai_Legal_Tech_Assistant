import requests
import time

def test(name, url, method="GET", data=None):
    print(f"\nTesting {name} ({url})...")
    t1 = time.time()
    try:
        if method == "GET":
            res = requests.get(url)
        else:
            res = requests.post(url, json=data)
        print(f"Status: {res.status_code}, Time: {time.time()-t1:.2f}s")
        print(f"Response: {str(res.json())[:500]}...")
    except Exception as e:
        print(f"FAILED: {e}")

test("Cases", "http://localhost:8000/cases")
test("Stats", "http://localhost:8000/stats")
test("Predict", "http://localhost:8000/predict", "POST", {
    "breach_type": "finance",
    "data_exposed": "SSN",
    "records_affected": 500000,
    "company_type": "bank",
    "jurisdiction": "US",
    "time_since_breach": 30,
    "user_impact_level": "high",
    "past_case_similarity_score": 0.85
})
test("Privacy", "http://localhost:8000/api/privacy/analyze", "POST", {
  "name": "John Doe",
  "location": "California",
  "employment": "Software Engineer",
  "dataTypes": ["SSN", "Email"],
  "financialLoss": True
})
test("Chatbot", "http://localhost:8000/chatbot", "POST", {
    "question": "What are my legal rights if my SSN is leaked?",
    "history": [],
    "jurisdiction": "Global"
})
