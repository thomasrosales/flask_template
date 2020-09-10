import json
from flask import jsonify
from http import HTTPStatus
from datetime import datetime


class APIException(Exception):
    """Base API Exception"""

    http_status = HTTPStatus.INTERNAL_SERVER_ERROR  # Default Error
    internal_err_msg = 'API exception occurred'  # Default Message
    user_err_msg = 'Sorry ! An unexpected error occurred on our end.'

    def __init__(self, *args, user_err_msg=None):
        if args:
            self.internal_err_msg = args[0]
            super().__init__(*args)
        else:
            super().__init__(self.internal_err_msg)

        if user_err_msg is not None:
            self.user_err_msg = user_err_msg

    def to_json(self):
        err_object = {'status': self.http_status, 'message': self.user_err_msg}
        return jsonify(err_object)

    def log_exception(self):
        exception = {
            "type": type(self).__name__,
            "http_status": self.http_status,
            "message": self.args[0] if self.args else self.internal_err_msg,
            "args": self.args[1:]
        }
        return json.dumps(exception)
        # print(f'EXCEPTION: {datetime.utcnow().isoformat()}: {exception}')


class ApplicationException(APIException):
    """General databases exception"""
    http_status = HTTPStatus.INTERNAL_SERVER_ERROR
    internal_err_msg = 'Generic server side exception.'
    user_err_msg = 'Sorry. An unexpected error occurred on our end.'


class DBException(ApplicationException):
    """General database exception"""
    http_status = HTTPStatus.INTERNAL_SERVER_ERROR
    internal_err_msg = 'Database side exception.'
    user_err_msg = 'Sorry. An unexpected error occurred on our end.'


class TokenNotFound(DBException):
    """ Indicates that a token could not be found in the database
    """
    http_status = HTTPStatus.INTERNAL_SERVER_ERROR
    internal_err_msg = 'Indicates that a token could not be found in the database'
    user_err_msg = 'Indicates that a token could not be found in the database'


class ClientException(APIException):
    """Indicates exception that was casued by user, not an internal error"""
    http_status = HTTPStatus.BAD_REQUEST
    internal_err_msg = 'Client sumbitted bad requests'
    user_err_msg = 'A bad request was received.'


class NotFoundError(ClientException):
    """Indicates resource was not found"""
    http_status = HTTPStatus.NOT_FOUND
    internal_err_msg = 'Resource not found'
    user_err_msg = 'Requested resource was not found.'


class ForbiddenError(ClientException):
    """The server understood the request but refuses to authorize it."""
    http_status = HTTPStatus.FORBIDDEN
    internal_err_msg = 'The server understood the request but refuses to authorize it.'
    user_err_msg = 'Forbidden.'


class ConflictError(ClientException):
    """The request has been accepted for processing, but the processing has not been completed."""
    http_status = HTTPStatus.CONFLICT
    internal_err_msg = 'The request has been accepted for processing, but the processing has not been completed.'
    user_err_msg = 'Accepted.'


class NotAuthorizedError(ClientException):
    """User is not authorized to perform requested action on resource"""
    http_status = HTTPStatus.UNAUTHORIZED
    internal_err_msg = 'Client not authorized to perform this operation'
    user_err_msg = 'You are not authorized to perform this operation.'
