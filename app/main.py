from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import api, storage
from .services.db_service import engine
from sqlmodel import SQLModel
from .config import Settings

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SQLModel.metadata.create_all(engine)

app.include_router(api.router)
app.include_router(storage.router)
