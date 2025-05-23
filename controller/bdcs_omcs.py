from typing import Dict, Union
import requests

from schemas.bdcs import BDCIn, OMCIn
from models.bdcs import BDC, OMC
from utils import sql
from utils.session import CreateDBSession
from fastapi import HTTPException
from utils.common import remove_dict_dulicates
from fastapi.exceptions import HTTPException
from config.setting import settings




OMC_URL = settings.OMC_SYNC_URL
BDC_URL = settings.BDC_SYNC_URL

HEADERS = {
    "Content-Type": "application/json",
    "API-KEY": ""
}

class BDCOMCController:

    @staticmethod
    def add_bdc_omc(bdc_data: Union[BDCIn, OMCIn]) -> Dict:
        """Add a new BDC to the database

        :param bdc_data: The BDC data to be added
        :type bdc_data: BDCIn
        :return: The BDC data that was added
        :rtype: Dict
        """
        bdc_ob = BDC(**bdc_data.model_dump()) if isinstance(bdc_data, BDCIn) else OMC(**bdc_data.model_dump())
        bdc = sql.add_object_to_database(bdc_ob)
        return bdc
    

    @staticmethod
    def all_bdcs_omcs(param: str) -> Dict:
        """Get all BDCs or OMCs from the database

        :param param: The parameter to query
        :type param: str
        :return: The BDCs or OMCs
        :rtype: Dict
        """
        with CreateDBSession() as db_session:
            if param == "bdc":
                bdcs = db_session.query(BDC).filter_by(deleted_at=None).all()
                return bdcs
            elif param == "omc":
                omcs = db_session.query(OMC).filter_by(deleted_at=None).all()
                return omcs
            else:
                bdcs = db_session.query(BDC).filter_by(deleted_at=None).all()
                omcs = db_session.query(OMC).filter_by(deleted_at=None).all()
                return {"bdcs": bdcs, "omcs": omcs}
        


    @staticmethod
    def delete_bdc_omc(bdc_id: int = None, omc_id: int = None) -> Dict:
        """Delete a BDC from the database

        :param bdc_id: The BDC ID to be deleted
        :type bdc_id: int
        :return: The BDC data that was deleted
        :rtype: Dict
        """
        with CreateDBSession() as db_session:
            if bdc_id:
                db_session.query(BDC).filter(BDC.id == bdc_id).delete()
                db_session.commit()
                return {"message": "BDC deleted successfully", "status": True}
            elif omc_id:
                db_session.query(OMC).filter(OMC.id == omc_id).delete()
                db_session.commit()
                return {"message": "OMC deleted successfully", "status": True}
            else:
                raise HTTPException(status_code=400, detail="Either bdc_id or omc_id must be provided")
            


    @staticmethod

    def sync_omcs() -> Dict:
        """Sync OMCs with the database

        :return: The OMC data that was synced
        :rtype: Dict
        """
        HEADERS["API-KEY"] = settings.OMC_API_KEY
        response = requests.get(OMC_URL, headers=HEADERS)
        if response.status_code == 200:
             omcs= remove_dict_dulicates(response.json())
             with CreateDBSession() as db_session:	 
                sync_omcs = OMC.sync_omcs(db_session,omcs)
                return {
                    "message": f"{len(sync_omcs)} OMCs synced successfully",
                    "status": True,
                }
        raise HTTPException(status_code=response.status_code, detail=response.text)
    

    @staticmethod
    def sync_bdcs() -> Dict:
        """Sync BDCs with the database

        :return: The BDC data that was synced
        :rtype: Dict
        """
        HEADERS["API-KEY"] = settings.BDC_API_KEY
        response = requests.get(BDC_URL, headers=HEADERS)
        if response.status_code == 200:
            bdcs = remove_dict_dulicates(response.json())
            with CreateDBSession() as db_session:
                sync_bdcs = BDC.sync_bdcs(db_session, bdcs)
                return {
                    "message": f"{len(sync_bdcs)} BDCs synced successfully",
                    "status": True,
                }
        raise HTTPException(status_code=response.status_code, detail=response.text)
    

    @staticmethod
    def sync_bdcs_omcs() -> Dict:
        """Sync BDCs and OMCs with the database

        :return: The BDCs and OMCs data that was synced
        :rtype: Dict
        """
        response = requests.get(BDC_URL, headers=HEADERS)
        if response.status_code == 200:
            bdcs = remove_dict_dulicates(response.json())
            with CreateDBSession() as db_session:
                sync_bdcs = BDC.sync_bdcs(db_session, bdcs)
                return {
                    "message": f"{len(sync_bdcs)} BDCs synced successfully",
                    "status": True,
                }
        raise HTTPException(status_code=response.status_code, detail=response.text)

        

  


            
            