from fastapi import FastAPI
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional, Union

from routers import deletes, metrics, actions
from signing import verify, sign
from db import models
from db.database import engine, get_db
from db.models import DeleteRequest

from dotenv import load_dotenv

load_dotenv()

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(deletes.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")
app.include_router(actions.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"Description": "Deletes for XrdCeph"}
