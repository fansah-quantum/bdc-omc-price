import pytest 
from datetime import datetime



from models.sample_model import SampleModel

sample_data = {
    "id": 1,
    "name": "sample",
    "description": "sample",
    "created_at": datetime.now(),
    "updated_at": datetime.now(),
    "deleted_at": None
}


@pytest.mark.model
def test_sample_model():
    assert SampleModel.__tablename__ == 'sample'
    assert SampleModel.__mapper__.has_property('id')
    assert SampleModel.__mapper__.has_property('name')
    assert SampleModel.__mapper__.has_property('description')
    assert SampleModel.__mapper__.has_property('created_at')
    assert SampleModel.__mapper__.has_property('updated_at')

    sample_instance = SampleModel(**sample_data)
    assert str(sample_instance) == '1-sample'
    

    
