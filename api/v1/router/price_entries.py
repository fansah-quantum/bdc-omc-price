from fastapi import APIRouter, Depends,  UploadFile, File, Form
from typing import Union, Optional, List
from utils.auth import bearerschema, AuthToken
from schemas.price_entry import SellerType
from fastapi.background import BackgroundTasks



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
    DelResponse,
)
from controller.price_entries import PriceEntryController


price_entry_router = APIRouter()




@price_entry_router.get(
    "/price_entries",
    response_model=Union[List[OMCPriceEntryOut], List[BDCPriceEntryOut]],
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



@price_entry_router.post("/price_entries/omc", response_model=list[OMCPriceEntryOut])
async def add_omc_price_entry(
    bg: BackgroundTasks,
    seller_type: SellerType = Form(...),
    date: datetime = Form(...),
    omc_id: str = Form(...),
    window: WindowType = Form(...),
    station_id: str = Form(...),
    product_type: str = Form(...),
    product_price: str = Form(...),
    price_entries_images: List[UploadFile] = File(None),
    bearer_token=Depends(bearerschema),
):
    input_data = {
        "seller_type": seller_type,
        "date": date,
        "omc_id": int(omc_id),
        "window": window,
        "station_id": int(station_id),
        "product": {
            "product_type": product_type,
            "price": product_price,
        },
    }
    price_entry_data = OMCPriceEntryCreate(**input_data)
    user_info = AuthToken.verify_user_token(bearer_token.credentials)
    price_entry = await PriceEntryController.add_price_entry(
        user_info, price_entry_data,bg,  price_entries_images
    )
    return price_entry


@price_entry_router.post("/price_entries/bdc", response_model=List[BDCPriceEntryOut])
async def add_bdc_price_entry(
    bg: BackgroundTasks,
    seller_type: SellerType = Form(...),
    date: datetime = Form(...),
    source_id: str = Form(...),
    bdc_id: str = Form(...),
    window: WindowType = Form(...),
    town_of_loading: str = Form(...),
    transaction_term: TransactionTerm = Form(...),
    product_credit_price: str = Form(None),
    product_credit_price_days: str = Form(None),
    product_type: str = Form(...),
    product_price: str = Form(...),
    price_entries_images: List[UploadFile] = File(None),
    bearer_token=Depends(bearerschema),
):
    input_data = {
        "seller_type": seller_type,
        "date": date,
        "bdc_id": int(bdc_id),
        "window": window,
        "town_of_loading": town_of_loading,
        "transaction_term": transaction_term,
        "source_id": int(source_id) if source_id else None,	
        "product": {
            "product_type": product_type,
            "price": product_price,
            "credit_days": int(product_credit_price_days) if product_credit_price_days else None,
            "credit_price": float(product_credit_price) if product_credit_price else None,
        },
    }
    price_entry_data = BDCPriceEntryCreate(**input_data)
    user_info = AuthToken.verify_user_token(bearer_token.credentials)
    price_entry = await PriceEntryController.add_price_entry(
        user_info, price_entry_data,bg, price_entries_images
    )
    return price_entry

@price_entry_router.put(
    "/price_entries/omc/{price_entry_id}", response_model=OMCPriceEntryOut
)
async def update_omc_price_entry(
    bg: BackgroundTasks,
    price_entry_id: int,
    omc_id: Optional[str] = Form(None),
    window: Optional[WindowType] = Form(None),
    station_id: Optional[str] = Form(None),
    product_type: Optional[str] = Form(None),
    product_price: Optional[str] = Form(None),
    product_unit_of_measurement: Optional[str] = Form(None),
    new_price_entries_images: List[UploadFile] = File(None),
    bearer_token=Depends(bearerschema),
):
    input_data = {
        "omc_id": int(omc_id) if omc_id else None,
        "window": window,
        "station_id": int(station_id) if station_id else None,	
        "product": {
            "product_type": product_type,
            "price": float(product_price) if product_price else None,
            "unit_of_measurement": product_unit_of_measurement,
        },
    }

    price_entry_data = OMCPriceEntryUpdate(**input_data)
    AuthToken.verify_user_token(bearer_token.credentials)
    price_entry = await PriceEntryController.update_price_entry(
        price_entry_data, price_entry_id, "omc", bg, new_price_entries_images
    )
    return price_entry




@price_entry_router.put(
    "/price_entries/bdc/{price_entry_id}", response_model=BDCPriceEntryOut
)
async def update_bdc_price_entry(
    bg: BackgroundTasks,
    price_entry_id: int,
    bdc_id: Optional[str] = Form(None),
    window: Optional[WindowType] = Form(None),
    town_of_loading: Optional[str] = Form(None),
    source_id: Optional[str] = Form(None),
    transaction_term: Optional[TransactionTerm] = Form(None),
    product_credit_price: Optional[str] = Form(None),
    product_credit_price_days: Optional[str] = Form(None),
    product_type: Optional[str] = Form(None),
    product_price: Optional[str] = Form(None),
    product_unit_of_measurement: Optional[str] = Form(None),
    new_price_entries_images: List[UploadFile] = File(None),
    bearer_token=Depends(bearerschema),
):
    
    input_data = {
        "bdc_id": int(bdc_id) if bdc_id else None,
        "window": window,
        "town_of_loading": town_of_loading,
        "transaction_term": transaction_term,
        "source_id": int(source_id) if source_id else None,
        "product": {
            "product_type": product_type,
            "price": float(product_price) if product_price else None,
            "unit_of_measurement": product_unit_of_measurement,
            "credit_days": int(product_credit_price_days) if product_credit_price_days else None,
            "credit_price": float(product_credit_price) if product_credit_price else None,
        },
    }
    

    price_entry_data =  BDCPriceEntryUpdate(**input_data)
    AuthToken.verify_user_token(bearer_token.credentials)
    price_entry = await  PriceEntryController.update_price_entry(
        price_entry_data, price_entry_id,"bdc", bg, new_price_entries_images
    )
    return price_entry

@price_entry_router.delete("/price_entries/{price_entry_id}", response_model=DelResponse)
async def delete_price_entry_image(price_entry_id: int, image_id: int):
    message = await PriceEntryController.delete_price_entry_image(price_entry_id, image_id)
    return message



