import asyncio
import feedparser
from bs4 import BeautifulSoup
from pymongo import MongoClient, UpdateOne
from datetime import datetime
import os
import json
import subprocess
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["legal_ai_db"]

db.breaches.create_index([("title", 1), ("source_url", 1)], unique=True)
db.cases.create_index([("title", 1), ("source_url", 1)], unique=True)

TARGET_RECORDS = 1500


class RSSLegalDataScraper:

    def __init__(self):
        self.records_collected = db.breaches.count_documents({})
        self.feeds = [
            "https://www.law360.com/rss/classaction",
            "https://www.lexblog.com/feed/",
            "https://feeds.feedburner.com/TheHackersNews",
            "https://www.bleepingcomputer.com/feed/",
            "https://krebsonsecurity.com/feed/",
            "https://www.securityweek.com/feed/",
            "https://threatpost.com/feed/",
            "https://www.darkreading.com/rss.xml",
            "https://www.csoonline.com/feed/",
            "https://www.jdsupra.com/resources/syndication/docsRSSfeed.aspx?so=date",
        ]

    def clean_html(self, html_text):
        if not html_text:
            return ""
        soup = BeautifulSoup(html_text, "html.parser")
        return soup.get_text(separator=" ", strip=True)

    def parse_feed_sync(self, feed_url):
        print(f"📡 Parsing feed: {feed_url}")
        try:
            feed = feedparser.parse(feed_url)
            records = []

            for entry in feed.entries:
                title = entry.get("title", "")
                link = entry.get("link", "")
                description_html = entry.get("description", entry.get("summary", ""))
                description = self.clean_html(description_html)
                date_str = entry.get("published", datetime.utcnow().isoformat())

                if len(title) > 10 and len(description) > 20:
                    records.append(
                        {
                            "title": title.strip(),
                            "company": "Unknown",
                            "source": feed.feed.get("title", "RSS Feed"),
                            "source_url": link,
                            "date": date_str,
                            "full_description": description.strip(),
                            "created_at": datetime.utcnow(),
                        }
                    )
            return records
        except Exception as e:
            print(f"⚠️ Failed to parse {feed_url}: {e}")
            return []

    async def run_async(self):
        print(
            f"🚀 Starting Async RSS Scraper Pipeline. Target: {TARGET_RECORDS} records."
        )

        tasks = [asyncio.to_thread(self.parse_feed_sync, feed) for feed in self.feeds]
        results = await asyncio.gather(*tasks)

        all_records = []
        for records in results:
            all_records.extend(records)

        if all_records:
            operations = [
                UpdateOne(
                    {"title": r["title"], "source_url": r["source_url"]},
                    {"$setOnInsert": r},
                    upsert=True,
                )
                for r in all_records
            ]
            try:
                result = db.breaches.bulk_write(operations, ordered=False)
                new_inserts = result.upserted_count
                self.records_collected += new_inserts
                print(
                    f"✅ Inserted {new_inserts} new records. Total: {self.records_collected}"
                )
            except Exception as e:
                print(f"⚠️ Bulk write failed: {e}")

        print("🏁 RSS Scraping complete.")


class EnrichedData(BaseModel):
    case_type: str | None
    jurisdiction: str | None
    compensation_amount: str | None
    deadline: str | None
    eligibility_issue: bool
    documentation_issue: bool
    complexity_level: str | None
    transparency_issue: bool
    delay_issue: bool
    fairness_issue: bool
    severity_score: int | None
    records_affected: int | None
    data_exposed: str | None
    summary: str | None


class AIEnricher:

    def __init__(self):
        self.gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))

    def enrich_record(self, record):
        prompt = f"""
        Analyze the following legal/data breach text and extract the required fields.
        Text: "{record.get('title')} - {record.get('full_description')}"
        """
        try:
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=EnrichedData,
                    temperature=0.1,
                ),
            )
            extracted_data = json.loads(response.text)

            enriched_record = {**record, **extracted_data}
            enriched_record["is_enriched"] = True
            if "_id" in enriched_record:
                del enriched_record["_id"]

            return enriched_record
        except Exception as e:
            return None

    def run_batch_enrichment(self, limit=500):
        print(f"🧠 Starting AI Enrichment Batch Process (Limit: {limit})...")
        raw_records = list(db.breaches.find({}).sort("_id", -1).limit(limit))

        enriched_count = 0
        for record in raw_records:
            if db.cases.find_one(
                {"title": record["title"], "source_url": record["source_url"]}
            ):
                continue

            enriched = self.enrich_record(record)
            if enriched:
                db.cases.insert_one(enriched)
                enriched_count += 1
                if enriched_count % 10 == 0:
                    print(f"✅ Enriched {enriched_count} records...")

        print(f"🏁 Enrichment complete. Total new cases enriched: {enriched_count}")


def sync_mongodb_vectors():

    print("🔄 Synchronizing MongoDB Vectors...")
    try:
        subprocess.run(["./venv_new/bin/python", "rag/data_ingestion.py"], check=True)
        print("✅ MongoDB Vector Sync Complete.")
    except Exception as e:
        print(f"⚠️ Vector Sync failed: {e}")


def run_claimdepot_scraper():

    print("🔄 Running ClaimDepot Deep Scraper...")
    try:
        subprocess.run(["./venv_new/bin/python", "scraper.py"], check=True)
        print("✅ ClaimDepot Scraper Complete.")
    except Exception as e:
        print(f"⚠️ ClaimDepot Scraper failed: {e}")


if __name__ == "__main__":
    import sys

    if "--scrape-only" in sys.argv:
        asyncio.run(RSSLegalDataScraper().run_async())
    elif "--enrich-only" in sys.argv:
        AIEnricher().run_batch_enrichment(limit=200)
    elif "--sync-only" in sys.argv:
        sync_mongodb_vectors()
    elif "--claimdepot" in sys.argv:
        run_claimdepot_scraper()
    else:
        print("🚀 Running FULL Legal Intelligence Pipeline...")

        run_claimdepot_scraper()

        asyncio.run(RSSLegalDataScraper().run_async())

        AIEnricher().run_batch_enrichment(limit=300)

        sync_mongodb_vectors()
        print("🏁 Full Pipeline Execution Finished.")
