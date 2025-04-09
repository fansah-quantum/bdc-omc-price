import pytest 

from controller.sample_controller import SampleController

@pytest.mark.app_controller
def test_sample_controller_get():
    response = SampleController.get_sample()
    assert response is not None