from typing import Dict, Union, List
from pydantic import BaseModel

from schemas.price_entry import OMCPriceEntryCreate, BDCPriceEntryCreate, OMCPriceEntryUpdate
from models.bdcs import PriceEntry
from utils import sql
from utils.session import CreateDBSession
from utils.price_entry_filter import PriceEntryQuery
from services import s3
from models.users import User
from fastapi import UploadFile



class PriceEntryController:

    @staticmethod
    def add_omc_price_entry(price_entry_data: OMCPriceEntryCreate) -> Dict:
        """Add a new price entry to the database

        :param price_entry_data: The price entry data to be added
        :type price_entry_data: OMCPriceEntryCreate
        :return: The price entry data that was added
        :rtype: Dict
        """
        


        with CreateDBSession() as db_session:
            price_entry = PriceEntry.add_omc_price_entry(
                db_session, 
                price_entry_data.user_id,
                price_entry_data.omc_id, 
                price_entry_data.window,
                price_entry_data.product,
                price_entry_data.station_location,
                price_entry_data.images)
            return price_entry

    @staticmethod

    def add_bdc_price_entry(price_entry_data: BDCPriceEntryCreate) -> Dict:
        """Add a new price entry to the database

        :param price_entry_data: The price entry data to be added
        :type price_entry_data: BDCPriceEntryCreate
        :return: The price entry data that was added
        :rtype: Dict
        """

        with CreateDBSession() as db_session:
            price_entry = PriceEntry.add_bdc_price_entry(
                db_session, 
                price_entry_data.user_id,
                price_entry_data.bdc_id, 
                price_entry_data.window,
                price_entry_data.product,
                price_entry_data.town_of_loading,
                price_entry_data.transaction_term,
                price_entry_data.images)
            return price_entry
        

    @staticmethod
    async def add_price_entry(user: "User", price_entry_data: Union[OMCPriceEntryCreate, BDCPriceEntryCreate], price_entry_images: List[UploadFile] = None) -> Dict:
        """Add a new price entry to the database

        :param price_entry_data: The price entry data to be added
        :type price_entry_data: Union[OMCPriceEntryCreate, BDCPriceEntryCreate]
        :return: The price entry data that was added
        :rtype: Dict
        """

        if price_entry_images:
            price_entry_images = await  s3.upload_multiple_images_to_s3(price_entry_images)

        with CreateDBSession() as db_session:
            if isinstance(price_entry_data, OMCPriceEntryCreate):
                
                price_entry = PriceEntry.add_omc_price_entry(
                    db_session, 
                    user.id,
                    price_entry_data.omc_id, 
                    price_entry_data.window,
                    price_entry_data.product,
                    price_entry_data.station_location,
                    price_entry_images)
            else:
                price_entry = PriceEntry.add_bdc_price_entry(
                    db_session, 
                    user.id,
                    price_entry_data.bdc_id, 
                    price_entry_data.window,
                    price_entry_data.product,
                    price_entry_data.town_of_loading,
                    price_entry_data.transaction_term,
                    price_entry_images
                    )
             
            #  todo: send data to consumer endpoint based on the data type
             

            return price_entry
        

    @staticmethod
    def update_price_entry(price_entry_data: Union[OMCPriceEntryCreate, BDCPriceEntryCreate], price_entry_id: int) -> Dict:
        """Update a price entry in the database

        :param price_entry_data: The price entry data to be updated
        :type price_entry_data: Union[OMCPriceEntryCreate, BDCPriceEntryCreate]
        :return: The updated price entry data
        :rtype: Dict
        """

        with CreateDBSession() as db_session:
            
            omc_bdc_price_entry_fields = price_entry_data.model_dump(exclude=["product", "images"], exclude_unset=True)
            price_entry = PriceEntry.update_omc_price_entry(
                db_session=db_session, 
                price_entry_id=price_entry_id,
                product=price_entry_data.product,
                images=price_entry_data.images,
                basic_fields=omc_bdc_price_entry_fields
                )
            return price_entry
        

    @staticmethod
    def get_price_entries(params: BaseModel,user_id: int ) -> Dict:
        """Get price entries from the database

        :param params: The parameters to filter the price entries
        :type params: OMCBDCFilterParams
        :return: The price entries
        :rtype: Dict
        """

        with CreateDBSession() as db_session:
            price_entries = PriceEntryQuery(db_session, params).paginate()
            return price_entries
        

    @staticmethod
    def get_presigned_url(image_names: List[str]) -> Dict:
        """Get a presigned URL for an image

        :param image_name: The name of the image
        :type image_name: str
        :return: The presigned URL
        :rtype: Dict
        """
        presigned_url_list  = []
        for image in image_names:
            url = s3.generate_url_for_frontend_upload(s3.get_s3_client(), image, 3600)
            presigned_url_list.append({"image_name": image, "url": url})
            # presigned_url_list.append({image: url})
        print(presigned_url_list)
        return presigned_url_list
    

    @staticmethod
    def get_price_entry(price_entry_id: int) -> Dict:
        """Get a price entry from the database

        :param price_entry_id: The id of the price entry
        :type price_entry_id: int
        :return: The price entry
        :rtype: Dict
        """
        
        price_entry = sql.get_object_by_id_from_database(PriceEntry, price_entry_id)
        return price_entry


    @staticmethod
    async def upload_image(file) -> str:
        """Upload an image to S3

        :param file: The image file
        :type file: UploadFile
        :return: The URL of the image
        :rtype: str
        """
        url = await s3.upload_to_s3(file)
        return url
    
            


        
        

    