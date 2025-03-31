from fastapi import APIRouter
from tyro_gateway.notion_client import create_record
from tyro_gateway.models.email_identity import EmailIdentity
from tyro_gateway.models.client_crm import ClientCRM

router = APIRouter()

@router.post("/add-email-identity")
def add_email_identity(data: EmailIdentity):
    return create_record("1.1", data.dict())

@router.post("/add-client-crm")
def add_client_crm(data: ClientCRM):
    return create_record("1.2", data.dict())