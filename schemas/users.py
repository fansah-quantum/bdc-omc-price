from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, Field

class UserType(str, Enum):
    MARKETING_STAFF = "marketing_staff"
    POWER_FUELS_STAFF = "power_fuels_staff"

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    mobile_number: Optional[str] = Field(None, min_length=10, max_length=15)
    user_type: UserType
    password: str = Field(..., min_length=8)

    @field_validator('email')
    def validate_email(cls, v):
        if v is None and cls.mobile_number is None:
            raise ValueError("Either email or mobile number must be provided")
        return v
    @field_validator('mobile_number')  
    def check_mobile_number_not_null(cls, v):
        if v is None and cls.email is None:
            raise ValueError("Either email or mobile number must be provided")
        return v

    @field_validator('password')
    def password_must_contain_upper(cls, v):
        if len(v) < 8 or not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least 1 uppercase letter and be at least 8 characters')
        return v






# class UserLogin(BaseModel):
#     email: Optional[EmailStr] = None
#     mobile_number: Optional[str] = Field(None, min_length=10, max_length=15)
#     password: str = Field(..., min_length=8)

#     @field_validator('email')
#     def validate_email(cls, v):
#         if v is None and cls.mobile_number is None:
#             raise ValueError("Either email or mobile number must be provided")
#         return v
#     @field_validator('mobile_number')
#     def check_mobile_number_not_null(cls, v):
#         if v is None and cls.email is None:
#             raise ValueError("Either email or mobile number must be provided")
#         return v


#     @field_validator('mobile_number')
#     def validate_mobile_number(cls, v):
#         if v is not None and not v.isdigit():
#             raise ValueError("Mobile number must contain only digits")
#         return v

#     @field_validator('password')
#     def password_must_contain_upper(cls, v):
#         if len(v) < 8 or not any(char.isupper() for char in v):
#             raise ValueError('Password must contain at least 1 uppercase letter and be at least 8 characters')
#         return v



# class MyUserBase(UserLogin):
#     email: Optional[EmailStr] = None
#     mobile_number: Optional[str] = Field(None, min_length=10, max_length=15)
#     user_type: UserType
#     password: str = Field(..., min_length=8)

#     @field_validator('email')
#     def validate_email(cls, v):
#         if v is None and cls.mobile_number is None:
#             raise ValueError("Either email or mobile number must be provided")
#         return v
#     @field_validator('mobile_number')  
#     def check_mobile_number_not_null(cls, v):
#         if v is None and cls.email is None:
#             raise ValueError("Either email or mobile number must be provided")
#         return v

    

# class UserIn(MyUserBase):
#     pass


# class UserResetDetail(BaseModel):
#     email: Optional[EmailStr]= None
#     mobile_number: Optional[str] = None
    
    


#     @field_validator('email')
#     def validate_email(cls, v):
#         if v is None and cls.mobile_number is None:
#             raise ValueError("Either email or mobile number must be provided")
#         return v
#     @field_validator('mobile_number')
#     def check_mobile_number_not_null(cls, v):
#         if v is None and cls.email is None:
#             raise ValueError("Either email or mobile number must be provided")
#         return v
    

# class UserResetPassword(UserResetDetail):
#     password: str = Field(..., min_length=8)
#     token: str

#     @field_validator('password')
#     def password_must_contain_upper(cls, v):
#         if len(v) < 8 or not any(char.isupper() for char in v):
#             raise ValueError('Password must contain at least 1 uppercase letter and be at least 8 characters')
#         return v
    

# class VerifyOTP(UserResetDetail):
#     token: str = Field(..., min_length=6, max_length=6)

#     @field_validator('token')
#     def validate_otp(cls, v):
#         if not v.isdigit():
#             raise ValueError("OTP must contain only digits")
#         return v
    




class LDAPLogin(BaseModel):
    email: EmailStr = Field(...)
    password: Optional[str]  = Field(None, min_length=8)

    
    # @field_validator('password')
    # def validate_password(cls, v):
    #     if v is None and cls.pin is None:
    #         raise ValueError("Either pin or password must be provided")
    #     return v


class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str  = Field()
    


class ResetPin(BaseModel):
    email: EmailStr = Field(...)
    pin: str = Field(..., min_length=6, max_length=6)

        
    


    


    
    








    



class UserUpdate(UserLogin):
    password: Optional[str] = None
    token: str
    full_name: Optional[str] = None





class UserOut(BaseModel):
    id: int
    email: Optional[EmailStr]
    created_at: datetime
    name: Optional[str]
    company_id: Optional[int]
    is_admin: Optional[bool] = False
    
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None


class UserLoginOut(BaseModel):
    user: UserOut
    token: str 


class UserMessage(BaseModel):
    message: str
    status: bool




class CompanyAdminIn(BaseModel):
    email: EmailStr = Field(...)
    company_id: int = Field(...) 
    name: str = Field(...)


class CompanyAllowedUsers(BaseModel):
    email: EmailStr = Field(...)

class AdminUser(BaseModel):
    id: int
    email: Optional[EmailStr]
    created_at: datetime
    name: Optional[str]



class SystemAdminOut(BaseModel):
    token: str
    user: AdminUser



class CompanyUser(BaseModel):
    email: EmailStr = Field(...)
    is_admin: Optional[bool] = False
    company_id: Optional[int] = None

class CompanyUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    is_admin: Optional[bool] = False
    company_id: Optional[int] = None
    

