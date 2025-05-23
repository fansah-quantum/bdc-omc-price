from datetime import datetime, timedelta
from sqlalchemy import desc, asc

from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from fastapi_pagination import Params
from fastapi_pagination.ext.sqlalchemy import paginate as sql_paginate
from models.bdcs import PriceEntry, ProductPrice
from pydantic import BaseModel


from models.bdcs import ProductType

class PriceEntryQuery:
    def __init__(self, db_session: Session, params: BaseModel, user_id: int = None):
        self.db_session = db_session
        self.params = params
        self.user_id = user_id


        

    def apply_filters(self, query):
        
        needs_variation_join = any([
            getattr(self.params, 'product_type', None)
        ])
        if needs_variation_join:
            query = query.join(ProductPrice)


        if self.params.seller_type:
            query = query.filter(PriceEntry.seller_type == self.params.seller_type)
        if self.params.product_type:
            query = query.filter(ProductPrice.product_type == self.params.product_type)
        if self.params.window:
            query = query.filter(PriceEntry.window == self.params.window)
        if self.params.transaction_term:
            query = query.filter(PriceEntry.transaction_term == self.params.transaction_term)
        return query
    

    def apply_sorting(self, query):
        if not self.params.sort_by:
            query = query.order_by(desc(PriceEntry.created_at))
        else:
            sort_field = getattr(PriceEntry, self.params.sort_by, None)
            if sort_field:
                if self.params.sort_order == "asc":
                    query = query.order_by(asc(sort_field))
                else:
                    query = query.order_by(desc(sort_field))
        return query


    def apply_date_range_filter(self, query):
        if self.params.from_date and self.params.to_date:
            from_date = datetime.strptime(self.params.from_date, "%Y-%m-%d")
            to_date = datetime.strptime(self.params.to_date, "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)
            query = query.filter(PriceEntry.created_at.between(from_date, to_date))
        return query
    

    def paginate(self):
        query = self.db_session.query(PriceEntry).filter(PriceEntry.user_id == self.user_id)
        query = self.apply_filters(query)
        query = self.apply_sorting(query)
        query = self.apply_date_range_filter(query)
        return query.all()



    



    