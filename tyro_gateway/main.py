from fastapi import FastAPI
from tyro_gateway.routers import router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from TYRO Gateway"}

app.include_router(router)
