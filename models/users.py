from typing import Optional

from sqlalchemy import String

from datetime import datetime, timedelta
from typing import List

from sqlalchemy import DateTime
from sqlalchemy.orm import  Mapped, mapped_column, relationship, Session
from utils.common import verify_password


from models.custom_base import CustomBase




class User(CustomBase):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    pin: Mapped[str] = mapped_column(String, nullable=True)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)

    price_entries: Mapped[List["PriceEntry"]] = relationship(back_populates="user", lazy="selectin")



    @staticmethod
    def login_with_email_and_pin(db_session: Session, email: str, pin: str= None, get_user_only: bool = False):
        """
        This method is used to login with email and pin or get only the usr
        """	
        user = db_session.query(User).filter(User.email == email).first()
        if not user:
            return None
        return user if get_user_only else user if pin and verify_password(pin, user.pin) else None
    
    @staticmethod
    def get_user_by_email(db_session: Session, email: str):
        user = db_session.query(User).filter(User.email == email).first()
        return user
    


class AllowedUser(CustomBase):
    __tablename__ = "allowed_users"

    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    company_id: Mapped[Optional[int]] = mapped_column(String, nullable=True)
    company: Mapped["Company"] = relationship(back_populates="allowed_users", lazy="selectin")


    
    