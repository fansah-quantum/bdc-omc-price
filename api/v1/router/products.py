from typing import List

from fastapi import APIRouter, Depends
from controller.products import ProductController
from schemas.products import Product, ProductIn
from utils.auth import bearerschema, AuthToken


def verify_system_admin(bearer_token=Depends(bearerschema)):
    """Verify System Admin
    This method verifies if the user is a system admin
    """
    AuthToken.verify_system_admin(bearer_token.credentials)





product_router = APIRouter()
# product_router.dependencies.append(Depends(verify_system_admin))


@product_router.get("/products", response_model=List[Product])
async def get_products(
    # bearer_token=Depends(bearerschema) 
    ):
    """Get all products
    This method gets all products
    """
    # AuthToken.verify_user_token(bearer_token.credentials)
    return ProductController.get_all_products()


@product_router.get("/products/{product_id}", response_model=Product)
async def get_product_by_id(product_id: int, 
                            # bearer_token=Depends(bearerschema)
                            ):
    """Get product by id
    This method gets a product by id
    """
    # AuthToken.verify_user_token(bearer_token.credentials)
    return ProductController.get_product(product_id)


@product_router.post("/products", response_model=Product)
async def add_product(product_name: ProductIn, bearer_token=Depends(bearerschema)):
    AuthToken.verify_system_admin(bearer_token.credentials)
    return ProductController.add_product(product_name.model_dump())


@product_router.delete('/products/{id}', response_model=Product)
async def delete_product(id: int, bearer_token=Depends(bearerschema)):
    AuthToken.verify_system_admin(bearer_token.credentials)
    return ProductController.delete_product(id)


@product_router.put('/products/restore/{id}', response_model=Product)
async def restore_product(id: int, bearer_token=Depends(bearerschema)):
    AuthToken.verify_system_admin(bearer_token.credentials)
    return ProductController.restore_product(id)


