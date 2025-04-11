from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import api
from .services.db_service import engine
from sqlmodel import SQLModel

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
