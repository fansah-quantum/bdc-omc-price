from pydantic import BaseModel, Field
from datetime import datetime



class BDCIn(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)



class OMCIn(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)



class BDCOMCOut(BaseModel):
    id: int
    name: str
    created_at: datetime

class BDCOMCAllOut(BaseModel):
    bdcs: list[BDCOMCOut]
    omcs: list[BDCOMCOut]
    