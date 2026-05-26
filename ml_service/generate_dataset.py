import os
import json
import asyncio
from pymongo import MongoClient
from google import genai
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

client = MongoClient(MONGO_URI)
db = client["legal_ai_db"]
breaches_col = db["breaches"]
dataset_col = db["ml_dataset"]

dataset_col.create_index([("source_url", 1)], unique=True)

PROMPT_TEMPLATE = """
You are an expert legal data labeler for an ML system.
Analyze the following raw data breach case and extract structured features for our ML model.

Case Data:
Title: {title}
Company: {company}
Description: {description}

Extract and estimate the following features:
1. breach_type (categorical: e.g., "Data Breach", "Ransomware", "Phishing", "Insider Threat")
2. data_exposed (list of strings: e.g., ["SSN", "Email", "Credit Card", "Medical Records"])
3. records_affected (numeric: estimate the number of records affected, use 0 if unknown)
4. company_type (categorical: e.g., "Finance", "Healthcare", "Tech", "Retail")
5. jurisdiction (categorical: e.g., "California", "EU", "Federal", "Unknown")
6. time_since_breach (numeric: estimated months since breach, use 12 if unknown)
7. legal_precedent_score (numeric 0.0 to 1.0: 1.0 means highly likely to settle based on precedent)
8. eligibility_label (categorical: strictly one of ["Eligible", "Likely", "Not Eligible"]. Assess based on severity and clear damages.)

Return ONLY a valid JSON object with the exact keys:
breach_type, data_exposed, records_affected, company_type, jurisdiction, time_since_breach, legal_precedent_score, eligibility_label.
"""


async def generate_labels(breach):
    title = breach.get("title") or breach.get("company", "Unknown")
    prompt = PROMPT_TEMPLATE.format(
        title=title,
        company=breach.get("company", "Unknown"),
        description=breach.get("description", ""),
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", contents=prompt
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error labeling {title}: {e}")
        return None


async def main():
    print("🚀 Starting synthetic dataset generation...")
    raw_cases = list(breaches_col.find())
    print(f"Found {len(raw_cases)} raw cases.")

    count = 0
    for breach in raw_cases:
        if dataset_col.find_one({"source_url": breach.get("source_url")}):
            continue

        print(f"Labeling: {breach.get('title') or breach.get('company')}")
        labels = await generate_labels(breach)

        if labels:
            dataset_entry = {**breach, **labels}
            dataset_entry.pop("_id", None)
            try:
                dataset_col.insert_one(dataset_entry)
                count += 1
                print(f"✅ Saved to dataset: {dataset_entry.get('title')}")
            except Exception as e:
                pass

        await asyncio.sleep(1)

    print(f"✨ Dataset generation complete. Added {count} new labeled records.")


if __name__ == "__main__":
    asyncio.run(main())
