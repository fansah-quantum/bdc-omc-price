from fastapi import APIRouter, Depends
from schemas.users import (
    UserLogin,
    UserOut,
    UserLoginOut,
    CompanyUser,
    SystemAdminOut,
)
from controller.users import UserController
from utils.auth import bearerschema, AuthToken
from errors.exception import AuthException


user_router = APIRouter()



@user_router.post("/system-admin/login/", response_model=SystemAdminOut, description="Login System Admin")
async def login_system_admin(data: UserLogin):
    """Login System Admin
    This method logs in a system admin and returns a token
    """
    user = UserController.login_system_admin(data)
    return user


# @user_router.post("/company-admin", response_model=UserOut, description="Add Company Admin, requires system admin privileges")
# async def add_company_admin(data: CompanyAdminIn, bearer_token=Depends(bearerschema)):
#     """Add Company Admin
#     This method adds a company admin to the database
#     """
#     AuthToken.verify_system_admin(bearer_token.credentials)
#     user = UserController.add_company_admin(data.model_dump())
#     return user

@user_router.post("/users/login", response_model=UserLoginOut, description="Login Company Admin, use this endpoint to login users")
async def login(data: UserLogin):
    """Login Company Admin
    This method logs in a company admin and returns a token
    """
    user = UserController.login(data)
    return user


# @user_router.post("/users", response_model=UserOut, description="Add User, requires company admin privileges")
# async def add_user(data: CompanyAllowedUsers, 
#                    bearer_token=Depends(bearerschema)):
#     """Add User
#     This method adds a user to the database
#     """
#     admin = AuthToken.verify_user_token(bearer_token.credentials)
#     if not admin.is_admin:
#         raise AuthException("You are not authorized to add users")
#     user = UserController.add_user(data.model_dump(), admin.company_id)
#     return user



@user_router.post("/users", response_model=UserOut, description="Add User(company admin or usual user), requires company admin privileges or system admin privileges")
async def add_user(data: CompanyUser, bearer_token=Depends(bearerschema)):
    """Add User
    This method adds a user to the database
    """
    if data.is_admin is True:
        AuthToken.verify_system_admin(bearer_token.credentials)
    else:
        company_admin = AuthToken.verify_user_token(bearer_token.credentials)
        if not company_admin.is_admin:
            raise AuthException("You are not authorized to add users")
    company_id = data.company_id if data.company_id else company_admin.company_id
    user_data = data.model_dump(exclude_none=True)
    user_data["company_id"] = company_id
    user = UserController.add_user(data.model_dump())
    return user



@user_router.put("/users/{user_id}", response_model=UserOut, description="Update User(company admin or usual user), requires company admin privileges")
async def update_user(user_id: int, data: CompanyUser, bearer_token=Depends(bearerschema)):
    company_admin = None
    system_admin = AuthToken.just_verify_system_admin(bearer_token.credentials)
    if system_admin:
        user =UserController.update_user(user_id, data.model_dump(exclude_unset=True), None)
        return user
    else:
        company_admin = AuthToken.verify_user_token(bearer_token.credentials)
        if not company_admin.is_admin:
            raise AuthException("You are not authorized to update users")
    user_data = data.model_dump(exclude_none=True)
    user_data["name"] = None
    user = UserController.update_user(user_id, user_data, company_admin.company_id if company_admin else None)
    return user







@user_router.get("/users", response_model=list[UserOut], description="Get all users, requires company admin privileges")
def get_all_users(bearer_token=Depends(bearerschema), company_id: int = None):
    """Get All Users
    This method returns all users from the database
    """
    if company_id:
        company_admin = AuthToken.verify_user_token(bearer_token.credentials)
        if not company_admin.is_admin or company_id != company_admin.company_id:
            raise AuthException("You are not authorized to get users")
        else:
            AuthToken.verify_system_admin(bearer_token.credentials)
    users = UserController.get_all_users(company_id)
    return users



@user_router.get("/users/{user_id}", response_model=UserOut, description="Get user by ID, requires company  admin or normal user privileges")
def get_user(user_id: int, bearer_token=Depends(bearerschema)):
    """Get User
    This method returns a user from the database
    """
    user_info = AuthToken.verify_user_token(bearer_token.credentials)
    if user_info.id != user_id:
        raise AuthException("You are not authorized to get this user")
    user = UserController.get_user(user_id)
    return user
    












