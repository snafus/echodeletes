from datetime import datetime
from pydantic import BaseModel, validator
from typing import List, Optional, Union

from db import models


class DeletePatch(BaseModel):
    """pydantic schema for a delete request, with optional values"""
    poolname: Union[str,None] = None
    oid:   Union[str,None] = None
    state: Union[models.DeletionState, None] = None
    #state: str



class DeleteRequest(BaseModel):
    """pydantic schema for a delete request"""
    poolname: str
    oid: str
    state: Union[str,models.DeletionState]
    #state: str
    @validator("state", pre=False)
    def conv_state(cls, value):
        """Convert the  string representation of the inputted enum"""
        if type(value) == str:
            return models.DeletionState[value]
        else:
            return value
    # @validator("state", pre=False)
    # def parse_state(cls, value):
    #     """Return the string representation of the enum"""
    #     return value.name

class DeleteId(BaseModel):
    """Respponse after worker has run a delete"""
    id         : int     

class DeleteDone(BaseModel):
    """Respponse after worker has run a delete"""
    id         : int     
    # uuid       : str       
    poolname   : str           
    oid        : str      
    state      : models.DeletionState   
    @validator("state", pre=True)
    def conv_state(cls, value):
        """Convert the  string representation of the inputted enum"""
        if type(value) == str:
            return models.DeletionState[value]
        else:
            return value     

class DeleteDoneList(BaseModel):
    data: List[DeleteDone]



class DeleteOut(DeleteRequest):
    id: str
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    signature: str

    @validator("created_at", pre=False)
    def parse_create_time(cls, value):
        return value.strftime("%Y-%m-%d %T %Z")

    @validator("started_at", pre=False)
    def parse_start_time(cls, value):
        if value is None:
            return "N/A"
        return value.strftime("%Y-%m-%d %T %Z")

    @validator("finished_at", pre=False)
    def parse_finish_time(cls, value):
        if value is None:
            return "N/A"
        return value.strftime("%Y-%m-%d %T %Z")


    @validator("state", pre=False)
    def parse_state(cls, value):
        """Return the string representation of the enum"""
        return value.name

    class Config:
        orm_mode = True
