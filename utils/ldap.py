from contextlib import contextmanager
from ldap3 import Connection


class LDAPAuth:
    @staticmethod
    @contextmanager
    def ldap_connection():
        """
        Context manager for LDAP connection
        """
        try:
            ldsp_server = Server(settings.LDAP_SERVER)
            with Connection(
                ldsp_server,
                user=settings.LDAP_USER,
                password=settings.LDAP_PASSWORD,
            ) as conn:
                yield conn
        
        except Exception as e:
            raise ValueError(e.args[0])
        finally:
            conn.unbind()