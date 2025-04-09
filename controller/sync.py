import requests

from utils.session import CreateDBSession
from models.bdcs import PriceEntry
from apscheduler.schedulers.background import BackgroundScheduler




class SyncController:

    # def __init__(self, url: str, headers: dict[str, str], timeout: int):
    #     self.url = url
    #     self.headers = headers
    #     self.timeout = timeout


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
            raise ValueError(f"Unable to send data {response.text}")
        SyncController.save_failed_request_to_db(data)
            

    @staticmethod
    def save_failed_request_to_db(request_data: dict[str, str]) -> None:
        """
        Save the failed request to the database.
        """
        with CreateDBSession() as db:
            price_entry = db.query(PriceEntry).filter_by(
                id=request_data.id
            ).first()
            price_entry.sync_status = True
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
            for bdcs in failed_bdcs:
                response = SyncController.send_request("post", "http://localhost:300", bdcs)
                if response.status_code != 200:
                    print(response.json())
                SyncController.save_failed_request_to_db(bdcs)
                

    @staticmethod
    def retry_failed_omcs() -> None:
        """
        Retry all failed dbcs syncs.
        """
        with CreateDBSession() as db:
            failed_omcs = PriceEntry.get_all_failed_price_entries(db, "omc")
            for omcs in failed_omcs:
                response = SyncController.send_request("post", "http://localhost:300", omcs)
                if response.status_code != 200:
                    print(response.json())
                SyncController.save_failed_request_to_db(omcs)
                
                    


    @staticmethod
    def schedule_retry():
        """
        Schedule the retry_failed_requests function to run at 12 AM every day.
        """
        scheduler = BackgroundScheduler()
        scheduler.add_job(SyncController.retry_failed_bdcs, "cron", hour=15, minute=55)
        scheduler.add_job(SyncController.retry_failed_omcs, "cron", hour=15, minute=55)
        scheduler.start()
        
      
    

