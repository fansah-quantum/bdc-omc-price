from contextlib import contextmanager
# from ldap import Connection, Server

from fastapi.exceptions import HTTPException
from ldap3 import Connection, Server, ALL_ATTRIBUTES


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
            print(e)
            print("LDAP connection failed here first")
            raise HTTPException(status_code=401, detail="LDAP authentication failed",
            )

        

    @staticmethod
    def authenticate_user(email: str, password: str) -> bool:
        """
        Authenticate user using LDAP
        """
        with LDAPAuth.ldap_connection(email, password) as conn:
            data = {}
            if conn.bind():
                # check if the user is admin in LDAP company
                unique_name = email.split("@")[0]
                conn.search(
                    "ou=QUANTUM_GROUP,dc=quantumgroupgh,dc=com",
                    f"(&(objectClass=person)(sAMAccountName={unique_name}))",
                    attributes=ALL_ATTRIBUTES,
                )
                results = list(conn.entries)
                # take 
                print(results)
                return True
        
            else:
                raise HTTPException(status_code=401, detail="LDAP authentication failed")