from typing import Optional

from sqlalchemy import String, or_

from sqlalchemy.orm import Mapped, Session
from sqlalchemy.orm import mapped_column
from datetime import datetime
from enum import Enum
from typing import List, Literal




from sqlalchemy import ForeignKey, Float, DateTime, Boolean, Integer
from sqlalchemy.orm import  Mapped, mapped_column, relationship
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
    
    @classmethod
    def sync_bdcs(cls, db_session: Session, bdc_data: List[dict]):




        """
        Sync BDCs with the database.
        This method will add or update BDCs based on the provided data.
        remove bdcs that are not in the list of bdc_data
        add all new bdcs, do not update existing bdcs
        """
        existing_bdc_names = {(bdc.name) for bdc in db_session.query(cls).all()}
        new_bdc_names = {(bdc["name"]) for bdc in bdc_data}
        for bdc in existing_bdc_names - new_bdc_names:
            bdc_instance = db_session.query(cls).filter(cls.name == bdc).first()
            if bdc_instance and bdc_instance.deleted_at is None:
                bdc_instance.soft_delete()
            else:
                bdc_instance.restore()
                # db_session.delete(bdc_instance)
        for bdc_name in new_bdc_names - existing_bdc_names:
            cls.add_bdc(db_session, bdc_name)
        db_session.commit()
        return db_session.query(cls).all()


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
    

    @classmethod
    def sync_omcs(cls, db_session: Session, omc_data: List[dict]):
        """
        Sync OMCs with the database.
        This method will add or update OMCs based on the provided data.
        remove omcs that are not in the list of omc_data
        add all new omcs, do not update existing omcs
        """
        existing_omc_names = {(omc.name) for omc in db_session.query(cls).all()}
        new_omc_names = {(omc["name"]) for omc in omc_data}
        for omc in existing_omc_names - new_omc_names:
            omc_instance = db_session.query(cls).filter(cls.name == omc).first()
            if omc_instance and omc_instance.deleted_at is None:
                omc_instance.soft_delete()
            else:
                omc_instance.restore()
                # db_session.delete(omc_instance)
        for omc_name in new_omc_names - existing_omc_names:
            cls.add_omc(db_session, omc_name)
        db_session.commit()
        return db_session.query(cls).all()


