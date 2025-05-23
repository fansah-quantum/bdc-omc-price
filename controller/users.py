from typing import List, Dict
from utils import sql as sql


from schemas.users import  UserLogin
from utils.common import  verify_password
from models.users import User, SystemAdmin
from utils.session import CreateDBSession
from utils.auth import AuthToken
from errors.exception import AuthException
from config.setting import settings
from utils.ldap import LDAPAuth
from typing import Union





class UserController:

    @staticmethod
    def add_company_admin(user_data: dict):
        """Add a new company admin to the database

        :param user_data: The user data to be added
        :type user_data: dict
        :return: The user data that was added
        :rtype: dict
        """
        user_ob = User(**user_data, is_admin=True)
        user = sql.add_object_to_database(user_ob)
        return user
    

    @staticmethod
    def add_user(user_data: dict) -> Dict:
        """Add a new user to the database

        :param user_data: The user data to be added
        :type user_data: dict
        :return: The user data that was added
        :rtype: dict
        """
        user_ob = User(**user_data)
        user = sql.add_object_to_database(user_ob)
        return user
    


    

    @staticmethod
    def login(data: UserLogin) -> Dict:
        """Login a user and return a token

        :param data: The user data to be logged in
        :type data: UserLogin
        :return: The user data that was logged in
        :rtype: dict
        """
        with CreateDBSession() as db_session:
            db_user = User.get_user_by_email(data.email)
            if not db_user: 
                raise AuthException(msg="User not found", code = 404)
            user = LDAPAuth.authenticate_user(data.email, data.password)
            if not db_user.name:
                sql.update_object_in_database(User, "email", data.email, {"name": user["name"]})
            token = AuthToken.encode_auth_token_for_user(user)
            return {
                "token": token, 
                "user": db_user
            }
        

    @staticmethod
    def login_system_admin(data: UserLogin) -> Dict:
        """Login a system admin and return a token

        :param data: The user data to be logged in
        :type data: UserLogin
        :return: The user data that was logged in
        :rtype: dict
        """
        db_user = SystemAdmin.get_system_admin_by_email(data.email)
        if not db_user: 
            raise AuthException(msg="User not found", code = 404)
        if not verify_password(data.password, db_user.password):
            raise AuthException(msg="Invalid password", code = 401)
        token = AuthToken.encode_auth_token_for_user({"email": db_user.email})
        return {
            "token": token, 
            "user": db_user
        }
    


    def get_all_users(company_id: int = None) -> List[Dict]:
        """Get all users from the database

        :param company_id: The company id to get users from
        :type company_id: int
        :return: The user data that was retrieved
        :rtype: list
        """
        with CreateDBSession() as db_session:
            query = db_session.query(User)
            if company_id:
                query = query.filter(User.company_id == company_id)
            users = query.all()
            return [user for user in users]
        
    @staticmethod
    def get_user(user_id: int) -> Dict:
        """Get a user from the database

        :param user_id: The user id to get
        :type user_id: int
        :return: The user data that was retrieved
        :rtype: dict
        """
        user = sql.get_object_by_id_from_database(User, user_id)
        if not user:
            raise AuthException(msg="User not found", code = 404)
        return user
    

    @staticmethod
    def update_user(user_id: int, user_data: dict, company_id: Union[int, None]) -> Dict:
        """Update a user in the database

        :param user_id: The user id to be updated
        :type user_id: int
        :param user_data: The new user data to be updated
        :type user_data: dict
        :return: The updated user data or None if not found
        :rtype: dict
        """
        if company_id:
            user = sql.get_object_by_id_from_database(User, user_id)
            if not user or user.company_id != company_id:
                raise AuthException(msg="User not found", code = 404)
        user = sql.update_object_in_database(User, "id", user_id, user_data)
        if not user:
            raise AuthException(msg="User not found", code = 404)
        return user

