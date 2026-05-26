import requests
import json

def test_claim_submission():
    url = "http://localhost:8000/submit-claim"
    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "phone": "1234567890",
        "email": "john.doe@example.com",
        "address": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip": "10001",
        "country": "USA",
        "affected": True,
        "notification_method": "Email",
        "relationship": "Customer",
        "consent": True,
        "problem_description": "My data was leaked in the 2026 breach.",
        "case_id": "test-case-123"
    }

    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_claim_submission()
