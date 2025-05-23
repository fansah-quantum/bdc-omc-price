from datetime import datetime
from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict, HttpUrl
from models.bdcs import ProductType, SellerType, WindowType, TransactionTerm

class ProductPriceBase(BaseModel, use_enum_values=True):
    product_type: str
    price: str = Field(..., description="Price must be greater than 0")
    unit_of_measurement: Optional[str] = Field(
        None,
        description="Auto-populated based on product type"
    )
    
    
    

class ProductPriceBaseUpdate(BaseModel, use_enum_values=True):
    product_type: Optional[str] = None
    price: Optional[float] = None
    unit_of_measurement: Optional[str] = None
    
    @field_validator('unit_of_measurement', mode='before')
    def set_unit_of_measurement(cls, v, info):
        if 'product_type' in info.data:
            if info.data['product_type'] == ProductType.LPG:
                return "Ghana Cedis per Kg"
            return "Ghana Cedis per litre"
        return v
    

class BDCProductPriceBase(BaseModel, use_enum_values=True):
    product_type: str
    price: float = Field(..., description="Price must be greater than 0")
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
    
    product: ProductPriceBase = Field(
        ...,
        description="product and their prices"
    )
    # source_id: int = Field(description="omc source id")
    station_id: int = Field(description="station id")
    
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

    source_id: int = Field(..., description="bdc source id")


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
class BDCProductPriceOut(BDCProductPriceBase):
    id: int
    credit_price: Optional[float] = None
    credit_days: Optional[int] = None

class ProductPriceOut(BaseModel):
    id: int
    product_type: str
    price: float
    unit_of_measurement: Optional[str] = None





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
    station_id: Optional[int] = None
    product: Optional[ProductPriceBaseUpdate] = None
    images: Optional[List[PriceEntryImageUpdate]] = None

class BDCPriceEntryUpdate(BaseModel):
    bdc_id: Optional[int] = None
    window: Optional[WindowType] = None
    town_of_loading: Optional[str] = None
    transaction_term: Optional[TransactionTerm] = None
    product: Optional[BDCProductPriceUpdate] = None
    images: Optional[List[PriceEntryImageUpdate]] = None


class StationOut(BaseModel):
    id: int
    name: str
    location: str
    


class OMCPriceEntryOut(BaseModel):
    id: int
    user_id: int
    seller_type: SellerType
    date: datetime
    window: WindowType
    product_price: ProductPriceOut
    images: List[PriceEntryImageOut]
    omc_id: Optional[int] = None
    station: Optional[StationOut] 
    created_at: datetime
    updated_at: datetime

class BDCPriceEntryOut(BaseModel):
    id: int
    user_id: int
    seller_type: SellerType
    date: datetime
    bdc_id: int
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
    window: Optional[WindowType] = None
    transaction_term: Optional[TransactionTerm] = None
    sort_by: Optional[str] = None
    sort_order: Optional[str] = "desc"
    from_date: Optional[str] = None
    to_date: Optional[str] = None



class PresignedUrlItem(BaseModel):
    image_name: str
    url: HttpUrl



class DelResponse(BaseModel):
    message: str = Field(..., description="Success message")
    status: bool 



    