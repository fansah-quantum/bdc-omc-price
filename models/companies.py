from typing import Optional, List

from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Session

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship





from models.custom_base import CustomBase



class Company(CustomBase):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    allowed_users: Mapped[List["User"]] = relationship("User", back_populates="company", lazy="selectin", cascade="all, delete-orphan")
    api_key: Mapped[str] = mapped_column(String)
    api_user: Mapped[str] = mapped_column(String)
    api_endpoint: Mapped[str] = mapped_column(String, nullable=False, unique=True)



    

  




