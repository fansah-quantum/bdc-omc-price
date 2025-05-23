from typing import Any, Dict
import json

import requests
from requests import Response
from passlib.context import CryptContext
from datetime import datetime, timezone

from errors.exception import InternalProcessingError
from tools.log import Log
from models import users
from models.bdcs import ProductType


common_logger = Log(name=f"{__name__}")


HEADERS = {
    "Authorization": "Basic c2VydmljZV9rZXk6c2VjcmV0",
    "x-subscription-key": "subscription_key",
}

TIMEOUT = 6000
BLACKLIST_STATUS_CODES = (500, 403, 422, 401)


def raise_internal_processing_error(response: Response) -> None:
    """
    Raise InternalProcessingError
    """
    if response.status_code in BLACKLIST_STATUS_CODES:
        common_logger.error(
            f"{raise_internal_processing_error.__name__} - {response.text}"
        )
        raise InternalProcessingError(
            msg={"message": "Internal Processing Error, Please try again"}, code=500
        )


def send_request(method: str, url: str, data: dict[Any, Any]= None) -> requests.Response:
    """
    Send a request to the specified url with the specified data and headers.
    """
    try:
        response = requests.request(
            method,
            url,
            json=data,
            headers=HEADERS,
            timeout=TIMEOUT,
        )
        raise_internal_processing_error(response)
        return response
    except InternalProcessingError:
        raise InternalProcessingError(
            msg={"message": "Internal Processing Error, Please try again"}, code=500
        )
    except Exception as e:
        common_logger.error(f"{send_request.__name__} - {str(e.args[0])}")
        raise InternalProcessingError(
            msg={"message": "Internal Server Error"}, code=500
        )
    


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)




def is_token_expired(recovery_token_time: datetime) -> bool:
    """
    Check if the recovery token time is before the current time.
    Ensures both datetimes are timezone-aware.
    
    Args:
        recovery_token_time (datetime): The datetime to check.
    
    Returns:
        bool: True if the token is expired, False otherwise.
    """
    if recovery_token_time.tzinfo is None:
        recovery_token_time = recovery_token_time.replace(tzinfo=timezone.utc)
    
    current_time = datetime.now(timezone.utc)
    return current_time > recovery_token_time



def get_user_data(user_data: Dict) -> Dict:
    if "email" in user_data and user_data["email"]:
        return {"email": users.User.email == user_data["email"]}
    return {"mobile_number": users.User.mobile_number == user_data["mobile_number"]}


def compute_unit_of_measurement(product_type:str )-> str : 
    """
    Compute the unit of measurement based on the product type.
    
    Args:
        product_type (str): The product type.
    
    Returns:
        str: The unit of measurement.
    """
    if product_type == "LPG":
        return "Ghana Cedis per Kg"
    return "Ghana Cedis per litre"
        



def remove_dict_dulicates(list_of_dicts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Remove duplicates from a list of dictionaries based on the 'id' key.
    
    Args:
        list_of_dicts (list[dict]): The list of dictionaries to process.
    
    Returns:
        list[dict]: The list of dictionaries with duplicates removed.
    """
    dict_value = list({json.dumps(d, sort_keys=True) for d in list_of_dicts})
    dict_value = [json.loads(d) for d in dict_value]
    return dict_value
   
