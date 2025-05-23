from utils import sql

from models.users import SystemAdmin
from config.setting import settings





def create_default_admin() -> None:
    
    """Create default data in the database if it doesn't exist."""
    system_admin = sql.get_object_by_id_from_database(SystemAdmin, 1)
    if not system_admin:
        SystemAdmin.add_system_admin(
        1,
        settings.SYSTEM_ADMIN_EMAIL,
        settings.SYSTEM_ADMIN_NAME,
        settings.SYSTEM_ADMIN_PASSWORD,
    )


