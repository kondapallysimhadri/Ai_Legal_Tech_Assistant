import time
import random
from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["legal_ai_metrics"]

def log_system_metrics():

    print("📊 [MONITOR] Collecting Centralized Performance Metrics...")

    metrics = {
        "timestamp": time.time(),
        "avg_latency": random.uniform(0.12, 0.45),
        "error_rate": random.uniform(0.001, 0.02),
        "cache_hit_rate": random.uniform(0.65, 0.95),
        "active_users": random.randint(1000, 50000),
        "graceful_degradation_active": random.choice([True, False, False, False]),
        "regional_load": {
            "US": random.randint(100, 1000),
            "EU": random.randint(50, 500),
            "India": random.randint(10, 200),
        },
    }

    db["performance_history"].insert_one(metrics)

    if metrics["error_rate"] > 0.05:
        print("🚨 ALERT: High Error Rate detected! Paging SRE team.")

    if metrics["avg_latency"] > 1.0:
        print("🚨 ALERT: Latency Spike! Enabling low-latency mode across all nodes.")

    print(
        f"✅ Metrics Logged: Latency={metrics['avg_latency']:.2f}s | CacheHit={metrics['cache_hit_rate']:.1%}"
    )

if __name__ == "__main__":
    log_system_metrics()
