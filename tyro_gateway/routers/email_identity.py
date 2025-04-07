# tyro_gateway/routers/writing.py

from fastapi import APIRouter
from tyro_gateway.utils.notion_client import create_record, query_records
from tyro_gateway.models.email_identity import EmailIdentity


router = APIRouter()

# 1.1 Email Identity - CREATE
@router.post("/add-email-identity")
def add_email_identity(data: EmailIdentity):
    return create_record("1.1", data.dict())

# 1.1 Email Identity - QUERY
@router.get("/email-identities")
def list_email_identities(limit: int = 10):
    return query_records("1.1", page_size=limit)


