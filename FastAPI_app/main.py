from fastapi import FastAPI
from typing import List, Dict
from pydantic import BaseModel
from database import get_database
import uvicorn
from datetime import datetime


app = FastAPI()

db = get_database()
collection = db['mqtt_data']

class ProductAddRequest(BaseModel):
    startTime: str
    endTime: str

class StatusCount(BaseModel):
    status: int
    count: int


@app.post("/getdata", response_model=List[StatusCount])
async def get_data(request: ProductAddRequest):
    start_time = datetime.strptime(request.startTime, "%d-%m-%Y %H:%M:%S")
    end_time = datetime.strptime(request.endTime, "%d-%m-%Y %H:%M:%S")

    pipeline = [
        {"$match": {"timeStamp": {"$gte": start_time, "$lte": end_time}}},
        {"$group": {"_id": "$data.status","count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]

    documents = collection.aggregate(pipeline)
    results = [{'status': doc['_id'], 'count': doc['count']} for doc in documents]
    return results


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host = "0.0.0.0",
        port = 8000,
        reload=True
        )