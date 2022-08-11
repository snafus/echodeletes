from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from collections import Counter

from sqlalchemy.orm import Session
from typing import List, Optional, Union

from db import models 
from db.database import get_db
# import schemas

router = APIRouter(
    prefix="/metrics",
    tags=['Metrics']
)

@router.get("/ping")
def ping():
    return {'data':'pong'}


@router.get("")
def get_state(db: Session = Depends(get_db)):
    q = db.query(models.DeleteRequest).all()

    c_states       = Counter(x.state.name for x in q)
    c_pool         = Counter(x.poolname for x in q)
    c_pool_states  = Counter(f'{x.poolname}_{x.state.name}' for x in q)

    print(c_states,c_pool,c_pool_states, sep='\n' )
    return {'c_states':c_states, 'c_pool':c_pool, 'c_pool_states':c_pool_states }

