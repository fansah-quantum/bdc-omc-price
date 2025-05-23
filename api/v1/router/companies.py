from fastapi import APIRouter, Depends

from controller.companies import CompanyController
from schemas.companies import CompanyIn, CompanyOut, CompanyConfigIn, CompanyConfigOut, CompanyUpdate
from utils.auth import AuthToken, bearerschema



def verify_system_admin(bearer_token=Depends(bearerschema)):
    """Verify System Admin
    This method verifies if the user is a system admin
    """
    AuthToken.verify_system_admin(bearer_token.credentials)

company_router = APIRouter()
company_router.dependencies.append(Depends(verify_system_admin))



@company_router.post("/companies", response_model=CompanyOut, description="Add a new company, requires system admin privileges")
def add_company(company_data: CompanyIn):
    """Add Company
    This method adds a company to the database
    """
    company = CompanyController.add_company(company_data)
    return company


@company_router.get("/companies/{company_id}", response_model=CompanyOut, description="Get a company by ID, requires system admin privileges")
def get_company(company_id: str):
    """Get Company
    This method returns a company from the database
    """
    company = CompanyController.get_company(company_id)
    return company

@company_router.get("/companies", response_model=list[CompanyOut], description="Get all companies, requires system admin privileges")
def get_all_companies():
    """Get All Companies
    This method returns all companies from the database
    """
    companies = CompanyController.get_all_companies()
    return companies


@company_router.put("/companies/{company_id}", response_model=CompanyOut, description="Update a company by ID, requires system admin privileges")
def update_company(company_id: str, company_data: CompanyUpdate):
    """Update Company
    This method updates a company in the database
    """
    company = CompanyController.update_company(company_id, company_data)
    return company





