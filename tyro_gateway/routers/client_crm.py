# tyro_gateway/routers/client_crm.py

from fastapi import APIRouter
from tyro_gateway.models.client_crm import ClientCRM
from tyro_gateway.utils.notion_client import create_record, query_records

router = APIRouter()

# 1.2 Client CRM - CREATE
@router.post("/add-client-crm")
def add_client_crm(data: ClientCRM):
    return create_record("1.2", data.dict())

# 1.2 Client CRM - QUERY
@router.get("/client-crm")
def list_client_crm(limit: int = 10):
    return query_records("1.2", page_size=limit)

