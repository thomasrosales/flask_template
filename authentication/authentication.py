from flask import Blueprint, request, jsonify
from utils.decorators import ErrorHandler
from flask_jwt_extended import (
    jwt_required,
    jwt_refresh_token_required
)
from .responses import AuthenticationResponse, TokenResponse
from .permissions import admin_required, prohibitted
import logging
from flaskr import jwt
from flask_cors import CORS

authentication = Blueprint('authentication', __name__,
                           template_folder='templates')

CORS(authentication)

logger = logging.getLogger('app')


# Create your end-points here.


@authentication.route('/auth/token/valid', methods=['GET'])
@jwt_required
@ErrorHandler(logger, authentication)
def is_valid_token():
    result, status_code = AuthenticationResponse(request).is_valid()
    return result, status_code


@authentication.route('/login', methods=['POST'])
@ErrorHandler(logger, authentication)
def login():
    result, status_code = AuthenticationResponse(request).login()
    return result, status_code


@authentication.route('/refresh', methods=['POST'])
# @jwt_refresh_token_required
@ErrorHandler(logger, authentication)
@prohibitted
def refresh():
    result, status_code = AuthenticationResponse(request).refresh()
    return result, status_code


@authentication.route('/logout', methods=['DELETE'])
@jwt_required
@ErrorHandler(logger, authentication)
def logout():
    result, status_code = AuthenticationResponse(request).logout()
    return result, status_code


# Provide a way for a user to look at their tokens
@authentication.route('/auth/token/list', methods=['GET'])
@jwt_required
@ErrorHandler(logger, authentication)
@admin_required
def get_tokens():
    result, status_code = TokenResponse().lists()
    return result, status_code


# Provide a way for a user to revoke/unrevoke their tokens
@authentication.route('/logout', methods=['POST'])
@jwt_required
@ErrorHandler(logger, authentication)
@admin_required
def delete_token():
    result, status_code = AuthenticationResponse(request).logout()
    return result, status_code


@authentication.route('/auth/token/<token_id>', methods=['PUT'])
@jwt_required
@ErrorHandler(logger, authentication)
@prohibitted
def modify_token(token_id):
    result, status_code = AuthenticationResponse(request).revoke(token_id)
    return result, status_code
