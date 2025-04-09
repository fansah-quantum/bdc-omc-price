from datetime import datetime
from typing import List, Dict
from utils import sql as sql

from fastapi.background import BackgroundTasks

from schemas.users import  UserUpdate, UserLogin, UserResetDetail, MyUserBase, UserResetPassword, VerifyOTP
from utils.common import get_password_hash, verify_password, get_user_data
from utils import sql
from models.users import User, PasswordResetToken
from models.bdcs import PriceEntry
from utils.session import CreateDBSession
from services.mail import MailService
from utils.auth import AuthToken
from errors.exception import AuthException
from config.setting import settings




class UserController:

    @staticmethod 
    def add_user(user_data: MyUserBase)-> Dict:
        
        """Add a new user to the database
        
        
        :param user_data: The user data to be added
        :type user_data: UserIn
        :return: The user data that was added
        :rtype: Dict
        """
        
        user_data["hashed_password"] = get_password_hash(user_data["password"])
        user_data = {k: v for k, v in user_data.items() if k != "password"}
        user_data["last_login"] = datetime.now() 
        user_name = AuthToken.generate_username(user_data["email"])
        user_data["full_name"] = user_name
        user_ob = User(**user_data)
        user = sql.add_object_to_database(user_ob)
        token = AuthToken.encode_auth_token_for_user(user)
        return {
            "user": user,
            "token": token
        }
        

    

    @staticmethod
    def update_user(user:dict, user_data: UserUpdate) -> Dict:
        
        """Update a user in the database
        
        :param user_id: The id of the user to be updated
        :type user_id: int
        :param user_data: The new user data
        :type user_data: UserIn
        :return: The updated user data
        :rtype: Dict
        """
        with CreateDBSession() as db:
            token = PasswordResetToken.verify_user_token(db, user.id, user_data["token"])
            if not token:
                raise AuthException(msg="Invalid token", code=401)
            if user_data.get("password"):
                user_data["hashed_password"] = get_password_hash(user_data["password"])
            user = User.update_user(db, user.id, user_data)
            return  user
        

    

    @staticmethod
    def verify_otp(user_data: VerifyOTP) -> Dict:
        """Verify the OTP for a user
        
        :param user_data: The user data to be verified
        :type user_data: UserIn
        :return: The user data that was verified
        :rtype: Dict
        """
        with CreateDBSession() as db:
            user = sql.check_if_user_exist(user_data)
            if not user:
                raise AuthException(msg="Invalid Token", code=404)
            token = PasswordResetToken.verify_user_token(db, user.id, user_data["token"])
            if not token:
                raise AuthException(msg="Invalid token", code=401)
            return {
                "message": "OTP verified successfully",
                "status": True
            }
            
           

            
            


        


    



    @staticmethod
    def login_user(user_data: UserLogin) -> Dict:
        """Login a user	"
        "    :param user_data: The user data to be logged in"
        "    :type user_data: Dict""
        "  :return: The user data that was logged in"""
        "    :rtype: Dict"

        login_type = "email" if user_data.get("email", None) else "mobile_number"
        login_filter = get_user_data(user_data)

        with CreateDBSession() as db:
            user = db.query(User).filter(login_filter.get(login_type)).first()
            if user:
                if user and verify_password(user_data["password"], user.hashed_password):
                    user.last_login = datetime.now()
                    token = AuthToken.encode_auth_token_for_user(user)
                    db.commit()
                    db.refresh(user)
                    return {
                        "user": user,
                        "token": token
                    }
            raise AuthException(msg="Invalid Credentials", code=401)

    

    @staticmethod
    def request_opt(user_reset_detail: UserResetDetail, bg: BackgroundTasks ):
        # login_type = "email" if user_reset_detail.get("email", None) else "mobile_number"
        # login_filter = get_user_data(user_reset_detail)

        with CreateDBSession() as db:
            user = sql.check_if_user_exist(user_reset_detail)
            if user:
                token = AuthToken.generate_random_code()
                PasswordResetToken.create_password_reset_token(db, user.id, token)
                db.commit()
                db.refresh(user)
                bg.add_task(MailService.send_email,
                subject="Password Credentials",
                email=user.email,
                msg="Reset your Credentials",
                content={"reset_code": user.password_reset_token.token, "email": user.email, "name": user.email},
               )

                return {
                   "message": "OTP sent successfully",
                   "status": True
                }
            raise AuthException(msg="Invalid Credentials", code=401)
        


    @staticmethod
    def forgot_password(user_reset_detail: UserResetPassword)-> str:
        login_type = "email" if user_reset_detail.get("email", None) else "mobile_number"
        login_filter = get_user_data(user_reset_detail)
        with CreateDBSession() as db:
            user = db.query(User).filter(login_filter.get(login_type)).first()
            if user:
                token = PasswordResetToken.verify_user_token(db, user.id, user_reset_detail["token"])
                if not token:
                    raise AuthException(msg="Invalid token", code=401)
                user.hashed_password = get_password_hash(user_reset_detail["password"])
                db.commit()
                db.refresh(user)
                return {
                    "message": "Password reset successfully",
                    "status": True
                }
            raise AuthException(msg="Invalid user credentials",code=404)
        


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

        



        