class ProductType(str, Enum):
    PETROL = "petrol"
    DIESEL = "diesel"
    LPG = "LPG"
    RFO = "rfo"
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

    omc_id: Mapped[int] = mapped_column(ForeignKey("omcs.id"))
    station_location: Mapped[Optional[str]] = mapped_column(String)

    # BDC specific fields
    bdc_id: Mapped[Optional[int]] = mapped_column(ForeignKey("bdcs.id"))
    town_of_loading: Mapped[Optional[str]] = mapped_column(String)
    transaction_term: Mapped[Optional[TransactionTerm]] = mapped_column(SQLAlchemyEnum(TransactionTerm))
    station_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("stations.id"), nullable=True)
    station: Mapped[Optional["Station"]] = relationship(back_populates="price_entries_station", lazy="selectin")

    user: Mapped["User"] = relationship(back_populates="price_entries", lazy="selectin")
    omc: Mapped[Optional["OMC"]] = relationship(back_populates="price_entries", lazy="selectin")
    # source_omc: Mapped[Optional["OMC"]] = relationship(foreign_keys=[source_id],lazy="selectin")
    bdc: Mapped[Optional["BDC"]] = relationship(back_populates="price_entries", lazy="selectin")
    product_price: Mapped["ProductPrice"] = relationship(back_populates="price_entry", lazy="selectin")
    images: Mapped[List["PriceEntryImage"]] = relationship(back_populates="price_entry", lazy="selectin")
    external_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    update_sync_status: Mapped[bool] = mapped_column(Boolean, default=False)

    @staticmethod
    def add_omc_price_entry(db_session: Session, user_id: int, omc_id: int, window: WindowType, product: dict,  station_location: str, images: Optional[List[str]]):
        price_entry = PriceEntry(seller_type= "omc", user_id=user_id, omc_id=omc_id, window=window, station_location=station_location)
        db_session.add(price_entry)
        db_session.flush()
        product_prices = product.price.split(",")
        product_types = product.product_type.split(",")
        for product_price,product_type in zip(product_prices, product_types):
            product_price_data = {
                "product_type": product_type,
                "price": float(product_price),
                "unit_of_measurement": compute_unit_of_measurement(product_type),
            }
            ProductPrice.add_product_price(db_session, price_entry.id, product_price_data)

        # TODO : to go with this method, map the product as a list to the price entry
        PriceEntryImage.add_images(db_session, price_entry.id, images)
        db_session.commit()
        db_session.refresh(price_entry)
        return price_entry

    @staticmethod
    def add_multiple_omc_price_entry(db_session: Session,omc_base_data : dict, product: dict, images: Optional[List[str]]):
        prince_entry_list = []

        product_prices = product.price.split(",")
        product_types = product.product_type.split(",")
        for product_price,product_type in zip(product_prices, product_types):
            product_price_data = {
                "product_type": product_type,
                "price": float(product_price),
                "unit_of_measurement": compute_unit_of_measurement(product_type),
            }
            price_entry = PriceEntry(**omc_base_data)
            db_session.add(price_entry)
            db_session.flush()
            ProductPrice.add_product_price(db_session, price_entry.id, product_price_data)
            prince_entry_list.append(price_entry)
            PriceEntryImage.add_images(db_session, price_entry.id, images)
        db_session.commit()
        db_session.refresh(price_entry)
        return prince_entry_list

    @staticmethod
    def add_multiple_bdc_price_entry(db_session: Session, bdc_base_data: dict, product: dict, images: Optional[List[str]]):
        price_entry_list = []
        product_prices = product.price.split(",")
        product_types = product.product_type.split(",")
        for product_price,product_type in zip(product_prices, product_types):
            product_price_data = {
                "product_type": product_type,
                "price": float(product_price),
                "unit_of_measurement": compute_unit_of_measurement(product_type),
                "credit_price": product.credit_price if bdc_base_data['transaction_term'] == TransactionTerm.CREDIT else None,
                "credit_days": product.credit_days if bdc_base_data['transaction_term'] == TransactionTerm.CREDIT else None,
            }
            price_entry = PriceEntry(**bdc_base_data)
            db_session.add(price_entry)
            db_session.flush()
            ProductPrice.add_product_price(db_session, price_entry.id, product_price_data)
            PriceEntryImage.add_images(db_session, price_entry.id, images)
            price_entry_list.append(price_entry)
        db_session.commit()
        db_session.refresh(price_entry)
        return price_entry_list

    @staticmethod
    def add_bdc_price_entry(db_session: Session, user_id: int, bdc_id: int, window: WindowType, product: dict, town_of_loading: str, transaction_term: TransactionTerm, images: Optional[List[str]]):
        price_entry = PriceEntry(seller_type= "bdc", user_id=user_id, bdc_id=bdc_id, window=window, town_of_loading=town_of_loading, transaction_term=transaction_term)
        db_session.add(price_entry)
        db_session.flush()
        ProductPrice.add_product_price(db_session, price_entry.id, product)
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
        basic_fields['update_sync_status'] = True
        for key, value in basic_fields.items():
            setattr(price_entry_instance, key, value) if value else None
        db_session.add(price_entry_instance)

    @staticmethod
    def update_omc_price_entry(db_session: Session, price_entry_id: int, seller_type: Literal["omc", "bdc"], product: dict, images: List[str], basic_fields: dict, new_price_entry_images: List[str] = None) -> Optional["PriceEntry"]:
        price_entry = db_session.query(PriceEntry).filter(PriceEntry.id == price_entry_id, PriceEntry.seller_type == seller_type).first()
        if price_entry:
            PriceEntry.update_basic_fields(db_session, price_entry, basic_fields)
            if product:
                ProductPrice.update_product_price(db_session, price_entry, product)
            if images:
                PriceEntryImage.update_images(db_session, price_entry_id, images)
            if new_price_entry_images:
                PriceEntryImage.add_images(db_session, price_entry_id, new_price_entry_images)
            db_session.commit()
            db_session.refresh(price_entry)
            return price_entry
        return None

    def omc_sync_json(self):
        return {
            "id": self.id,
            "product_name": self.product_price.product_type,
            "station": {
                    "name": self.station.name,
                    "location": self.station.location,
                    },
            "omc_name": self.omc.name,
            "date": self.date.strftime("%Y-%m-%d"),
            "cash_price": self.product_price.price,
        }

    def bdc_sync_json(self):
        return {
            "id": self.id,	
            "product_name": self.product_price.product_type,
            "source_name": self.omc.name,
            "bdc_name": self.bdc.name,
            "date": self.date.strftime("%Y-%m-%d"),
            "cash_price": self.product_price.price,
            "credit_price": self.product_price.credit_price,
            "credit_days": self.product_price.credit_days
        }

    def failed_omc_sync_json(self):
        return {
            "id": self.id,
            "product_name": self.product_price.product_type,
            "station": {
                    "name": self.station.name if self.station else None,
                    "location": self.station.location if self.station else None,
                    },
            "omc_name": self.omc.name,
            "date": self.date.strftime("%Y-%m-%d"),
            "cash_price": self.product_price.price if self.product_price else None,
            "user_id": self.user_id,
            "external_id": self.external_id if self.external_id else None,
        }

    def failed_bdc_sync_json(self):
        return {
            "id": self.id,	
            "product_name": self.product_price.product_type,
            "source_name": self.omc.name,
            "bdc_name": self.bdc.name,
            "date": self.date.strftime("%Y-%m-%d"),
            "cash_price": self.product_price.price if self.product_price else None,
            "credit_price": self.product_price.credit_price if self.product_price else None,
            "credit_days": self.product_price.credit_days if self.product_price else None,
            "user_id": self.user_id,
            "external_id": self.external_id if self.external_id else None,
        }

    @staticmethod
    def get_all_failed_price_entries(db: Session, omc_or_bdc: Literal["omc", "bdc"]):
        """
        Get all price entries that have failed to sync with the BDC or OMC
        """
        if omc_or_bdc == "omc":
            failed_omcs = (
                db.query(PriceEntry)
                .filter(
                    PriceEntry.seller_type == SellerType.OMC,
                    PriceEntry.external_id.is_(None),
                    or_(
                        PriceEntry.seller_type == SellerType.OMC,
                        PriceEntry.update_sync_status is False,

                    ),
                )
                .all()
            )
            return group_by_external_id(failed_omcs)
        failed_bcds = (
            db.query(PriceEntry)
            .filter(
                PriceEntry.seller_type == SellerType.BDC,
                PriceEntry.external_id.is_(None),
                or_(
                    PriceEntry.seller_type == SellerType.BDC,
                    PriceEntry.update_sync_status is False,
                ),
            )
            .all()
        )
        return group_by_external_id(failed_bcds)


