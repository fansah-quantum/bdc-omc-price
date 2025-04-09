from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

class SampleSchemaIn(BaseModel):

    """Sample Schema
    This is a sample schema to show how to create a schema
    """

    name: str  = Field(..., title="Name", description="Name of the sample", examples=["sample1", "sample2"])
    description: str  = Field(..., title="Description", description="Description of the sample", examples=["description1", "description2"])


class SampleSchemaOut(BaseModel):
        """Sample Schema
        Each schema should possiblly have a response schema
        """
        name: str
        description: str
        id: int
        created_at: datetime
        updated_at: datetime
        deleted_at: Optional[datetime]

        class Config:
            from_attriubte = True
    



