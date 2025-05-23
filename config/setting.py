from typing import Union

from pydantic_settings import BaseSettings


"""
This class is used to store the application settings.
Feel free to add more settings as needed. and make sure to add them to the .env file
You can also add more configurations to the class Config
You can change the class name to whatever you want, but make sure to change it in the core/setup.py file

"""

class Settings(BaseSettings):
    version: str = "1.0"
    releaseId: str = "1.1"
    API_PREFIX: str = "/api/v1"
    APP_NAME: str = "BDC-OMC Price Service"
    API_TITLE: str = "BDC-OMC Price API"
    APP_DESCRIPTION: str = "This is the API for the BDC-OMC Price Service"
    DATABASE_URL: str = "sqlite:///./test.db"
    POSTGRES_URL: str 
    TESTING: bool = True
    AWS_ACCESS_KEY: str 
    AWS_SECRET_KEY: str 
    S3_ENDPOINT_URL: str
    S3_BUCKET_NAME: str = "omc-bdc-price"
    S3_REGION : str = "S3_REGION"
    X_SUBSCRIPTION_KEY: str=  "tester"
    AUTH_SERVICE_API_USER: str = "tester"
    AUTH_SERVICE_API_KEY: str = "tester"
    REDIS_HOST: str
    REDIS_PORT: Union[int, str] = 6379
    REDIS_DB: Union[int, str] = 0
    REDIS_PASSWORD: str = ""
    JWT_SECRET_KEY: str 
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE: int = 3600
    DEFAULT_PASSWORD: str = "123456789"
    LDAP_SERVER: str 
    OMC_BDC_URL: str
    OMC_SYNC_URL: str 
    BDC_SYNC_URL: str 
    OMC_API_KEY: str 
    BDC_API_KEY: str
    STATIONS_SYNC_URL: str 
    STATIONS_API_KEY: str 
    SYSTEM_ADMIN_EMAIL: str 
    SYSTEM_ADMIN_PASSWORD : str 
    SYSTEM_ADMIN_NAME : str 
    

    class Config:
        env_file = ".env"


settings = Settings()