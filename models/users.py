from typing import Optional

from sqlalchemy import String, Integer

from typing import List

from sqlalchemy import  ForeignKey
from sqlalchemy.orm import  Mapped, mapped_column, relationship
from utils.session import CreateDBSession
from utils.common import get_password_hash




from models.custom_base import CustomBase



class User(CustomBase):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    company_id: Mapped[int] = mapped_column(Integer, ForeignKey("companies.id"))
    company: Mapped["Company"] = relationship("Company", back_populates="allowed_users", lazy="selectin", uselist=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    price_entries: Mapped[List["PriceEntry"]] = relationship(back_populates="user", lazy="selectin")



    @staticmethod
    def get_user_by_email( email: str):
        with CreateDBSession() as db_session:
            user = db_session.query(User).filter(User.email == email).first()
            return user
        

    def config_url(self) -> dict:
        """Get the configuration URL for the user

        :return: The configuration URL
        :rtype: dict
        """
        return {
            "api_key": self.company.api_key,
            "api_user": self.company.api_user,
            "api_endpoint": self.company.api_endpoint,
        }
        




class SystemAdmin(CustomBase):
    __tablename__ = "system_admins"

    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=False)




    @staticmethod
    def add_system_admin(id: int, email: str, name: str, password: str) -> "SystemAdmin":
        with CreateDBSession() as db_session:
            system_admin = SystemAdmin(id=id ,email=email, name=name, password=get_password_hash(password))
            db_session.add(system_admin)
            db_session.commit()
            return system_admin
        
    @staticmethod
    def get_system_admin_by_email(email: str) -> Optional["SystemAdmin"]:
        with CreateDBSession() as db_session:
            system_admin = db_session.query(SystemAdmin).filter(SystemAdmin.email == email).first()
            return system_admin
        


    
    