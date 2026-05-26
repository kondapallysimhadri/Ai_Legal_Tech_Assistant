from fastapi import APIRouter, HTTPException, Depends
from auth import get_current_user
from pymongo import MongoClient
import os

router = APIRouter(prefix="/compliance", tags=["Compliance"])

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["legal_ai_db"]

@router.delete("/delete-user")
async def right_to_be_forgotten(user: dict = Depends(get_current_user)):

    user_id = user.get("sub")

    res1 = db["predictions"].delete_many({"user_id": user_id})

    res2 = db["feedback"].delete_many({"user_id": user_id})

    res3 = db["users"].delete_one({"_id": user_id})

    return {
        "status": "success",
        "message": "All personal data has been permanently erased.",
        "records_deleted": res1.deleted_count + res2.deleted_count + res3.deleted_count,
    }

@router.get("/export-data")
async def data_portability(user: dict = Depends(get_current_user)):

    user_id = user.get("sub")

    predictions = list(db["predictions"].find({"user_id": user_id}, {"_id": 0}))
    feedback = list(db["feedback"].find({"user_id": user_id}, {"_id": 0}))

    return {
        "user_id": user_id,
        "exported_at": os.popen("date").read().strip(),
        "data": {"predictions": predictions, "feedback": feedback},
        "disclaimer": "This export contains all personal identifiers stored in the AI Legal Assistant system.",
    }

def anonymize_pii(data: dict):

    sensitive_fields = ["name", "email", "phone_number", "ssn_full"]
    for field in sensitive_fields:
        if field in data:
            data[field] = "[ANONYMIZED]"
    return data
