from fastapi import FastAPI
from .routers import api
from .services.db_service import engine
from sqlmodel import SQLModel

app = FastAPI()

SQLModel.metadata.create_all(engine)

app.include_router(api.router)
