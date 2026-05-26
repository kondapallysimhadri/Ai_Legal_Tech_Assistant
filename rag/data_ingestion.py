import os
import datetime
import logging
from pymongo import MongoClient, UpdateOne
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import numpy as np

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/legal_ai_db")
client = MongoClient(MONGO_URI)
db = client.get_database()

logger = logging.getLogger("VectorPipeline")
logging.basicConfig(level=logging.INFO)


class LocalVectorPipeline:
    def __init__(self):
        print("🧠 Loading local embedding model (all-MiniLM-L6-v2)...")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.vector_collection = db["vector_embeddings"]

        self.vector_collection.create_index([("source_url", 1)], unique=True)

    def sync_vectors(self):

        source_collections = ["settlements", "breaches"]

        total_synced = 0
        for coll_name in source_collections:
            if coll_name not in db.list_collection_names():
                continue

            records = list(
                db[coll_name].find({"vector_synced": {"$ne": True}}).limit(15)
            )
            print(f"📦 Found {len(records)} new records in '{coll_name}' to vectorize.")

            for doc in records:
                title = doc.get("title", "Untitled")
                content = doc.get(
                    "content", doc.get("full_description", doc.get("summary", ""))
                )
                source_url = doc.get("source_url")

                if not content:
                    continue

                embedding = self.model.encode(f"{title}\n{content[:500]}").tolist()

                vector_doc = {
                    "source_id": doc["_id"],
                    "source_collection": coll_name,
                    "title": title,
                    "source_url": source_url,
                    "content_preview": content[:1000],
                    "embedding": embedding,
                    "created_at": datetime.datetime.utcnow(),
                    "metadata": {
                        "risk_level": doc.get("risk_level", "Medium"),
                        "source": doc.get("source", "Unknown"),
                    },
                }

                self.vector_collection.update_one(
                    {"source_url": source_url}, {"$set": vector_doc}, upsert=True
                )

                db[coll_name].update_one(
                    {"_id": doc["_id"]}, {"$set": {"vector_synced": True}}
                )
                total_synced += 1

                if total_synced % 10 == 0:
                    print(f"✅ Synced {total_synced} vectors...")

        print(f"🏁 Universal Local Vector Sync Finished. Total: {total_synced}")


if __name__ == "__main__":
    import logging

    pipeline = LocalVectorPipeline()
    pipeline.sync_vectors()
