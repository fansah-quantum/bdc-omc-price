import uuid
from typing import Dict


from boto3 import session
from botocore.exceptions import  ClientError
from fastapi import UploadFile


from tools.log import Log
from config.setting import settings




new_session = session.Session()
s3_logger = Log(name=f"{__name__}")




def get_s3_client():
    """Get an S3 client"""
    try:
        return new_session.client('s3',
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        endpoint_url=settings.S3_ENDPOINT_URL,
    )
    except Exception as e: 
        s3_logger.error(f"Could not establish s3 connection: {str(e)}")
        raise Exception("Cold not establish S3 connection")


def generate_url_for_frontend_upload(s3_session: session.Session, object_name: str, expiration=3600) -> str:
    """Generate a presigned URL for frontend upload
    
    :param s3_session: The S3 session
    :type s3_session: session.Session
    :param object_name: The object name
    :type object_name: str
    :param expiration: The expiration time, defaults to 3600
    :type expiration: int, optional
    :return: The presigned URL
    :rtype: str
    """
    try:
        response = s3_session.generate_presigned_url('put_object',Params={'Bucket':settings.S3_BUCKET_NAME,'Key': object_name, 'ACL': 'public-read'},ExpiresIn=expiration)

    except ClientError as e:
        s3_logger.error(f"Error generating presigned URL: {str(e)}")
        raise Exception("Error generating presigned URL")
    return response

        

async def convert_image_to_base64(file: UploadFile) -> str:
    base_b4_file = await file.read().decode("utf-8")
    return base_b4_file


async def upload_to_s3(file: UploadFile ) -> str:
    s3_client = get_s3_client()
    try:
        extention = file.filename.split(".")[-1]
        s3_key = f"omc-bdc/docs/{uuid.uuid4()}.{extention}"
        s3_client.upload_fileobj(file.file,settings.S3_BUCKET_NAME, s3_key)
        return {
            "s3_key": s3_key,
        }
    except ClientError as e:
        s3_logger.error(f"Error uploading file to S3: {str(e)}")
        raise Exception("Error uploading file to S3")



async def upload_multiple_images_to_s3(files: list[UploadFile]) -> list[dict]:
    s3_client = get_s3_client()
    uploaded_files = []
    for file in files:
        try:
            extention = file.filename.split(".")[-1]
            s3_key = f"omc-bdc/docs/{uuid.uuid4()}.{extention}"
            s3_client.upload_fileobj(file.file,settings.S3_BUCKET_NAME, s3_key)
            full_image_path = f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/{s3_key}"
            uploaded_files.append({
                "image_url": full_image_path,
            })
        except ClientError as e:
            s3_logger.error(f"Error uploading file to S3: {str(e)}")
            raise Exception("Error uploading file to S3")
        
    return uploaded_files
    

def create_presigned_url (s3_session: session.Session, object_name: str, expiration=3600):
    if cacher.get_value(object_name):
        return cacher.get_value(object_name)
    try:
        response = s3_session.generate_presigned_url('get_object',Params={'Bucket':settings.S3_BUCKET_NAME,'Key': object_name},ExpiresIn=expiration)
        cacher.set_value(object_name, response, expiration - 2)
    except ClientError as e:
        s3_logger.error(f"Error generating presigned URL: {str(e)}")
        raise Exception("Error generating presigned URL")
    return response



async def delete_from_s3(image_url: str) -> bool:
    """Delete a file from S3
    """
    s3_key = image_url.split(f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/")[-1]
    try:
        s3_client = get_s3_client()
        s3_client.delete_object(Bucket=settings.S3_BUCKET_NAME,Key=s3_key)
        return True
    except ClientError as e:
        s3_logger.error(f"Error deleting file from S3: {str(e)}")
        raise Exception("Error deleting file from S3")
    

    








