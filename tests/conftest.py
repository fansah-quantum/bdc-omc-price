import os
import sys
from typing import Any, Generator

import pytest
from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import sessionmaker


from api.v1.router import  health, sample_route as sam 
from core.setup import Base
from errors.exception import AuthException
from handler import exceptions as exec
from utils import session

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("TESTING", "True")
os.environ.setdefault("X_SUBSCRIPTION_KEY", "testing")
os.environ.setdefault("AUTH_SERVICE_API_USER", "testing")
os.environ.setdefault("AUTH_SERVICE_API_KEY", "testing")


def start_application_up():
    app = FastAPI()
    app.include_router(health.health_router)
    app.include_router(sam.sample_router)
    app.add_exception_handler(RequestValidationError, exec.validation_error_handler)
    app.add_exception_handler(ValidationError, exec.validation_error_handler)
    app.add_exception_handler(AuthException, exec.validation_exception_handler)
    app.add_exception_handler(ValueError, exec.validation_for_all_exceptions)
    app.add_exception_handler(HTTPException, exec.validation_http_exceptions)
    app.add_exception_handler(DBAPIError, exec.db_error_handler)
    app.add_exception_handler(IntegrityError, exec.db_error_handler)
    return app


SQLALCHEMY_DATABASE_URL = "sqlite:///testing.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionTesting = sessionmaker(autoflush=False, autocommit=False, bind=engine)


@pytest.fixture(scope="package")
def app() -> Generator[FastAPI, Any, None]:
    Base.metadata.create_all(engine)
    _app = start_application_up()
    yield _app
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="package")
def db_session(app: FastAPI) -> Generator[SessionTesting, Any, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionTesting(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="package")
def client(app: FastAPI, db_session):
    def _get_test_db():
        yield db_session

    app.dependency_overrides[session.CreateDBSession] = _get_test_db
    with TestClient(app) as client:
        yield client