from fastapi import APIRouter
from notion_client import create_record
from models.tax import PersonalTax
from models.tax import BusinessTax

router = APIRouter()

@router.post("/add-personal-tax")
def add_personal_tax(data: PersonalTax):
    return create_record("3.1", data.dict())

@router.post("/add-business-tax")
def add_business_tax(data: BusinessTax):
    return create_record("3.2", data.dict())

