from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Customer Financial Summary"
)

app.include_router(router)