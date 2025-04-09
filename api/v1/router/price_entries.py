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
    PresignedUrlItem,
    TransactionTerm,
    WindowType,
    ProductType
)
from controller.price_entries import PriceEntryController


price_entry_router = APIRouter()


@price_entry_router.post("/price_entries/omc", response_model=OMCPriceEntryOut)
async def add_omc_price_entry(
    price_entry_data: OMCPriceEntryCreate, bearer_token=Depends(bearerschema)
):
    user_info = AuthToken.verify_user_token(bearer_token.credentials)
    price_entry = PriceEntryController.add_price_entry(
        user_info, price_entry_data)
    return price_entry


@price_entry_router.post("/price_entries/bdc", response_model=BDCPriceEntryOut)
async def add_bdc_price_entry(
    price_entry_data: BDCPriceEntryCreate, bearer_token=Depends(bearerschema)
):
    user_info = AuthToken.verify_user_token(bearer_token.credentials)
    price_entry = PriceEntryController.add_price_entry(
        user_info, price_entry_data)
    return price_entry


@price_entry_router.put(
    "/price_entries/omc/{price_entry_id}", response_model=OMCPriceEntryOut
)
async def update_omc_price_entry(
    price_entry_id: int,
    price_entry_data: OMCPriceEntryUpdate,
    bearer_token=Depends(bearerschema),
):
    AuthToken.verify_user_token(bearer_token.credentials)
    price_entry = PriceEntryController.update_price_entry(
        price_entry_data, price_entry_id
    )
    return price_entry


@price_entry_router.put(
    "/price_entries/bdc/{price_entry_id}", response_model=BDCPriceEntryOut
)
async def update_bdc_price_entry(
    price_entry_id: int,
    price_entry_data: BDCPriceEntryUpdate,
    bearer_token=Depends(bearerschema),
):
    AuthToken.verify_user_token(bearer_token.credentials)
    price_entry = PriceEntryController.update_price_entry(
        price_entry_data, price_entry_id
    )
    return price_entry


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


@price_entry_router.post(
    "/price_entries/presigned_url", response_model=list[PresignedUrlItem]
)
async def get_presigned_url(
    image_names: list[str],
    # bearer_token = Depends(bearerschema)
):
    # AuthToken.verify_user_token(bearer_token.credentials)
    url = PriceEntryController.get_presigned_url(image_names)
    return url


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


@price_entry_router.post("/price_entries/upload-image")
async def upload_image(file: UploadFile = File(...)):
    image_url = await PriceEntryController.upload_image(file)
    return image_url


@price_entry_router.post("/upload-data-images/")
async def upload_data_images(product: dict = Form(...), file: UploadFile = File(...)):
    print(file)
    print(product)
    return {"filename": file.filename, "data": product}


@price_entry_router.post("/new-price_entries/omc")
async def new_add_omc_price_entry(
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
    price_entry = PriceEntryController.add_price_entry(
        user_info, price_entry_data, price_entries_images
    )
    return price_entry


@price_entry_router.post("/new-price_entries/bdc")
async def new_add_bdc_price_entry(
    seller_type: SellerType = Form(...),
    date: datetime = Form(...),
    omc_id: int = Form(...),
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
        "omc_id": omc_id,
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
    price_entry = PriceEntryController.add_price_entry(
        user_info, price_entry_data, price_entries_images
    )
    return price_entry



