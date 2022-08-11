import schemas
import uuid 

from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional, Union

from db import models 
from db.database import get_db

from asyncio import Lock

from signing import verify, sign


router = APIRouter(
    prefix="/deletes",
    tags=['Deletes']
)


@router.get("", response_model=List[schemas.DeleteOut])
def get_deletes(db: Session = Depends(get_db),
                limit: Union[int, None] = None,
                offset: Union[int, None] = None,
                poolname: Optional[str] = "",
                state: Optional[str] = models.DeletionState.Set,
                ):
    requests = db.query(models.DeleteRequest).\
                        filter(models.DeleteRequest.poolname.contains(poolname)).\
                        filter(models.DeleteRequest.state == state).\
                        limit(limit).offset(offset).all()
    return requests

@router.get("{item_id}", response_model=schemas.DeleteOut)
def read_item(item_id: int, db: Session = Depends(get_db),):

    request = db.query(models.DeleteRequest).filter(models.DeleteRequest.id == item_id).one_or_none()
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail='Id {:d} not foud'.format(item_id) )

    return request

@router.post("", status_code=status.HTTP_201_CREATED, response_model=schemas.DeleteOut)
async def create_deletes(request: schemas.DeleteRequest, db: Session = Depends(get_db)):
    uuid_raw = uuid.uuid4()
    uuid_hex = uuid_raw.hex
    uuid_b = uuid_raw.bytes

    message = "{}:{}".format(request.poolname, request.oid)
    # await asyncio.sleep(1)
    sig = sign(message.encode('utf8'),uuid_b)
    # print('sign', sig, uuid_hex, uuid_b)
    request = models.DeleteRequest(**request.dict(), 
                                   uuid=uuid_hex,
                                   signature=sig.decode('utf8') )
    db.add(request)
    db.commit()
    db.refresh(request)

    return request

@router.delete("{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(item_id: int, db: Session = Depends(get_db),):

    request_query  = db.query(models.DeleteRequest).filter(models.DeleteRequest.id == item_id)

    if request_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail='Id {:d} not foud'.format(item_id) )

    # any other authorisations?
    request_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


process_deletes_lock = Lock()

@router.patch("{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_deletes(item_id: int, update_request: schemas.DeletePatch, db: Session = Depends(get_db) ):
    # async with process_deletes_lock:
    request_query  = db.query(models.DeleteRequest).filter(models.DeleteRequest.id == item_id)
    request = request_query.first()
    if request is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail='Id {:d} not foud'.format(item_id) )

    # if requests.state == models.DeletionState.Started:
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT,
    #                      detail='Id {:d} not in state Set'.format(item_id) )
    # for req in requests:
    #     req.state = models.DeletionState.Started
    #     req.started_at = datetime.utcnow()
    # await asyncio.sleep(3)        
    # request_query.update({'state':mdels.DeletionState.Started, 'started_at':datetime.utcnow()})

    update_items = update_request.dict(exclude_unset=True)
    request_query.update(update_items, synchronize_session=False)
    db.commit()
    # db.refresh(request)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

