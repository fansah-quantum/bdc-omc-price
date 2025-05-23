import requests

from utils.session import CreateDBSession
from models.bdcs import PriceEntry
from apscheduler.schedulers.background import BackgroundScheduler
from models.users import User
from tools.log import Log
from config.setting import settings



sync_logger = Log(f"{__name__}")




class SyncController:

    
    @staticmethod
    def send_request( method: str, url: str, data: dict[str, str] = None, HEADERS: dict= None) -> requests.Response:
        """
        Send a request to the specified url with the specified data and headers.
        """
        try:
            response = requests.request(
                method,
                url,
                json=data,
                headers=HEADERS,
                timeout=30,
            )
            return response
        except Exception as e:
            raise ValueError(f"Unable to send data {e}")


    @staticmethod
    def send_and_save_entry(
        method: str, url: str, data: dict[str, str], HEADERS: dict = None) -> None:
        """
        Send a request to the specified url with the specified data and headers.
        """
        response = SyncController.send_request(method, url, data, HEADERS)
        if response.status_code != 200:
            sync_logger.error(f"Failed to send data {data}: {response.text}")
        SyncController.save_failed_request_to_db(data)
            

    @staticmethod
    def save_failed_request_to_db(request_data: dict[str, str]) -> None:
        """
        Save the failed request to the database.
        """
        with CreateDBSession() as db:
            price_entry = db.query(PriceEntry).filter_by(
                id=request_data.get("id"),
            ).first()
            price_entry.sync_status = True
            db.commit()
            db.refresh(price_entry)
            return price_entry
        

    @staticmethod
    def save_successful_request_to_db(resource_id: int, request_data: dict[str, str], response_data: dict) -> None:
        """
        Save the failed request to the database.
        """
        with CreateDBSession() as db:
            price_entry = db.query(PriceEntry).filter_by(
                id=resource_id,
            ).first()
            price_entry.external_id =  response_data.get("id")
            price_entry.update_sync_status = True
            db.commit()
            db.refresh(price_entry)
            return price_entry
        

    @staticmethod
    def retry_failed_bdcs() -> None:
        """
        Retry all failed dbcs syncs.
        """
        with CreateDBSession() as db:
            failed_bdcs = PriceEntry.get_all_failed_price_entries(db, "bdc")
            bdcs_to_create = failed_bdcs.get("to_create")
            bdcs_to_update = failed_bdcs.get("to_update")
            if bdcs_to_create:
                for bdc in bdcs_to_create:
                    data = bdc.failed_bdc_sync_json()
                    user_id = data.pop("user_id")
                    external_id = data.pop("external_id", None)
                    SendController.send_omc_data_to_company_config(user_id, [data], f"{settings.OMC_BDC_URL}/bdc")
            if bdcs_to_update:
                for bdc in bdcs_to_update:
                    data = bdc.failed_bdc_sync_json()
                    user_id = data.pop("user_id")
                    external_id = data.pop("external_id", None)
                    SendController.update_omc_data_to_company_config(user_id, [data], f"{settings.OMC_BDC_URL}/bdc/{external_id}")
                

    @staticmethod
    def retry_failed_omcs() -> None:
        """
        Retry all failed dbcs syncs.
        """
        with CreateDBSession() as db:
            failed_omcs = PriceEntry.get_all_failed_price_entries(db, "omc")
            omcs_to_create = failed_omcs.get("to_create")
            omcs_to_update = failed_omcs.get("to_update")
            if omcs_to_create:
                sync_logger.info(f"Retrying failed omcs: {omcs_to_create}")
                for omc in omcs_to_create if omcs_to_create else None:
                    data = omc.failed_omc_sync_json()
                    user_id = data.pop("user_id")
                    data.pop("external_id", None)	
                    SendController.send_omc_data_to_company_config(user_id, [data], f"{settings.OMC_BDC_URL}/omc")
            if omcs_to_update:
                sync_logger.info(f"Retrying failed omcs: {omcs_to_update}")
                for omc in omcs_to_update if omcs_to_update else None:
                    data = omc.failed_omc_sync_json()
                    user_id = data.pop("user_id")
                    external_id = data.pop("external_id", None)
                    SendController.update_omc_data_to_company_config(user_id, [data], f"{settings.OMC_BDC_URL}/omc/{external_id}")
        
                




            
                

                
                    


    @staticmethod
    def schedule_retry():
        """
        Schedule the retry_failed_requests function to run at 12 AM every day.
        """
        scheduler = BackgroundScheduler()
        scheduler.add_job(SyncController.retry_failed_bdcs, "cron", hour=0, minute=0)
        scheduler.add_job(SyncController.retry_failed_omcs, "cron", hour=0, minute=0)
        scheduler.start()






