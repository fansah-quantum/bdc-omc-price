from utils.sql import get_all_objects_from_database, add_object_to_database
from models.sample_model import SampleModel
from schemas.sample_schema import SampleSchemaIn


class SampleController:

    """The processor
    The sample controller is responsible for processing the data
    """

    @staticmethod
    def get_sample() -> dict:
        """Get Sample
        This method returns a sample response
        """
        return get_all_objects_from_database(SampleModel)
    
    @staticmethod
    def create_sample(sample: SampleSchemaIn) -> dict:
        """Create Sample
        This method creates a sample response
        """
        sample = SampleModel(
            name=sample.name,
            description=sample.description
        )
        return add_object_to_database(sample)
    
