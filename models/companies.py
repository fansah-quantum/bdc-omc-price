from typing import Optional, List

from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship





from models.custom_base import CustomBase



class Company(CustomBase):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    
    allowed_users: Mapped[List["AllowedUser"]] = relationship(back_populates="company", lazy="selectin")






class Configuration(CustomBase):
    __tablename__ = "configurations"

    company_id: Mapped[int] = mapped_column(String, nullable=False)
    company: Mapped["Company"] = relationship(back_populates="configuration", lazy="selectin")
    api_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    api_user: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    api_endpoint: Mapped[str] = mapped_column(String, nullable=False, unique=True)
