from datetime import datetime
from typing import List, Dict
from utils import sql as sql


from schemas.users import  UserLogin,LDAPLogin
from utils.common import get_password_hash, verify_password, get_user_data
from utils import sql
from models.users import User
from utils.session import CreateDBSession
from utils.auth import AuthToken
from errors.exception import AuthException
from config.setting import settings
from utils.ldap import LDAPAuth
from typing import Union




class UserController:

    

    @staticmethod
    def get_user_by_id(id: int)-> "User":
        """Get a user by id
        
        :param id: The id of the user to be retrieved
        :type id: int
        :return: The user data
        :rtype: User
        """
        user = sql.get_object_by_id_from_database(User, id)
        if not user:
            raise AuthException(msg="User not found", code=404)
        return user
    


    @staticmethod
    def sign_up_with_ldap(user_data: LDAPLogin)-> Dict:

        
        
        user = LDAPAuth.authenticate_user(user_data['email'], user_data['password'])
        user_data.pop("password")
        user = User(**user_data)
        user = sql.add_object_to_database(user)
        token = AuthToken.encode_auth_token_for_user(user)
        return {
            "user": user,
            "token": token,
        }
    
    @staticmethod
    def create_pin(reset_data: dict)-> Dict:
        with CreateDBSession() as db:
            user = User.login_with_email_and_pin(db, reset_data["email"], None, get_user_only=True)
            if not user:
                raise AuthException(msg="User not found", code=404)
            user.pin = get_password_hash(reset_data["pin"])
            db.commit()
            db.refresh(user)
            return {
                "message": "Pin created successfully",
                "status": True
            }
        
    @staticmethod
    def login_with_ldap_cred_or_pin(data: Union[LDAPLogin, UserLogin])-> Dict:
        with CreateDBSession() as db:
        
            if "password" in data:
                print(True, "this is ldap instance")
                LDAPAuth.authenticate_user(data['email'], data['password'])
                user = User.login_with_email_and_pin(db, data['email'], None, True)
                token = AuthToken.encode_auth_token_for_user(user)
                return {
                    "user": user,
                    "token": token
                }
            user = User.login_with_email_and_pin(db, data['email'], data['pin'])
            if not user:
                raise AuthException(msg="Invalid Credentials", code=401)
            token = AuthToken.encode_auth_token_for_user(user)
            return {
                "user": user,
                "token": token
            }








        



        