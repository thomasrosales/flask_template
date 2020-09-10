import functools
import logging
import sys
import traceback
import json
from .errors import (
    APIException,
    ApplicationException,
    DBException,
    NotFoundError,
    NotAuthorizedError,
    ClientException,
    ConflictError
)
from flask_jwt_extended.exceptions import (
    FreshTokenRequired,
    InvalidHeaderError,
    NoAuthorizationError,
    UserLoadError,
    JWTExtendedException  # GLOBAL EXCEPTION
)
from werkzeug.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError


class ErrorHandler:

    def __init__(self, logger, blueprint):
        self._logger = logger
        self._blueprint = blueprint.name

    def _prepare_traceback_to_log(self, loggin_type):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        trace = repr(traceback.format_exception(
            exc_type, exc_value, exc_traceback))
        self._logger.log(loggin_type, trace, extra=dict(bp=self._blueprint))

    def __call__(self, func, *args, **kwargs):
        @functools.wraps(func)
        def wrapper_decorator(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                self._logger.log(logging.INFO, result,
                                 extra=dict(bp=self._blueprint))
                return result
            except (ConflictError, NotAuthorizedError) as e:
                self._prepare_traceback_to_log(logging.INFO)
                return e.to_json(), e.http_status
            except (ClientException,) as e:
                self._prepare_traceback_to_log(logging.ERROR)
                return e.to_json(), e.http_status
            except (HTTPException,) as e:
                self._prepare_traceback_to_log(logging.ERROR)
                return ClientException(user_err_msg=str(e)).to_json(), e.code or e.http_status
            except (ApplicationException, JWTExtendedException) as e:
                self._prepare_traceback_to_log(logging.ERROR)
                return e.to_json(), e.http_status
            except Exception as e:
                self._prepare_traceback_to_log(logging.CRITICAL)
                return APIException().to_json(), 500
        return wrapper_decorator


def error_raise_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except IntegrityError as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            raise DBException(user_err_msg=str(exc_value).split('\n')[0])
        except Exception as e:
            raise e
    return wrapper

#parse('duplicate key value violates unique constraint "{constraint}"\nDETAIL:  Key ({field})=({input}) already exists.\n', str(e.orig))["field"]
