from flask import Blueprint, request
from utils.decorators import ErrorHandler
from workforce.responses import (
    UserResponse,
    UserImageResponse,
    SellerResponse,
    SellerDeleteResponse
)
from flask_jwt_extended import (
    get_jwt_claims,
    jwt_required
)
from authentication.permissions import admin_required, manager_required
from flask_cors import CORS
import logging


workforce = Blueprint('workforce',
                      __name__,
                      template_folder='templates',
                      static_folder='static'
                      )

CORS(workforce)

logger = logging.getLogger('app')


# Create your end-points here.


# Create a User


@workforce.route('/user', methods=['POST'])
@jwt_required
@ErrorHandler(logger, workforce)
@admin_required
def add_user():
    response, status_code = UserResponse(request).create()
    return response, status_code


# Get User By Id


@workforce.route('/user/<int:user_id>', methods=['GET'])
@jwt_required
@ErrorHandler(logger, workforce)
@admin_required
def get_user(user_id):
    response, status_code = UserResponse(request).retrive(user_id)
    return response, status_code


# Create a Seller


@workforce.route('/seller', methods=['POST'])
@jwt_required
@ErrorHandler(logger, workforce)
@manager_required
def add_seller():
    response, status_code = SellerResponse(request).create()
    return response, status_code


# Get Seller By Id


@workforce.route('/seller/<int:seller_id>', methods=['GET'])
@jwt_required
@ErrorHandler(logger, workforce)
@admin_required
def get_seller(seller_id):
    response, status_code = SellerResponse(request).retrive(seller_id)
    return response, status_code


# Delete Seller By ID


@workforce.route('/seller/<int:seller_id>', methods=['DELETE'])
@jwt_required
@ErrorHandler(logger, workforce)
@manager_required
def delete_seller(seller_id):
    response, status_code = SellerDeleteResponse().delete(seller_id)
    return response, status_code


# Upload a Image a Product By Id


@workforce.route('/user/<int:user_id>/image', methods=['POST'])
@jwt_required
@ErrorHandler(logger, workforce)
@manager_required
def upload_image(user_id):
    response, status_code = UserImageResponse(
        request).create(workforce.name, user_id)
    return response, status_code
