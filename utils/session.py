from sqlalchemy.orm import Session

from core import setup


class CreateDBSession:
    """
    Create a database session
    """

    def __init__(self):
        self.db_init = setup.DatabaseSetup()
        self.db = self.db_init.get_session()

    def __enter__(self) -> Session:
        return self.db()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.db().close()