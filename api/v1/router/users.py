from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends
from fastapi import BackgroundTasks
from schemas.users import ( UserUpdate,
                            UserLogin,
                            UserResetDetail, 
                            UserBase,
                            UserOut,
                            UserResetPassword,
                            VerifyOTP,
                            UserLoginOut, UserForgotPasswordOut)
from controller.users import UserController
from utils.auth import bearerschema, AuthToken





user_router = APIRouter()



@user_router.post("/users", response_model=UserLoginOut)
async def add_user(user_data: UserBase):
    user = UserController.add_user(user_data.model_dump(exclude_none=True))
    return user


@user_router.put("/users", response_model=UserOut)
async def update_user(user_data: UserUpdate, bearer_token = Depends(bearerschema)): # type: ignore
    user_info = AuthToken.verify_user_token(bearer_token.credentials)
    user = UserController.update_user(user_info, user_data.model_dump(exclude_none=True))
    return user


@user_router.post("/users/login", response_model=UserLoginOut)
async def login_user(user_data: UserLogin):
    user = UserController.login_user(user_data.model_dump(exclude_none=True))
    return user


@user_router.post("/users/request-otp", response_model=UserForgotPasswordOut)
async def request_otp(user_forgot_detail: UserResetDetail, bg_task: BackgroundTasks):
    otp = UserController.request_opt(user_forgot_detail.model_dump(exclude_none=True), bg_task)
    return otp


@user_router.post("/users/forgot-password", response_model=UserForgotPasswordOut)
async def forgot_password(user_reset_detail: UserResetPassword):
    user = UserController.forgot_password(user_reset_detail.model_dump(exclude_none=True))
    return user

@user_router.post("/users/verify-otp", response_model=UserForgotPasswordOut)
async def verify_otp(user_forgot_detail:VerifyOTP):
    user = UserController.verify_otp(user_forgot_detail.model_dump(exclude_none=True))
    return user


@user_router.get("/users/{user_id}",response_model=UserOut) 
async def get_user(user_id: int,
                    # bearer_token = Depends(bearerschema)
                    ):
    # AuthToken.verify_user_token(bearer_token.credentials)
    user = UserController.get_user_by_id(user_id)
    return user











