from typing import List

from fastapi import APIRouter

from controller.stations import StationController
from schemas.stations import StationsOut
from schemas.bdcs import DelMessage




stations_router = APIRouter()

@stations_router.get("/sync/stations", response_model=DelMessage)
async def sync_stations():
    """Sync Stations
    This method syncs the stations
    """
    return StationController.sync_stations()

@stations_router.get("/stations", response_model=List[StationsOut])
async def get_stations():
    """Get all stations
    This method gets all stations
    """
    return StationController.get_stations()



@stations_router.get("/stations/{station_id}", response_model=StationsOut)
async def get_station_by_id(station_id: int):
    """Get station by id
    This method gets a station by id
    """
    return StationController.get_station_by_id(station_id)