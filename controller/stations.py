import requests
import json

from fastapi.exceptions import HTTPException
from models.stations import Station
from utils.session import CreateDBSession

from config.setting import settings



STATIONS_URL = settings.STATIONS_SYNC_URL

class StationController:

    @staticmethod
    def sync_stations():
        """Sync Stations
        This method syncs the stations
        """
        headers = {
            "Content-Type": "application/json",
            "API-KEY": settings.STATIONS_API_KEY,
        }
        response = requests.get(STATIONS_URL, headers=headers)
        if response.status_code == 200:
            stations = response.json()
            with CreateDBSession() as db_session:
                stations = list({json.dumps(d, sort_keys=True) for d in stations}) 
                stations = [json.loads(d) for d in stations]	 
                sync_stations = Station.sync_stations(db_session,stations)
                return sync_stations
        raise HTTPException(
            status_code=response.status_code,
            detail=f"Error syncing stations: {response.text}"
        )


    @staticmethod
    def get_stations():
        """Get all stations
        This method gets all stations
        """
        with CreateDBSession() as db_session:
            stations = Station.get_stations(db_session)
            return stations

    @staticmethod
    def get_station_by_id(station_id: int):
        """Get station by id
        This method gets a station by id
        """
        with CreateDBSession() as db_session:
            station = Station.get_station_by_id(db_session, station_id)
            if not station:
                raise HTTPException(status_code=404, detail="Station not found")
            return station
        