def group_by_external_id(price_entries: List[PriceEntry]) -> dict:

    grouped_entries = {
        "to_update": [entry for entry in price_entries if entry.external_id],
        "to_create": [entry for entry in price_entries if not entry.external_id]
    }
    return grouped_entries


class ProductPrice(CustomBase):
    __tablename__ = "product_prices"
    
    price_entry_id: Mapped[int] = mapped_column(ForeignKey("price_entries.id"))
    product_type: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    unit_of_measurement: Mapped[str] = mapped_column(String, nullable=False)
    credit_price: Mapped[Optional[float]] = mapped_column(Float) 
    credit_days: Mapped[Optional[int]] = mapped_column(Integer)  
    
    price_entry: Mapped["PriceEntry"] = relationship(back_populates="product_price")


    @staticmethod
    def add_product_price(db_session: Session, price_entry_id: int, product: dict):
        if isinstance(product, dict):
            product = product 
        else: 
            product = product.model_dump(exclude_unset=True)
        product_price =ProductPrice(**product, price_entry_id=price_entry_id)
        db_session.add(product_price)
        return product_price
    
    @staticmethod
    def update_product_price(db_session: Session, price_entry: "PriceEntry", product: dict):
        for key, value in product.model_dump(exclude_unset=True).items():
            setattr(price_entry.product_price, key, value) if value else None
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
            price_entry_image = PriceEntryImage(price_entry_id=price_entry_id, image_url=image['image_url'])
            db_session.add(price_entry_image)
            db_session.flush()
        return price_entry_image
    

    

    @staticmethod
    def update_images(db_session: Session, price_entry_id: int, image_updates: List[dict]) -> List["PriceEntryImage"]:
        
        existing_images = db_session.query(PriceEntryImage).filter(
            PriceEntryImage.price_entry_id == price_entry_id
        ).all()

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



    


    
def compute_unit_of_measurement(product_type:str)-> str : 
        if product_type == "LPG":
            return "Ghana Cedis per Kg"
        return "Ghana Cedis per litre"



