# 📁 tyro_gateway/routers/tax.py
from fastapi import APIRouter
from tyro_gateway.models.personal_tax import PersonalTaxInput
from tyro_gateway.models.business_tax import BusinessTaxInput
from tyro_gateway.notion_client import create_personal_tax, create_business_tax

router = APIRouter()

# 2.1 Personal Annual Tax Filing Summary
@router.post("/add-personal-tax")
def add_personal_tax(data: PersonalTaxInput):
    status, response = create_personal_tax(data)
    return {"status": status, "response": response}

# 2.2 Business Annual Tax Filing Summary
@router.post("/add-business-tax")
def add_business_tax(data: BusinessTaxInput):
    status, response = create_business_tax(data)
    return {"status": status, "response": response}
