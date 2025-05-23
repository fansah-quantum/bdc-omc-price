from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List



class CompanyIn(BaseModel):
    name: str = Field(..., description="Name of the company")
    api_key: str = Field(..., description="API key for the company")
    api_user: str = Field(..., description="API user for the company")
    api_endpoint: str = Field(..., description="API endpoint for the company")

    



class CompanyOut(BaseModel):
    id: int = Field(..., description="ID of the company")
    name: str = Field(..., description="Name of the company")
    api_key: Optional[str] = Field(..., description="API key for the company")
    api_user: str = Field(..., description="API user for the company")
    api_endpoint: str = Field(..., description="API endpoint for the company")
    created_at: datetime = Field(..., description="Creation date of the company")



    @field_validator("name")
    def convert_to_lowercase(cls, v):
        return v.lower()
    

class CompanyConfigIn(BaseModel):
    api_key: str = Field(..., description="API key for the company")
    api_user: str = Field(..., description="API user for the company")
    api_endpoint: str = Field(..., description="API endpoint for the company")
    company_id: int = Field(..., description="ID of the company")



class CompanyConfigOut(BaseModel):
    api_user: Optional[str] = Field(None, description="API user for the company")
    api_endpoint: str = Field(..., description="API endpoint for the company")
    company_id: int = Field(..., description="ID of the company")



class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Name of the company")
    api_key: Optional[str] = Field(None, description="API key for the company")
    api_user: Optional[str] = Field(None, description="API user for the company")
    api_endpoint: Optional[str] = Field(None, description="API endpoint for the company")

