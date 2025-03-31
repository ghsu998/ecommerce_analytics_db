from fastapi import APIRouter
from tyro_gateway.notion_client import create_record, query_records
from tyro_gateway.models.personal_tax import PersonalTax
from tyro_gateway.models.business_tax import BusinessTax

router = APIRouter()

# 3.1 Personal Tax - CREATE
@router.post("/add-personal-tax")
def add_personal_tax(data: PersonalTax):
    return create_record("3.1", data.dict())

# 3.2 Business Tax - CREATE
@router.post("/add-business-tax")
def add_business_tax(data: BusinessTax):
    return create_record("3.2", data.dict())

# 3.1 Personal Tax - QUERY
@router.get("/personal-tax")
def list_personal_tax(limit: int = 10):
    return query_records("3.1", page_size=limit)

# 3.2 Business Tax - QUERY
@router.get("/business-tax")
def list_business_tax(limit: int = 10):
    return query_records("3.2", page_size=limit)
