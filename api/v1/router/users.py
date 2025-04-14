from fastapi import APIRouter, Depends
from typing import Union
from schemas.users import (
    UserLogin,
    UserOut,
    UserLoginOut,
    UserMessage,
    LDAPLogin,
    ResetPin,
)
from controller.users import UserController
from utils.auth import bearerschema, AuthToken


user_router = APIRouter()


@user_router.post("/users", response_model=UserLoginOut)
async def add_user(user_data: LDAPLogin):
    user = UserController.sign_up_with_ldap(user_data.model_dump(exclude_none=True))
    return user


@user_router.post("/users/login", response_model=UserLoginOut)
async def login_user(user_data: Union[UserLogin, LDAPLogin]):
    user = UserController.login_with_ldap_cred_or_pin(
        user_data.model_dump(exclude_none=True)
    )
    return user


@user_router.put("/users", response_model=UserMessage)
async def create_reset_user_pin(data: ResetPin):
    # AuthToken.verify_user_token(bearer_token.credentials)
    user_pin = UserController.create_pin(data.model_dump(exclude_none=True))
    return user_pin


@user_router.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int, bearer_token=Depends(bearerschema)):
    AuthToken.verify_user_token(bearer_token.credentials)
    user = UserController.get_user_by_id(user_id)
    return user
