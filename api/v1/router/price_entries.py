from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Union, Optional, List
from fastapi_pagination import Page
from utils.auth import bearerschema, AuthToken
from schemas.price_entry import SellerType



from datetime import datetime


from schemas.price_entry import (
    OMCPriceEntryCreate,
    BDCPriceEntryCreate,
    OMCPriceEntryUpdate,
    BDCPriceEntryUpdate,
    OMCPriceEntryOut,
    BDCPriceEntryOut,
    OMCBDCFilterParams,
    TransactionTerm,
    WindowType,
    ProductType,
    DelResponse,
)
from controller.price_entries import PriceEntryController


price_entry_router = APIRouter()




@price_entry_router.get(
    "/price_entries",
    response_model=Union[Page[OMCPriceEntryOut], Page[BDCPriceEntryOut]],
)
async def get_price_entries(
    params: OMCBDCFilterParams = Depends(), bearer_token=Depends(bearerschema)
):
    user_info = AuthToken.verify_user_token(bearer_token.credentials)
    price_entries = PriceEntryController.get_price_entries(
        params, user_info.id)
    return price_entries



@price_entry_router.get(
    "/price_entries/{price_entry_id}",
    response_model=Union[OMCPriceEntryOut, BDCPriceEntryOut],
)
async def get_price_entry_by_id(
    price_entry_id: int, bearer_token=Depends(bearerschema)
):
    AuthToken.verify_user_token(bearer_token.credentials)
    price_entry = PriceEntryController.get_price_entry(price_entry_id)
    return price_entry



@price_entry_router.post("/price_entries/omc", response_model=OMCPriceEntryOut)
async def add_omc_price_entry(
    seller_type: SellerType = Form(...),
    date: datetime = Form(...),
    omc_id: int = Form(...),
    window: WindowType = Form(...),
    station_location: str = Form(...),
    product_type: str = Form(...),
    product_price: float = Form(...),
    product_unit_of_measurement: str = Form(None),
    price_entries_images: List[UploadFile] = File(None),
    bearer_token=Depends(bearerschema),
):
    input_data = {
        "seller_type": seller_type,
        "date": date,
        "omc_id": omc_id,
        "window": window,
        "station_location": station_location,
        "product": {
            "product_type": product_type,
            "price": product_price,
            "unit_of_measurement": product_unit_of_measurement,
        },
    }
    price_entry_data = OMCPriceEntryCreate(**input_data)
    user_info = AuthToken.verify_user_token(bearer_token.credentials)
    price_entry = await PriceEntryController.add_price_entry(
        user_info, price_entry_data, price_entries_images
    )
    return price_entry


@price_entry_router.post("/price_entries/bdc", response_model=BDCPriceEntryOut)
async def add_bdc_price_entry(
    seller_type: SellerType = Form(...),
    date: datetime = Form(...),
    bdc_id: int = Form(...),
    window: WindowType = Form(...),
    town_of_loading: str = Form(...),
    transaction_term: TransactionTerm = Form(...),
    product_credit_price: float = Form(...),
    product_credit_price_days: int = Form(...),
    product_type: str = Form(...),
    product_price: float = Form(...),
    product_unit_of_measurement: str = Form(None),
    price_entries_images: List[UploadFile] = File(None),
    bearer_token=Depends(bearerschema),
):
    input_data = {
        "seller_type": seller_type,
        "date": date,
        "bdc_id": bdc_id,
        "window": window,
        "town_of_loading": town_of_loading,
        "transaction_term": transaction_term,
        "product": {
            "product_type": product_type,
            "price": product_price,
            "unit_of_measurement": product_unit_of_measurement,
            "credit_days": product_credit_price_days,
            "credit_price": product_credit_price,
        },
    }
    price_entry_data = BDCPriceEntryCreate(**input_data)
    user_info = AuthToken.verify_user_token(bearer_token.credentials)
    price_entry = await PriceEntryController.add_price_entry(
        user_info, price_entry_data, price_entries_images
    )
    return price_entry

@price_entry_router.put(
    "/price_entries/omc/{price_entry_id}", response_model=OMCPriceEntryOut
)
async def update_omc_price_entry(
    price_entry_id: int,
    omc_id: Optional[int] = None,
    window: Optional[WindowType] = None,
    station_location: Optional[str] = None,
    product_type: Optional[ProductType] = None,
    product_price: Optional[float] = None,
    product_unit_of_measurement: Optional[str] = None,
    new_price_entries_images: Optional[List[UploadFile]] = File(None),
    bearer_token=Depends(bearerschema),
):
    input_data = {
        "omc_id": omc_id,
        "window": window,
        "station_location": station_location,
        "product": {
            "product_type": product_type,
            "price": product_price,
            "unit_of_measurement": product_unit_of_measurement,
        },
    }

    price_entry_data = OMCPriceEntryUpdate(**input_data)
    AuthToken.verify_user_token(bearer_token.credentials)
    price_entry = await PriceEntryController.update_price_entry(
        price_entry_data, price_entry_id, new_price_entries_images
    )
    return price_entry




@price_entry_router.put(
    "/price_entries/bdc/{price_entry_id}", response_model=BDCPriceEntryOut
)
async def update_bdc_price_entry(
    price_entry_id: int,
    bdc_id: Optional[int] = None,
    window: Optional[WindowType] = None,
    town_of_loading: Optional[str] = None,
    transaction_term: Optional[TransactionTerm] = None,
    product_credit_price: Optional[float] = None,
    product_credit_price_days: Optional[int] = None,
    product_type: Optional[ProductType] = None,
    product_price: Optional[float] = None,
    product_unit_of_measurement: Optional[str] = None,
    new_price_entries_images: Optional[List[UploadFile]] = File(None),
    bearer_token=Depends(bearerschema),
):
    
    input_data = {
        "bdc_id": bdc_id,
        "window": window,
        "town_of_loading": town_of_loading,
        "transaction_term": transaction_term,
        "product": {
            "product_type": product_type,
            "price": product_price,
            "unit_of_measurement": product_unit_of_measurement,
            "credit_days": product_credit_price_days,
            "credit_price": product_credit_price,
        },
    }
    

    price_entry_data =  BDCPriceEntryUpdate(**input_data)
    AuthToken.verify_user_token(bearer_token.credentials)
    price_entry = await  PriceEntryController.update_price_entry(
        price_entry_data, price_entry_id, new_price_entries_images
    )
    return price_entry


@price_entry_router.delete("/price_entries/{price_entry_id}", response_model=DelResponse)
async def delete_price_entry_image(price_entry_id: int, image_id: int):
    message = await PriceEntryController.delete_price_entry_image(price_entry_id, image_id)
    return message



