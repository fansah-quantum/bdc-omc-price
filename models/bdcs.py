from typing import Optional

from sqlalchemy import String

from sqlalchemy.orm import Mapped, Session
from sqlalchemy.orm import mapped_column
from datetime import datetime
from enum import Enum
from typing import List, Literal



from sqlalchemy import ForeignKey, Float, DateTime, Boolean, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLAlchemyEnum




from models.custom_base import CustomBase




class BDC(CustomBase):
    __tablename__ = "bdcs"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    price_entries: Mapped[List["PriceEntry"]] = relationship(back_populates="bdc")


    @staticmethod
    def add_bdc(db_session: Session, name: str):
        bdc = BDC(name=name)
        db_session.add(bdc)
        db_session.commit()
        db_session.refresh(bdc)
        return bdc


class OMC(CustomBase):
    __tablename__ = "omcs"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    price_entries: Mapped[List["PriceEntry"]] = relationship(back_populates="omc")

    @staticmethod
    def add_omc(db_session: Session, name: str):
        omc = OMC(name=name)
        db_session.add(omc)
        db_session.commit()
        db_session.refresh(omc)
        return omc
    





class ProductType(str, Enum):
    PETROL = "petrol"
    DIESEL = "diesel"
    LPG = "lpg"
    OTHER = "other"

class SellerType(str, Enum):
    BDC = "bdc"
    OMC = "omc"

class WindowType(str, Enum):
    FIRST_WINDOW = "1st_window"
    SECOND_WINDOW = "2nd_window"

class TransactionTerm(str, Enum):
    CASH = "cash"
    CREDIT = "credit"




