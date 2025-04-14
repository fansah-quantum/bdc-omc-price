from datetime import datetime, timedelta
from typing import Tuple, Union

import jwt
from fastapi import security
import random


from errors.exception import AuthException
from config.setting import settings
from utils.sql import check_if_user_exist




class AuthToken:
    """
    This class is used to provide
    authentication and authorization functionality
    for the third party connectivity
    """

    @staticmethod
    def encode_auth_token(app_id: int) -> Union[Tuple[str, int], ValueError]:
        """
        Generates the auth token
        """
        try:
            payload = {
                "exp": datetime.utcnow()
                + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE),
                "iat": datetime.utcnow(),
                "sub": app_id,
            }
            return (
                jwt.encode(
                    payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
                ),
                settings.JWT_ACCESS_TOKEN_EXPIRE * 60,
            )
        except Exception as e:
            raise ValueError(e.args[0])
        

    @staticmethod
    def encode_auth_token_for_user(user: dict) -> str:
        """
        Generates the auth token for the user
        """
        try:
            payload = {
                "exp": datetime.utcnow()
                + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE),
                "iat": datetime.utcnow(),
                "sub": user.email
            }
            return jwt.encode(
                payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
            )
        except Exception as e:
            raise ValueError(e.args[0])

    @staticmethod
    def verify_auth_token(auth_token: str) -> str:
        print(auth_token)
        """
        Verifies the auth token
        """
        try:
            payload = jwt.decode(
                auth_token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthException(
                msg="Signature expired. Please log in again", code=403
            )
        except jwt.InvalidTokenError:
            raise AuthException(
                msg="Invalid token. Please log in again.", code=403
            )
        

    @staticmethod
    def generate_random_code() -> str:
        """Generate 6 digit random code"""
        return str(random.randint(100000, 999999))
    

    def generate_username(email: str)-> str:
            return email.split("@")[0]
    

    @staticmethod
    def verify_user_token(token: str)-> dict:
        """Verify admin token and return user data"""
        user_email_or_mobile = AuthToken.verify_auth_token(token)
        user_email = {"email": user_email_or_mobile["sub"]}
        db_user = check_if_user_exist(user_email)
        if not db_user:
            raise AuthException(msg="Invalid token", code=404)
        return db_user

    


    
bearerschema = security.HTTPBearer()



