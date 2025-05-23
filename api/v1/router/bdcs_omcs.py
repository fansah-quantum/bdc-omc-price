from fastapi import APIRouter, Depends
from typing import List
from typing import Optional, Union

from schemas.bdcs import BDCIn, OMCIn, BDCOMCOut, BDCOMCAllOut,DelMessage
from controller.bdcs_omcs import BDCOMCController
from utils.auth import AuthToken, bearerschema




bdc_omc_router = APIRouter()



@bdc_omc_router.post("/bdcs", response_model=BDCOMCOut, description="Add a new BDC, requires system admin privileges")
async def add_bdc(bdc_data: BDCIn, bearer_token=Depends(bearerschema)):
    AuthToken.verify_system_admin(bearer_token.credentials)
    bdc = BDCOMCController.add_bdc_omc(bdc_data)
    return bdc

@bdc_omc_router.post("/omcs", response_model=BDCOMCOut, description="Add a new OMC, requires system admin privileges")
async def add_omc(omc_data: OMCIn, bearer_token=Depends(bearerschema)):
    AuthToken.verify_system_admin(bearer_token.credentials)
    omc = BDCOMCController.add_bdc_omc(omc_data)
    return omc


@bdc_omc_router.get("/bdcs_omcs", response_model=Union[BDCOMCAllOut, List[BDCOMCOut]], description="Get all BDCs and OMCs, both system admin and users can access this endpoint")
async def all_bdcs_omcs(param: Optional[str] = None):
    bdcs_omcs = BDCOMCController.all_bdcs_omcs(param)
    return bdcs_omcs


@bdc_omc_router.delete("/bdcs/{bdc_id}", response_model=DelMessage, description="Delete a BDC by ID, requires system admin privileges")
async def delete_bdc(bdc_id: int, bearer_token=Depends(bearerschema)):
    AuthToken.verify_system_admin(bearer_token.credentials)
    bdc = BDCOMCController.delete_bdc_omc(bdc_id, None)
    return bdc

@bdc_omc_router.delete("/omcs/{omc_id}", response_model=DelMessage, description="Delete a OMC by ID, requires system admin privileges")
async def delete_omc(omc_id: int, bearer_token=Depends(bearerschema)):
    AuthToken.verify_system_admin(bearer_token.credentials)
    omc = BDCOMCController.delete_bdc_omc(None, omc_id)
    return omc

@bdc_omc_router.get("/omcs/sync", response_model=DelMessage, description="Sync OMCs with the database, requires system admin privileges")
async def sync_omcs(
    bearer_token=Depends(bearerschema)
    ):
    AuthToken.verify_system_admin(bearer_token.credentials)
    omc = BDCOMCController.sync_omcs()
    return omc


@bdc_omc_router.get("/bdcs/sync", description="Sync BDCs with the database, requires system admin privileges")
async def sync_bdcs(
    bearer_token=Depends(bearerschema)
    ):
    AuthToken.verify_system_admin(bearer_token.credentials)
    bdc = BDCOMCController.sync_bdcs()
    return bdc



