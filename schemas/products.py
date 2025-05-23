from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Product(BaseModel):
    id: int
    name: str
    deleted_at: Optional[datetime]= None


class ProductIn(BaseModel):
    name: str 