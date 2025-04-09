from typing import List

from fastapi import APIRouter

from schemas.sample_schema import SampleSchemaOut, SampleSchemaIn
from controller.sample_controller import SampleController

"""Sample Router
This module contains a sample router.
Create a new router designated for a specific purpose and register it in the core/start_app.py
This way, you can keep your code organized and easy to maintain.
"""


sample_router = APIRouter()

@sample_router.get("/sample", response_model=List[SampleSchemaOut])
async def get_sample():
    """Get Sample
    This method returns a sample response
    """
    return SampleController.get_sample()
    

@sample_router.post("/sample", response_model=SampleSchemaOut)
async def create_sample(sample: SampleSchemaIn):
    """Create Sample
    This method creates a sample response
    """
    sample = SampleController.create_sample(sample)
    return sample

