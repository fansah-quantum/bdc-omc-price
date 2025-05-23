from pydantic import BaseModel, Field

class StationsOut(BaseModel): 
    name: str 
    location: str
    id: int