from typing import Optional

from sqlalchemy import String

from sqlalchemy.orm import Mapped, Session
from sqlalchemy.orm import mapped_column

from models.custom_base import CustomBase



class Product(CustomBase):
    __tablename__ = "products"
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)




    @classmethod
    def sync_products(cls, db_session: Session, products: list) -> None:
        """
        Sync products with the database.
        If a product exists in the database but not in the provided list, it will be deleted.
        If a product exists in the provided list but not in the database, it will be added.
        """
        for product in products:
            existing_product = db_session.query(cls).filter_by(name=product['name']).first()
            if not existing_product:
                new_product = cls(name=product['name'])
                db_session.add(new_product)
        db_session.commit()
        return db_session.query(cls).all()
    

    @classmethod
    def get_products(cls, db_session: Session) -> list:
        """
        Get all products from the database.
        """
        return db_session.query(cls).all()
    

    @classmethod
    def get_product_by_id(cls, db_session: Session, product_id: int) -> Optional["Product"]:
        """
        Get a product by its ID.
        """
        return db_session.query(cls).filter_by(id=product_id).first()


    
    




