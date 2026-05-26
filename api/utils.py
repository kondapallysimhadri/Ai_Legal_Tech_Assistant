import os
import logging
import time
from functools import wraps
from fastapi import Request

os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/api.log"),
        logging.StreamHandler()
    ],
)

logger = logging.getLogger("ML_API")

def log_prediction(request_data, prediction, confidence):

    logger.info(
        f"Prediction made | Input: {request_data} | Result: {prediction} | Confidence: {confidence:.2f}"
    )

def detect_drift(current_input: dict):

    if current_input.get("records_affected", 0) > 50000000:
        logger.warning(
            f"⚠️ POTENTIAL DATA DRIFT: records_affected ({current_input['records_affected']}) is outside normal training bounds."
        )
        return True
    return False

async def log_requests(request: Request, call_next):

    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    response.headers["X-Process-Time"] = str(process_time)

    logger.info(
        f"Request: {request.method} {request.url.path} | Status: {response.status_code} | Time: {process_time:.4f}s"
    )

    return response
