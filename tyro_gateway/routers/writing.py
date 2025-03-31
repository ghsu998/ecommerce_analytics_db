from fastapi import APIRouter
from notion_client import create_record
from models.writing import EmailIdentity
from models.writing import ClientCrm

router = APIRouter()

@router.post("/add-email-identity")
def add_email_identity(data: EmailIdentity):
    return create_record("1.1", data.dict())

@router.post("/add-client-crm")
def add_client_crm(data: ClientCrm):
    return create_record("1.2", data.dict())

