from typing import Any, Dict, List, Optional
import os
from datetime import datetime
from pymongo import MongoClient

DATABASE_URL = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "app_db")

client = MongoClient(DATABASE_URL)
db = client[DATABASE_NAME]


def _with_timestamps(data: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.utcnow()
    return {**data, "created_at": now, "updated_at": now}


def create_document(collection_name: str, data: Dict[str, Any]) -> str:
    coll = db[collection_name]
    res = coll.insert_one(_with_timestamps(data))
    return str(res.inserted_id)


def get_documents(collection_name: str, filter_dict: Optional[Dict[str, Any]] = None, limit: int = 50) -> List[Dict[str, Any]]:
    coll = db[collection_name]
    cursor = coll.find(filter_dict or {}).limit(limit)
    docs: List[Dict[str, Any]] = []
    for d in cursor:
        d["_id"] = str(d["_id"])  # stringify ObjectId
        docs.append(d)
    return docs
