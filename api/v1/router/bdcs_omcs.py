from fastapi import APIRouter
from typing import List
from typing import Optional, Union

from schemas.bdcs import BDCIn, OMCIn, BDCOMCOut, BDCOMCAllOut
from controller.bdcs_omcs import BDCOMCController



bdc_omc_router = APIRouter()


@bdc_omc_router.post("/bdc", response_model=BDCOMCOut)
async def add_bdc(bdc_data: BDCIn):
    bdc = BDCOMCController.add_bdc_omc(bdc_data)
    return bdc

@bdc_omc_router.post("/omc", response_model=BDCOMCOut)
async def add_omc(omc_data: OMCIn):
    omc = BDCOMCController.add_bdc_omc(omc_data)
    return omc


@bdc_omc_router.get("/bdcs_omcs", response_model=Union[BDCOMCAllOut, List[BDCOMCOut]])
async def all_bdcs_omcs(param: Optional[str] = None):
    bdcs_omcs = BDCOMCController.all_bdcs_omcs(param)
    return bdcs_omcs



