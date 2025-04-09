import pytest 
from pydantic import BaseModel

import utils.common as common 
from errors.exception import InternalProcessingError


class Response_Sample(BaseModel):
    status_code : int  
    text: str
data = {  'status_code' : 500,  'text': 'this is in  the blacklist'}
json_response = Response_Sample(**data)


@pytest.mark.utils 
def test_raise_internalprocessing_errror():
    with pytest.raises(Exception) as exec_info:
        common.raise_internal_processing_error(response=json_response)
    assert exec_info.value.code == 500
    assert isinstance(exec_info.value, InternalProcessingError)
# 
# 
@pytest.mark.utils
def test_send_request_internal_eeror():
    with pytest.raises(Exception) as exec_info:
        common.send_request("POST", "http://test:9000", data= {"data": 67})
    assert isinstance(exec_info.value, InternalProcessingError)
    assert exec_info.value.msg == {"message": "Internal Server Error"}
    # 
# 
@pytest.mark.utils
def test_send_request(): 
    responses = common.send_request("GET", 'http://localhost:8000/docs', data = {})
    assert responses is not None
