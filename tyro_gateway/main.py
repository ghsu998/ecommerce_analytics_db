from fastapi import FastAPI
from tyro_gateway.routers import router  # <- 確保 routers/__init__.py 存在

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from TYRO Gateway"}

app.include_router(router)
