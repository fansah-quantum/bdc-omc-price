from typing import Optional

from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


from models.custom_base import CustomBase



class SampleModel(CustomBase):
    __tablename__ = "samples"


    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
