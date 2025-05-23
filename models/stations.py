from typing import Optional

from sqlalchemy import String, UniqueConstraint

from sqlalchemy.orm import Mapped, Session
from sqlalchemy.orm import mapped_column
from models.custom_base import CustomBase
from typing import List
from sqlalchemy.orm import relationship





class Station(CustomBase):
    __tablename__ = "stations"

    __table_args__ = (
        UniqueConstraint("name", "location", name="uq_station_name_location"),
    )
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    location: Mapped[str] = mapped_column(String, nullable=False)
    price_entries_station: Mapped[List["PriceEntry"]] = relationship("PriceEntry", back_populates="station", lazy="selectin", cascade="all, delete-orphan")





    @classmethod
    def sync_stations(cls, db_session: Session, stations: list) -> None:
        """
        Sync stations with the database.
        If a station (exists) in the database but not in the provided list, it will be deleted.
        If a station(name, location) exists in the provided list but not in the database, it will be added.
        """
        existing_stations = db_session.query(cls).all()
        existing_stations = {(station.name, station.location) for station in existing_stations}
        new_stations = {(station['name'], station['location']) for station in stations}
        for station in existing_stations - new_stations:
            existing_station = db_session.query(cls).filter_by(name=station[0], location=station[1]).first()
            if existing_station:
                if existing_station.deleted_at is not None:
                    existing_station.restore()
                else:
                    existing_station.soft_delete()
        for station in new_stations - existing_stations:
            db_session.add(Station(name=station[0], location=station[1]))
        db_session.commit()
        return {"message": "Stations synced successfully", "status": True}


        for station in stations:
            existing_station = db_session.query(cls).filter_by(name=station['name'], location=station['location']).first()
            if not existing_station:
                new_station = cls(name=station['name'], location=station['location'])
                db_session.add(new_station)
        db_session.commit()
        return db_session.query(cls).all()



    @classmethod
    def get_stations(cls, db_session: Session) -> list:
        """
        Get all stations from the database.
        """
        return db_session.query(cls).filter_by(deleted_at=None).all()
    


    @classmethod
    def get_station_by_id(cls, db_session: Session, station_id: int) -> Optional["Station"]:
        """
        Get a station by its ID.
        """
        return db_session.query(cls).filter_by(id=station_id).first()

        