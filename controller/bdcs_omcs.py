from typing import Dict, Union

from schemas.bdcs import BDCIn, OMCIn
from models.bdcs import BDC, OMC
from utils import sql


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
        if param == "bdc":
            bdcs = sql.get_all_objects_from_database(BDC)
            return bdcs
        elif param == "omc":
            omcs = sql.get_all_objects_from_database(OMC)
            return omcs
        else:
            bdcs = sql.get_all_objects_from_database(BDC)
            omcs = sql.get_all_objects_from_database(OMC)
            return {"bdcs": bdcs, "omcs": omcs}
        