from flaskr import jwt
from functools import wraps
from flask_jwt_extended import (
    verify_jwt_in_request,
    get_jwt_claims
)
from utils.errors import NotAuthorizedError
from utils.blacklist_helpers import is_token_revoked


# ROLES VALIDATIONS

# Define our callback function to check if a token has been revoked or not

@jwt.token_in_blacklist_loader
def check_if_token_revoked(decoded_token):
    return is_token_revoked(decoded_token)


@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    return identity


def prohibitted(fn):
    """Here is a custom decorator that verifies the JWT is present in
    the request, as well as insuring that this user has a role of
    `noneone` in the access token.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        raise NotAuthorizedError()
    return wrapper


def admin_required(fn):
    """Here is a custom decorator that verifies the JWT is present in
    the request, as well as insuring that this user has a role of
    `superuser` in the access token.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims.get('roles', None) \
                and isinstance(claims['roles'], dict) \
                and claims['roles'].get('is_superuser', None):
            return fn(*args, **kwargs)
        raise NotAuthorizedError()
    return wrapper


def manager_required(fn):
    """Here is a custom decorator that verifies the JWT is present in
    the request, as well as insuring that this user has a role of
    `manager` or `superuser` in the access token.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims.get('roles', None) \
                and isinstance(claims['roles'], dict) \
                and (claims['roles'].get('is_manager', None)
                     or claims['roles'].get('is_superuser', None)):
            return fn(*args, **kwargs)
        raise NotAuthorizedError()
    return wrapper


def staff_required(fn):
    """Here is a custom decorator that verifies the JWT is present in
    the request, as well as insuring that this user has a role of
    `seller`, `staff` or `superuser` in the access token.
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims.get('roles', None) \
                and isinstance(claims['roles'], dict) \
                and (claims['roles'].get('is_seller', None)
                     or claims['roles'].get('is_superuser', None)
                     or claims['roles'].get('is_manager', None)):
            return fn(*args, **kwargs)
        raise NotAuthorizedError()
    return wrapper
