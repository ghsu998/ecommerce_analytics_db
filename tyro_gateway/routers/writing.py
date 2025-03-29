# 📁 tyro_gateway/routers/writing.py
from fastapi import APIRouter
from tyro_gateway.models.email_identity import EmailIdentityInput
from tyro_gateway.models.client_crm import ClientCRMInput
from tyro_gateway.notion_client import create_email_identity, create_client_crm

router = APIRouter()

# 4.1 Email Identity DB
@router.post("/add-email-identity")
def add_email_identity(data: EmailIdentityInput):
    status, response = create_email_identity(data)
    return {"status": status, "response": response}

# 4.2 Client CRM DB
@router.post("/add-client-crm")
def add_client_crm(data: ClientCRMInput):
    status, response = create_client_crm(data)
    return {"status": status, "response": response}
