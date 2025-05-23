from typing import Dict, Union, List
from pydantic import BaseModel

from schemas.price_entry import OMCPriceEntryCreate, BDCPriceEntryCreate
from models.bdcs import PriceEntry, PriceEntryImage
from utils import sql
from utils.session import CreateDBSession
from utils.price_entry_filter import PriceEntryQuery
from services import s3
from models.users import User
from fastapi import UploadFile
from controller.sync import  SendController
from fastapi.background import BackgroundTasks
from config.setting import settings





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
    async def add_price_entry(user: "User", price_entry_data: Union[OMCPriceEntryCreate, BDCPriceEntryCreate], bg:BackgroundTasks, price_entry_images: List[UploadFile] = None) -> Dict:
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
                omc_base_data = {
                    "seller_type": "omc",
                    "user_id": user.id,
                    "omc_id": price_entry_data.omc_id,
                    "window": price_entry_data.window,
                    "station_id": price_entry_data.station_id,
                }
                
                price_entry = PriceEntry.add_multiple_omc_price_entry(
                    db_session, 
                    omc_base_data,
                    price_entry_data.product,
                    price_entry_images)
                bg.add_task(
                    SendController.send_omc_data_to_company_config,user.id,
                      [pr.omc_sync_json() for pr in price_entry], f"{settings.OMC_BDC_URL}/omc"
                      )
            else:
                bdc_base_data = {
                    "seller_type": "bdc",
                    "user_id": user.id,
                    "bdc_id": price_entry_data.bdc_id,
                    "window": price_entry_data.window,
                    "town_of_loading": price_entry_data.town_of_loading,
                    "transaction_term": price_entry_data.transaction_term,
                    "omc_id": price_entry_data.source_id,
                }
                price_entry = PriceEntry.add_multiple_bdc_price_entry(
                    db_session, 
                    bdc_base_data,
                    price_entry_data.product,
                    price_entry_images
                    )
                bg.add_task(
                    SendController.send_omc_data_to_company_config,user.id,
                      [pr.bdc_sync_json() for pr in price_entry], f"{settings.OMC_BDC_URL}/bdc"
                      )
            return price_entry
        

    @staticmethod
    async def update_price_entry(price_entry_data: Union[OMCPriceEntryCreate, BDCPriceEntryCreate], price_entry_id: int, seller_type: str ,bg: BackgroundTasks, new_price_entry_images: List[UploadFile] = None) -> Dict:
        """Update a price entry in the database

        :param price_entry_data: The price entry data to be updated
        :type price_entry_data: Union[OMCPriceEntryCreate, BDCPriceEntryCreate]
        :return: The updated price entry data
        :rtype: Dict
        """
        if new_price_entry_images:
            new_price_entry_images = await  s3.upload_multiple_images_to_s3(new_price_entry_images)
        
        seller_type_path = {
            "omc": f"{settings.OMC_BDC_URL}/omc/{price_entry_id}",
            "bdc": f"{settings.OMC_BDC_URL}/bdc/{price_entry_id}",
        }

        with CreateDBSession() as db_session:
            
            omc_bdc_price_entry_fields = price_entry_data.model_dump(exclude=["product", "images"], exclude_unset=True)
            if omc_bdc_price_entry_fields.get('source_id', None):
                omc_bdc_price_entry_fields['omc_id'] = omc_bdc_price_entry_fields.get('source_id')
                omc_bdc_price_entry_fields.pop('source_id')
            price_entry = PriceEntry.update_omc_price_entry(
                db_session=db_session, 
                price_entry_id=price_entry_id,
                seller_type=seller_type,
                product=price_entry_data.product,
                images=None,
                basic_fields=omc_bdc_price_entry_fields,
                new_price_entry_images=new_price_entry_images
                )
            if not price_entry:
                raise ValueError("Price entry not found")
            bg.add_task(
                SendController.update_omc_data_to_company_config, price_entry.user_id,
                [price_entry.omc_sync_json() if seller_type == 'omc' else price_entry.bdc_sync_json()], seller_type_path[seller_type]
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
            price_entries = PriceEntryQuery(db_session, params, user_id).paginate()
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
    
    @staticmethod
    async def delete_price_entry_image(entry_id: int, image_id: int) -> Dict:
        """Delete a price entry image from the database

        :param entry_id: The id of the price entry
        :type entry_id: int
        :param image_id: The id of the image to be deleted
        :type image_id: int
        :return: The deleted image data
        :rtype: Dict
        """
        with CreateDBSession() as db_session:
            price_entry = db_session.query(PriceEntry).filter(PriceEntry.id == entry_id).first()
            if not price_entry:
                raise ValueError("Price entry not found")
            image = db_session.query(PriceEntryImage).filter(PriceEntryImage.id == image_id).first()
            if not image:
                raise ValueError("Image not found")
            if image.image_url:
               response = await s3.delete_from_s3(image.image_url)
            db_session.delete(image)
            db_session.commit()
            db_session.refresh(price_entry)
            return {
                "message": "Image deleted successfully",
                "status": True
            }
        



        


        
        

    