class PriceEntry(CustomBase):
    __tablename__ = "price_entries"
    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    seller_type: Mapped[SellerType] = mapped_column(SQLAlchemyEnum(SellerType), nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    window: Mapped[WindowType] = mapped_column(SQLAlchemyEnum(WindowType), nullable=False)
    
    omc_id: Mapped[Optional[int]] = mapped_column(ForeignKey("omcs.id"))
    station_location: Mapped[Optional[str]] = mapped_column(String)
    
    # BDC specific fields
    bdc_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bdcs.id"))
    town_of_loading: Mapped[Optional[str]] = mapped_column(String)
    transaction_term: Mapped[Optional[TransactionTerm]] = mapped_column(SQLAlchemyEnum(TransactionTerm))
    
    
    user: Mapped["User"] = relationship(back_populates="price_entries", lazy="selectin")
    omc: Mapped[Optional["OMC"]] = relationship(back_populates="price_entries", lazy="selectin")
    bdc: Mapped[Optional["BDC"]] = relationship(back_populates="price_entries", lazy="selectin")
    product_price: Mapped["ProductPrice"] = relationship(back_populates="price_entry", lazy="selectin")
    images: Mapped[List["PriceEntryImage"]] = relationship(back_populates="price_entry", lazy="selectin")
    sync_status: Mapped[bool] = mapped_column(Boolean, default=False)



    @staticmethod
    def add_omc_price_entry(db_session: Session, user_id: int, omc_id: int, window: WindowType, product: dict,  station_location: str, images: Optional[List[str]]):
        price_entry = PriceEntry(seller_type= "omc", user_id=user_id, omc_id=omc_id, window=window, station_location=station_location)
        db_session.add(price_entry)
        db_session.flush()
        ProductPrice.add_product_price(db_session, price_entry.id, product)
        PriceEntryImage.add_images(db_session, price_entry.id, images)
        db_session.commit()
        db_session.refresh(price_entry)
        return price_entry
    
    @staticmethod
    def add_bdc_price_entry(db_session: Session, user_id: int, bdc_id: int, window: WindowType, product: dict, town_of_loading: str, transaction_term: TransactionTerm, images: Optional[List[str]]):
        price_entry = PriceEntry(seller_type= "bdc", user_id=user_id, bdc_id=bdc_id, window=window, town_of_loading=town_of_loading, transaction_term=transaction_term)
        db_session.add(price_entry)
        db_session.flush()
        ProductPrice.add_product_price(db_session, price_entry.id, product)
        # upload images to s3
        PriceEntryImage.add_images(db_session, price_entry.id, images)
        db_session.commit()
        db_session.refresh(price_entry)
        return price_entry
    

    @staticmethod
    def add_price_entry(
        db_session: Session,
        user_id: int,
        seller_type: SellerType,
        window: WindowType,
        product: dict,
        location: Optional[str] = None,
        transaction_term: Optional[TransactionTerm] = None,
        omc_id: Optional[int] = None,
        bdc_id: Optional[int] = None,
        images: Optional[List[str]] = None
    ):
        price_entry = PriceEntry(
            seller_type=seller_type,
            user_id=user_id,
            window=window,
            station_location=location if seller_type == SellerType.OMC else None,
            town_of_loading=location if seller_type == SellerType.BDC else None,
            transaction_term=transaction_term,
            omc_id=omc_id,
            bdc_id=bdc_id
        )
        db_session.add(price_entry)
        db_session.flush()
        ProductPrice.add_product_price(db_session, price_entry.id, product)
        PriceEntryImage.add_images(db_session, price_entry.id, images)
        db_session.commit()
        db_session.refresh(price_entry)
        return price_entry

    @staticmethod
    def update_basic_fields(db_session: Session, price_entry_instance: "PriceEntry", basic_fields: dict):
        if not basic_fields:
            return
        for key, value in basic_fields.items():
            setattr(price_entry_instance, key, value)
        db_session.add(price_entry_instance)
    
    @staticmethod
    def update_omc_price_entry(db_session: Session, price_entry_id: int, product: dict, images: List[str], basic_fields: dict):
        price_entry = db_session.query(PriceEntry).filter(PriceEntry.id == price_entry_id).first()
        if price_entry:
            PriceEntry.update_basic_fields(db_session, price_entry, basic_fields)
            if product:
                ProductPrice.update_product_price(db_session, price_entry, product)
            if images:
                PriceEntryImage.update_images(db_session, price_entry_id, images)
            db_session.commit()
            db_session.refresh(price_entry)
            return price_entry
        return None
    

    
    


    def omc_sync_json(self):
        return {
            "id": self.id,
            "user": self.user.full_name,
            "seller_type": self.seller_type,
            "date": self.date,
            "window": self.window,
            "station_location": self.station_location,
            "product_price": self.product_price.omc_price_sync_json(),
            "images": [image.image_url for image in self.images],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def bdc_sync_json(self):
        return {
            "id": self.id,
            "user": self.user.full_name,
            "seller_type": self.seller_type,
            "date": self.date,
            "window": self.window,
            "town_of_loading": self.town_of_loading,
            "transaction_term": self.transaction_term,
            "product_price": self.product_price.bdc_price_sync_json(),
            "images": [image.image_url for image in self.images],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    

    @staticmethod
    def get_all_failed_price_entries(db: Session, omc_or_bdc: Literal["omc", "bdc"]):
        """
        Get all price entries that have failed to sync with the BDC or OMC
        """
        if omc_or_bdc == "omc":
            failed_omcs =  db.query(PriceEntry).filter(PriceEntry.seller_type == SellerType.OMC, PriceEntry.sync_status is False).all()
            return [ failed_omc.omc_sync_json() for failed_omc in failed_omcs]
        failed_bcds = db.query(PriceEntry).filter(PriceEntry.seller_type == SellerType.BDC, PriceEntry.sync_status is False).all()
        return [ failed_bdc.bdc_sync_json() for failed_bdc in failed_bcds]
        

    




class ProductPrice(CustomBase):
    __tablename__ = "product_prices"
    
    price_entry_id: Mapped[int] = mapped_column(ForeignKey("price_entries.id"))
    product_type: Mapped[ProductType] = mapped_column(SQLAlchemyEnum(ProductType), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    unit_of_measurement: Mapped[str] = mapped_column(String, nullable=False)
    credit_price: Mapped[Optional[float]] = mapped_column(Float) 
    credit_days: Mapped[Optional[int]] = mapped_column(Integer)  
    
    price_entry: Mapped["PriceEntry"] = relationship(back_populates="product_price")


    @staticmethod
    def add_product_price(db_session: Session, price_entry_id: int, product: dict):
        product_price =ProductPrice(**product.model_dump(), price_entry_id=price_entry_id)
        db_session.add(product_price)
        return product_price
    
    @staticmethod
    def update_product_price(db_session: Session, price_entry: "PriceEntry", product: dict):
        for key, value in product.model_dump(exclude_unset=True).items():
            print(key, value, "key and value")
            setattr(price_entry.product_price, key, value)
        db_session.add(price_entry)  
        return price_entry


    def bdc_price_sync_json(self):
        return {
            "product_type": self.product_type,
            "price": self.price,
            "unit_of_measurement": self.unit_of_measurement,
            "credit_price": self.credit_price,
            "credit_days": self.credit_days
        }
    
    def omc_price_sync_json(self):
        return {
            "product_type": self.product_type,
            "price": self.price,
            "unit_of_measurement": self.unit_of_measurement,
        }


class PriceEntryImage(CustomBase):
    __tablename__ = "price_entry_images"
    
    price_entry_id: Mapped[int] = mapped_column(ForeignKey("price_entries.id"))
    image_url: Mapped[str] = mapped_column(String, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    price_entry: Mapped["PriceEntry"] = relationship(back_populates="images")


    @staticmethod
    def add_images(db_session: Session, price_entry_id: int, images: List[str]):
        if not images:
            return
        for image in images:
            price_entry_image = PriceEntryImage(price_entry_id=price_entry_id, image_url=image.image_url)
            db_session.add(price_entry_image)
        return price_entry_image
    

    

    @staticmethod
    def update_images(db_session: Session, price_entry_id: int, image_updates: List[dict]) -> List["PriceEntryImage"]:
        """
        Updates images for a price entry by:
        - Keeping existing images that are still wanted
        - Deleting images that were removed
        - Adding new images

        Args:
            db_session: Database session
            price_entry_id: ID of the price entry
            image_updates: List of image updates containing:
                - id: For existing images (None for new images)
                - image_url: New URL for the image

        Returns:
            List of all images associated with the price entry after update
        """
        # Get current images from database
        existing_images = db_session.query(PriceEntryImage).filter(
            PriceEntryImage.price_entry_id == price_entry_id
        ).all()

        # Separate updates into existing and new images
        existing_updates = {img.id: img for img in image_updates if img.id is not None}
        new_images = [img for img in image_updates if img.id is None]

        # Process existing images
        kept_images = []
        for existing_img in existing_images:
            if existing_img.id in existing_updates:
                # Update URL if changed
                if existing_img.image_url != existing_updates[existing_img.id].image_url:
                    existing_img.image_url = existing_updates[existing_img.id].image_url
                kept_images.append(existing_img)
            else:
                # Delete images not in the update list
                db_session.delete(existing_img)

        # Add new images
        for new_img in new_images:
            img = PriceEntryImage(
                price_entry_id=price_entry_id,
                image_url=new_img.image_url
            )
            db_session.add(img)
            kept_images.append(img)

        # Commit changes
        db_session.commit()

        # Refresh all kept images to ensure we have current state
        for img in kept_images:
            db_session.refresh(img)

        return kept_images
            
           




class SyncLog(CustomBase):
    __tablename__ = "sync_logs"

    # store all the failed logs and resend them at the end of the day
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    price_entry_id: Mapped[int] = mapped_column(ForeignKey("price_entries.id"))
    sync_status: Mapped[str] = mapped_column(String, default="failed")  
    error_message: Mapped[Optional[str]] = mapped_column(String)
    # price_entry: Mapped["PriceEntry"] = relationship("PriceEntry", back_populates="sync_logs")


    


    @staticmethod
    def add_sync_log(db_session: Session, price_entry_id: int, error_message: Optional[str] = None):
        sync_log = SyncLog(price_entry_id=price_entry_id, error_message=error_message)
        db_session.add(sync_log)
        db_session.commit()
        db_session.refresh(sync_log)
        return sync_log
    
    # 

