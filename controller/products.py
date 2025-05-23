from datetime import datetime
from typing import Dict, Union
from models.products import Product
from utils.session import CreateDBSession
from utils.sql import add_object_to_database, update_object_in_database

class ProductController:


    @staticmethod
    def get_product(product_id: int) -> Union[Dict, None]:
        """Get a product from the database

        :param product_id: The ID of the product to be retrieved
        :type product_id: int
        :return: The product data that was retrieved or None if not found
        :rtype: Union[Dict, None]
        """
        with CreateDBSession() as db_session:
            product = Product.get_product_by_id(db_session, product_id)
            if not product:
                raise ValueError(f"Product with ID {product_id} not found")
            return product
        
    @staticmethod
    def get_all_products() -> list[Dict]:
        """Get all products from the database

        :return: A list of all products in the database
        :rtype: list[Dict]
        """
        with CreateDBSession() as db_session:
            products = Product.get_products(db_session)
            return products
        

    @staticmethod
    def add_product(product_name:dict)-> dict:
        product = Product(name=product_name.get('name'))
        return add_object_to_database(product)
    

    @staticmethod
    def delete_product(id: int):
        data = {'deleted_at': datetime.now()}
        return update_object_in_database(Product, 'id', id, data)
    

    @staticmethod
    def restore_product(id: int):
        data = {'deleted_at': None}
        return update_object_in_database(Product, 'id', id, data)





    