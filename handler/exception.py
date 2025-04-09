from typing import Union

import fastapi
from fastapi.exceptions import HTTPException, RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import DBAPIError, IntegrityError

from errors.exception import AuthException
from tools.log import Log

exception_logger = Log(name=f"{__name__}")


def validation_error_handler(
    request: fastapi.Request, exec: Union[ValidationError, RequestValidationError]
) -> fastapi.responses.JSONResponse:
    """Validation Error Handler

    This method is serves a custom error handler
    for all validation errors raised by pydantic
    """
    error = exec.errors()[0]
    field = error.get("loc")[-1]
    message = error.get("msg")

    error_msg = f"Invalid {field}: {message}"
    exception_logger.error(f"{validation_error_handler.__name__} - {error_msg}")
    return fastapi.responses.JSONResponse(
        status_code=422, content={"message": error_msg}
    )


def validation_for_all_exceptions(
    request: fastapi.Request, exec: ValueError
) -> fastapi.responses.JSONResponse:
    """Custom validation for all exceptions"""
    exception_logger.error(f"{validation_for_all_exceptions.__name__} - {exec.args[0]}")
    return fastapi.responses.JSONResponse(
        status_code=400, content={"message": exec.args[0]}
    )


def validation_http_exceptions(
    request: fastapi.Request, exec: HTTPException
) -> fastapi.responses.JSONResponse:
    """Validation handler for http exceptions"""
    exception_logger.error(f"{validation_http_exceptions.__name__} - {exec.detail}")
    return fastapi.responses.JSONResponse(
        status_code=exec.status_code, content={"message": exec.detail}
    )


def validatation_auth_handler(
    request: fastapi.Request, exec: AuthException
) -> fastapi.responses.JSONResponse:
    """Validation handler for auth"""
    exception_logger.error(f"{validatation_auth_handler.__name__} - {exec.msg}")
    return fastapi.responses.JSONResponse(
        status_code=exec.code, content={"message": exec.msg}
    )




def db_error_handler(request: fastapi.Request, exec: Union[IntegrityError, DBAPIError]):
    """Db error handler"""
    error_msg = exec.args[0]
    if "UNIQUE" in error_msg:
        error_msg = (
            f"{error_msg.split(':')[1].split('.')[1].capitalize()} already exist"
        )
    exception_logger.error(f"{db_error_handler.__name__} - {error_msg}")
    return fastapi.responses.JSONResponse(
        status_code=422, content={"message": error_msg}
    )