class SendController:
    """
    SendController is responsible for sending data to the user's specific company config.
    """


    @staticmethod
    def get_user_config_url(user_id: int) -> dict[str, str]:
        """
        Get the user's specific company config URL.
        """
        with CreateDBSession() as db_session:
            user = db_session.query(User).filter_by(id=user_id).first()
            company_config_url = user.config_url()
            return company_config_url
            

    @staticmethod
    def send_data_to_company_config(user_id: int, data: dict[str, str]
    ) -> None:
        """
        Send data to the user's specific company config.
        """
        company_config_url = SendController.get_user_config_url(user_id)
        url = company_config_url["api_endpoint"]
        headers = {
            "api_user": company_config_url["api_user"],
            "api_key": company_config_url["api_key"],
        }
        response = SyncController.send_request("post", url, data, headers)
        if response.status_code != 200:
            sync_logger.error(f"Failed to send data {data}: {response.text}")
        SyncController.save_failed_request_to_db(data)






    @staticmethod
    def send_omc_data_to_company_config(user_id:int, data: list[dict[str, str]], path: str
    ) -> None:
        """
        Send data to the user's specific company config.
        """
        company_config_url = SendController.get_user_config_url(user_id)
        url = f"http://{company_config_url['api_endpoint']}{path}"
        headers = {
            "Content-Type": "application/json",
            "API-KEY": company_config_url["api_key"],
        }
        for d in data:
            id = d.pop("id", None)
            response =  requests.post(
                url=url,
                headers=headers,
                json=d,
            )
            if response.status_code == 200:
                SyncController.save_successful_request_to_db(id, d, response.json())
            sync_logger.error(f"Failed to send data {d}: {response.text}")


    @staticmethod
    def update_omc_data_to_company_config(user_id: int, data: list[dict[str, str]], path: str
    ) -> None:
        """
        Send data to the user's specific company config.
        """

        company_config_url = SendController.get_user_config_url(user_id)
        url = f"http://{company_config_url['api_endpoint']}{path}"
        headers = {
            "Content-Type": "application/json",
            "API-KEY": company_config_url["api_key"],
        }
        for d in data:
            id = d.pop("id", None)
            response =  requests.put(
                url=url,
                headers=headers,
                json=d,
            )
            if response.status_code == 200:
                sync_logger.info(f"Successfully updated data {d}: {response.text}")
                return
            sync_logger.error(f"Failed to update data {d}: {response.text}")
            SendController.save_failed_to_update_request_to_db(id, d, False)


    @staticmethod
    def save_failed_to_update_request_to_db(resource_id: int ,request_data: dict[str, str], update_sync_status: bool= True) -> None:
        """
        Save the failed request to the database.
        """
        with CreateDBSession() as db:
            price_entry = db.query(PriceEntry).filter(
                PriceEntry.id == resource_id,
                PriceEntry.external_id.is_not(None),
            ).first()
            price_entry.update_sync_status = update_sync_status
            db.commit()
            db.refresh(price_entry)
            return price_entry
            


    
      
     

