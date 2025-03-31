from fastapi import APIRouter
from tyro_gateway.notion_client import create_record
from tyro_gateway.models.personal_tax import PersonalTax
from tyro_gateway.models.business_tax import BusinessTax

router = APIRouter()

@router.post("/add-personal-tax")
def add_personal_tax(data: PersonalTax):
    return create_record("3.1", data.dict())

@router.post("/add-business-tax")
def add_business_tax(data: BusinessTax):
    return create_record("3.2", data.dict())