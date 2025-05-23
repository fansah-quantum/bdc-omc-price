from typing import Dict, Union

from schemas.companies import CompanyIn, CompanyUpdate
from utils import sql 
from models.companies import Company




class CompanyController:
    @staticmethod
    def add_company(company_data: CompanyIn) -> Dict:
        """Add a new company to the database

        :param company_data: The company data to be added
        :type company_data: CompanyIn
        :return: The company data that was added
        :rtype: Dict
        """
        company_ob = Company(**company_data.model_dump())
        company = sql.add_object_to_database(company_ob)
        return company
    

    @staticmethod
    def get_company(company_id: str) -> Union[Dict, None]:
        """Get a company from the database

        :param company_id: The ID of the company to be retrieved
        :type company_id: str
        :return: The company data that was retrieved or None if not found
        :rtype: Union[Dict, None]
        """
        company = sql.get_object_by_id_from_database(Company, company_id)
        if not company:
            raise ValueError(f"Company with ID {company_id} not found")
        return company
    


    @staticmethod
    def get_all_companies() -> list[Dict]:
        """Get all companies from the database

        :return: A list of all companies in the database
        :rtype: list[Dict]
        """
        companies = sql.get_all_objects_from_database(Company)
        return companies
    
    @staticmethod
    def update_company(company_id: str, company_data: CompanyUpdate) -> Union[Dict, None]:
        """Update a company in the database

        :param company_id: The ID of the company to be updated
        :type company_id: str
        :param company_data: The new company data to be updated
        :type company_data: CompanyIn
        :return: The updated company data or None if not found
        :rtype: Union[Dict, None]
        """
        company = sql.update_object_in_database(Company, "id", company_id, company_data.model_dump(exclude_unset=True))
        if not company:
            raise ValueError(f"Company with ID {company_id} not found")
        return company
    

    