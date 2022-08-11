import asyncio
import schemas

from datetime import datetime

from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List, Optional, Union

from db.database import get_db
from db import models 
# from signing import verify, sign



router = APIRouter(
    prefix="/actions",
    tags=['Actions']
)

@router.post("/prepare", status_code=status.HTTP_200_OK )
async def prepare_deletes(db: Session = Depends(get_db),
                limit: Union[int, None] = None,
                offset: Union[int, None] = None,
                poolname: Optional[str] = "",
                state: Optional[models.DeletionState] = models.DeletionState.Set,
                ):
    # lock this part to ensure no contention over the list 
    update_items = {'state': models.DeletionState.Started,
                    'started_at': datetime.utcnow() }

    #async with process_deletes_lock:
    try:
        request_ids = [x[0] for x in db.query(models.DeleteRequest.id).\
                        filter(models.DeleteRequest.poolname.contains(poolname)).\
                        filter(models.DeleteRequest.state == models.DeletionState.Set).\
                        limit(limit).offset(offset).\
                        with_for_update(skip_locked=True,nowait=False).all()
                      ]
        print(request_ids)
        request_query = db.query(models.DeleteRequest).\
                        filter(models.DeleteRequest.id.in_(request_ids))
        request_query.update(update_items, synchronize_session=False)
        print(request_query)
        await asyncio.sleep(3)   # sleep testing 
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.commit()

    prepared_requests = request_query.all()
    return {'len':len(request_ids),'ids':request_ids,'data':prepared_requests}

@router.post("/abort_prepares", status_code=status.HTTP_204_NO_CONTENT )
def abort_prepares(data: List[schemas.DeleteId], db: Session = Depends(get_db)):
    print(data)
    # reset the current state
    update_items = {'state': models.DeletionState.Set,
                    'started_at': None,
                    'finished_at': None }

    request_query = db.query(models.DeleteRequest).\
                    filter(models.DeleteRequest.id.in_([x.id for x in data]))


    request_query.update(update_items, synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/set_terminal_states", status_code=status.HTTP_204_NO_CONTENT)
def terminal_deletes(data: List[schemas.DeleteDone] , db: Session = Depends(get_db)):
    dt_now = datetime.utcnow()

    # done items
    done_ids = [x.id for x in data if x.state == models.DeletionState.Done]
    # failed items
    failed_ids = [x.id for x in data if x.state == models.DeletionState.Failed]

    rq = db.query(models.DeleteRequest).\
        filter(models.DeleteRequest.id.in_( (x for x in done_ids)  ))
    rq.update({'state':models.DeletionState.Done, 'finished_at': dt_now},
                synchronize_session=False)

    rq2 = db.query(models.DeleteRequest).\
        filter(models.DeleteRequest.id.in_( (x for x in failed_ids)  ))
    rq2.update({'state':models.DeletionState.Failed, 'finished_at': dt_now},
                synchronize_session=False)
    
    # finally commit the updates
    db.commit()
    #TODO other states ? 
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/set_done", status_code=status.HTTP_204_NO_CONTENT)
def terminal_deletes(data: List[schemas.DeleteDone] , db: Session = Depends(get_db)):
    dt_now = datetime.utcnow()

    # done items
    done_ids = [x.id for x in data if x.state == models.DeletionState.Done]
    rq = db.query(models.DeleteRequest).\
        filter(models.DeleteRequest.id.in_( (x for x in done_ids)  ))
    rq.update({'state':models.DeletionState.Done, 'finished_at': dt_now},
                synchronize_session=False)
    # finally commit the updates
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/set_failed", status_code=status.HTTP_204_NO_CONTENT)
def terminal_deletes(data: List[schemas.DeleteDone] , db: Session = Depends(get_db)):
    dt_now = datetime.utcnow()

    # failed items
    failed_ids = [x.id for x in data if x.state == models.DeletionState.Failed]
    rq2 = db.query(models.DeleteRequest).\
        filter(models.DeleteRequest.id.in_( (x for x in failed_ids)  ))
    rq2.update({'state':models.DeletionState.Failed, 'finished_at': dt_now},
                synchronize_session=False)
    # finally commit the updates
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

