"""
This is the main file of the project. It is the entry point of the application.

"""

from controller.sync import SyncController
from services import on_start



from core.start_app import AppBuilder

app = AppBuilder().get_app()



@app.on_event("startup")
async def startup_event():
    """
    This function is called when the application starts.
    It is used to initialize the application and start the background tasks.
    """
    SyncController.schedule_retry()
    on_start.create_default_admin()

    