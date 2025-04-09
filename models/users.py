from typing import Optional

from sqlalchemy import String

from datetime import datetime, timedelta
from enum import Enum
from typing import List

from sqlalchemy import ForeignKey, DateTime, Boolean
from sqlalchemy.orm import  Mapped, mapped_column, relationship, Session
from sqlalchemy import Enum as SQLAlchemyEnum





from models.custom_base import CustomBase 



class UserType(str, Enum):
    MARKETING_STAFF = "marketing_staff"
    POWER_FUELS_STAFF = "power_fuels_staff"



class User(CustomBase):
    __tablename__ = "users"
    
    email: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    mobile_number: Mapped[Optional[str]] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String)
    profile_image_url: Mapped[Optional[str]] = mapped_column(String)
    user_type: Mapped[UserType] = mapped_column(SQLAlchemyEnum(UserType), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    


    price_entries: Mapped[List["PriceEntry"]] = relationship(back_populates="user", lazy="selectin")
    password_reset_token: Mapped["PasswordResetToken"] = relationship(back_populates="user", uselist=False)

    @staticmethod
    def update_user(db_session: Session, user_id: int, data: dict):
        user = db_session.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        for key, value in data.items():
            setattr(user, key, value)
        db_session.commit()
        db_session.refresh(user)
        return user




class PasswordResetToken(CustomBase):
    __tablename__ = "password_reset_tokens"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    token: Mapped[str] = mapped_column(String, unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    is_used: Mapped[bool] = mapped_column(Boolean, default=False)


    user: Mapped["User"] = relationship(back_populates="password_reset_token")


    @staticmethod
    def create_password_reset_token(db_session: Session, user_id: int, token: str):
        expires_at = datetime.now() + timedelta(minutes=5)
        print(token, "token sent")
        password_reset_token = PasswordResetToken(user_id=user_id, token=token, expires_at=expires_at)
        db_session.add(password_reset_token)
        db_session.commit()
        db_session.refresh(password_reset_token)
        return password_reset_token
    
    @staticmethod
    def verify_user_token(db_session: Session, user_id: int, token: str):
        token = db_session.query(PasswordResetToken).filter(PasswordResetToken.user_id == user_id, PasswordResetToken.token == token).first()
        if token:
            if token.is_used or token.expires_at < datetime.now():
                print("Token already used or expired")
                return None
            token.is_used = True
            db_session.commit()
            return token
        return None
    

    
    