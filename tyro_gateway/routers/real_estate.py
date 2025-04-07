# tyro_gateway/routers/investment.py

from fastapi import APIRouter
from tyro_gateway.utils.notion_client import create_record, query_records

from tyro_gateway.models.real_estate import RealEstate

router = APIRouter()

# 4.3 Real Estate - CREATE
@router.post("/add-real-estate")
def add_real_estate(data: RealEstate):
    return create_record("4.3", data.dict())

# 4.3 Real Estate - QUERY
@router.get("/real-estate")
def list_real_estate(limit: int = 10):
    return query_records("4.3", page_size=limit)
