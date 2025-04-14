
from typing import Any,Dict, Union

from utils import session
from models.users import User
from utils.common import get_user_data


def add_object_to_database(item: Any) -> dict:
    """
    Add an item to the database
    Args:
        db (object): contain the session for the
                database operations
        item(Any): The item to insert
    returns:
        bool
    """
    with session.CreateDBSession() as database_session:
        database_session.add(item)
        database_session.commit()
        database_session.refresh(item)
        return item
    
def get_all_objects_from_database(model: Any) -> Any:
    """
    Get all items from the database
    Args:
        db (object): contain the session for the
                database operations
        model(Any): The model to query
    returns:
        Any
    """
    with session.CreateDBSession() as database_session:
        return database_session.query(model).all()
    
def get_object_by_id_from_database(model: Any, id: int) -> Any:
    """
    Get an item from the database by id
    Args:
        db (object): contain the session for the
                database operations
        model(Any): The model to query
        id(int): The id of the item to query
    returns:
        Any
    """
    with session.CreateDBSession() as database_session:
        return database_session.query(model).filter(model.id == id).first()
    

    def feel_free_to_create_more_functions():
        pass


def update_object_in_database(db_class, query_param: str, value: Any, update_data: Dict[str, Any]):
        """
        Update an object in the database.
        
        :param db_session: SQLAlchemy session object
        :param db_class: SQLAlchemy model class
        :param query_param: The field to query by
        :param value: The value to query for
        :param update_data: A dictionary of fields to update
        :return: The updated instance or None if not found
        """
        with session.CreateDBSession() as db_session:
            instance = db_session.query(db_class).filter(getattr(db_class, query_param) == value).first()
            if instance:
                for key, val in update_data.items():
                    setattr(instance, key, val)
                db_session.commit()
                db_session.refresh(instance)
                return instance
            return None
        

def check_if_user_exist(user_email: Dict[str , Any]) ->Union[Dict, None]:
    """
    Check if a user exists in the database
    Args:
        db (object): contain the session for the
                database operations
        user_email_or_mobile(Dict): The user email or mobile number
    returns:
        Any
    """
    with session.CreateDBSession() as db_session:
        user = db_session.query(User).filter(User.email == user_email['email']).first()
        return user if user else None

        