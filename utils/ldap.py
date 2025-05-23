from contextlib import contextmanager

from fastapi.exceptions import HTTPException
from ldap3 import Connection, Server, ALL_ATTRIBUTES
from models.users import User


from config.setting import settings


class LDAPAuth:
    @staticmethod
    @contextmanager
    def ldap_connection(email: str, password: str):
        """
        Context manager for LDAP connection
        """
        try:
            ldap_server = Server(settings.LDAP_SERVER)
            with Connection(ldap_server, user= email, password = password) as conn:
                yield conn
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"LDAP authentication failed {e}",
            )

        

    @staticmethod
    def authenticate_user(email: str, password: str) -> dict:
        """
        Authenticate user using LDAP
        """
        with LDAPAuth.ldap_connection(email, password) as conn:
            data = {}
            if conn.bind():
                unique_name = email.split("@")[0]
                conn.search(
                    "ou=QUANTUM_GROUP,dc=quantumgroupgh,dc=com",
                    f"(&(objectClass=person)(sAMAccountName={unique_name}))",
                    attributes=ALL_ATTRIBUTES,
                )
                results = list(conn.entries)
                db_user_data = User.get_user_by_email(email)
                if not db_user_data:
                    raise HTTPException(status_code=401, detail="User not found")
                distinguished_name = results[0]["distinguishedName"][0]
                company_name = [part.split("=")[1] for part in distinguished_name.split(",") if part.startswith("OU=")][-1]
                data["name"] = results[0]["name"][0]
                data["email"] = email
                data["company"] = company_name 
                data["is_admin"] = db_user_data.is_admin
                data["company_id"] = db_user_data.company_id
                data["user_id"] = db_user_data.id
                data["company_name"] = company_name
                return data
        
            else:
                raise HTTPException(status_code=401, detail="LDAP authentication failed")