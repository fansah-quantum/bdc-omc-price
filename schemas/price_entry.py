from datetime import datetime
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict, HttpUrl
from models.bdcs import ProductType, SellerType, WindowType, TransactionTerm

class ProductPriceBase(BaseModel, use_enum_values=True):
    product_type: ProductType
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    unit_of_measurement: Optional[str] = Field(
        None,
        description="Auto-populated based on product type"
    )
    
    @field_validator('unit_of_measurement', mode='before')
    def set_unit_of_measurement(cls, v, info):
        if 'product_type' in info.data:  # Access the 'data' attribute of ValidationInfo
            if info.data['product_type'] == ProductType.LPG:
                return "Ghana Cedis per Kg"
            return "Ghana Cedis per litre"
        return v
    

class ProductPriceBaseUpdate(BaseModel, use_enum_values=True):
    product_type: Optional[ProductType] = None
    price: Optional[float] = None
    unit_of_measurement: Optional[str] = None
    
    @field_validator('unit_of_measurement', mode='before')
    def set_unit_of_measurement(cls, v, info):
        if 'product_type' in info.data:
            if info.data['product_type'] == ProductType.LPG:
                return "Ghana Cedis per Kg"
            return "Ghana Cedis per litre"
        return v

class BDCProductPriceCreate(ProductPriceBase):
    credit_price: Optional[float] = Field(
        None,
        gt=0,
        description="Credit price must be greater than 0"
    )
    credit_days: Optional[int] = Field(
        None,
        ge=0,
        description="Number of credit days must be 0 or positive"
    )

class PriceEntryImageBase(BaseModel):
    image_url: str = Field(..., description="URL of the uploaded image")

class OMCPriceEntryCreate(BaseModel):
    seller_type: SellerType = Field(
        default=SellerType.OMC,
        description="Must be OMC for this schema"
    )
    date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Date of price collection"
    )
    omc_id: int = Field(..., description="ID of the OMC")
    window: WindowType
    station_location: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Location of the station (e.g., 'Ofankor, Greater Accra')"
    )
    product: ProductPriceBase = Field(
        ...,
        description="product and their prices"
    )
    
    @field_validator('seller_type')
    def validate_seller_type(cls, v):
        if v != SellerType.OMC:
            raise ValueError("Seller type must be OMC for this schema")
        return v

class BDCPriceEntryCreate(BaseModel):
    seller_type: SellerType = Field(
        default=SellerType.BDC,
        description="Must be BDC for this schema"
    )
    date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Date of price collection"
    )
    bdc_id: int = Field(..., description="ID of the BDC")
    window: WindowType
    town_of_loading: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Location of the depot (e.g., 'Tema')"
    )
    transaction_term: Optional[TransactionTerm] = Field(
        None,
        description="Cash or credit transaction terms"
    )
    product: BDCProductPriceCreate = Field(
        ...,
        description=" products and it's price"
    )


    @field_validator('seller_type')
    def validate_seller_type(cls, v):
        if v != SellerType.BDC:
            raise ValueError("Seller type must be BDC for this schema")
        return v

# Combined create schema using Union
PriceEntryCreate = Union[OMCPriceEntryCreate, BDCPriceEntryCreate]

# Update schemas
class BDCProductPriceUpdate(ProductPriceBaseUpdate):
    credit_price: Optional[float] = Field(None, gt=0)
    credit_days: Optional[int] = Field(None, ge=0)

class PriceEntryImageUpdate(BaseModel):
    id: Optional[int] = None  
    image_url: Optional[str] = None

class PriceEntryUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    date: Optional[datetime] = None
    window: Optional[WindowType] = None
    station_location: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100
    )
    # BDC specific fields
    town_of_loading: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100
    )
    transaction_term: Optional[TransactionTerm] = None
    product: Optional[BDCProductPriceUpdate] = None
    images: Optional[List[PriceEntryImageUpdate]] = None

# Response schemas
class BDCProductPriceOut(ProductPriceBase):
    id: int
    credit_price: Optional[float] = None
    credit_days: Optional[int] = None

class ProductPriceOut(ProductPriceBase):
    id: int

class PriceEntryImageOut(PriceEntryImageBase):
    id: int
    uploaded_at: datetime

class PriceEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    seller_type: SellerType
    date: datetime
    window: WindowType
    user_id: int
    # OMC fields
    omc_id: Optional[int] = None
    omc_name: Optional[str] = None
    station_location: Optional[str] = None
    # BDC fields
    bdc_id: Optional[int] = None
    bdc_name: Optional[str] = None
    town_of_loading: Optional[str] = None
    transaction_term: Optional[TransactionTerm] = None
    
    product: ProductPriceOut
    images: List[PriceEntryImageOut]
    created_at: datetime
    updated_at: datetime


class OMCPriceEntryUpdate(BaseModel):
    omc_id: Optional[int] = None
    window: Optional[WindowType] = None
    station_location: Optional[str] = None
    product: Optional[ProductPriceBaseUpdate] = None
    images: Optional[List[PriceEntryImageUpdate]] = None

class BDCPriceEntryUpdate(BaseModel):
    bdc_id: Optional[int] = None
    window: Optional[WindowType] = None
    town_of_loading: Optional[str] = None
    transaction_term: Optional[TransactionTerm] = None
    product: Optional[BDCProductPriceUpdate] = None
    images: Optional[List[PriceEntryImageUpdate]] = None


class OMCPriceEntryOut(BaseModel):
    id: int
    user_id: int
    seller_type: SellerType
    date: datetime
    window: WindowType
    station_location: str
    product_price: ProductPriceOut
    images: List[PriceEntryImageOut]
    created_at: datetime
    updated_at: datetime

class BDCPriceEntryOut(BaseModel):
    id: int
    user_id: int
    seller_type: SellerType
    date: datetime
    window: WindowType
    town_of_loading: str
    transaction_term: TransactionTerm
    product_price: BDCProductPriceOut
    images: List[PriceEntryImageOut]
    created_at: datetime
    updated_at: datetime


class OMCBDCFilterParams(BaseModel):
    seller_type: SellerType = Field("omc", description="Filter by seller type")
    product_type: Optional[ProductType] = None 
    omc_or_bdc_id: Optional[int] = None
    window: Optional[WindowType] = None
    transaction_term: Optional[TransactionTerm] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "desc"
    from_date: Optional[str] = None
    to_date: Optional[str] = None
    page: Optional[int] = 1
    size: Optional[int] = 50



class PresignedUrlItem(BaseModel):
    image_name: str
    url: HttpUrl



    