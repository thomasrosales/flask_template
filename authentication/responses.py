from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from marshmallow import ValidationError, Schema, fields
from utils.errors import (
    ConflictError,
    NotFoundError,
    ClientException,
    NotAuthorizedError,
    TokenNotFound
)
from utils.responses import AbstractResponse
from utils.serializers import SuccessResponseSchema
from settings.database import session
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_jwt_identity,
    get_raw_jwt,
    jwt_required
)
from .serializers import AuthenticationSchema, ToKenBlackListSchema
from http import HTTPStatus
from flask import jsonify
from workforce.models import User
from workforce.serializers import UserSchema
from datetime import timedelta
from flask_bcrypt import check_password_hash
from flaskr import bcrypt
from .permissions import add_claims_to_access_token
from utils.blacklist_helpers import (
    is_token_revoked,
    add_token_to_database,
    get_user_tokens,
    revoke_token,
    unrevoke_token,
    prune_database,
    get_token
)
import os

# Create your responses here.


class AuthenticationResponse:
    _EXPIRES = timedelta(minutes=30)
    _EXPIRES_REFRESH = timedelta(hours=12)

    def __init__(self, request):
        self.request = request
        self.data = request.get_json()

    def login(self):
        try:

            if not self.data:
                raise ClientException(user_err_msg="No input data provided")

            auth = AuthenticationSchema().dump(self.data)

            user = User.query.filter_by(username=auth['username']).one()

            check = bcrypt.check_password_hash(
                user.password, auth['password'])

            if not check:
                raise NotAuthorizedError(
                    user_err_msg='Bad username or password')

            identity = dict()
            roles = {
                'is_seller': user.is_seller,
                'is_costumer': user.is_costumer,
                'is_superuser': user.is_superuser,
                'is_manager': user.is_manager
            }
            identity['username'] = user.username
            identity['roles'] = roles

            # Create our JWT

            access_token = create_access_token(
                identity=identity, expires_delta=self._EXPIRES)
            refresh_token = create_refresh_token(
                identity=identity, expires_delta=self._EXPIRES_REFRESH)

            # Store the tokens in our store with a status of not currently revoked.
            add_token_to_database(
                access_token, os.environ.get('JWT_IDENTITY_CLAIM'))

            # TODO: USE OR NOT USE ? METHOD FOR TOKEN EXPIRED ?
            # add_token_to_database(
            #     refresh_token, os.environ.get('JWT_IDENTITY_CLAIM'))

            ret = {
                'access_token': access_token,
                # 'refresh_token': refresh_token
            }
            return jsonify(ret), HTTPStatus.CREATED
        except ValidationError as e:
            raise NotFoundError(user_err_msg=e.messages)
        except NoResultFound as e:
            raise NotAuthorizedError(user_err_msg='Bad username or password')
        except Exception as e:
            raise e

    def refresh(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(
            identity=current_user, expires_delta=self._EXPIRES)
        add_token_to_database(
            access_token, os.environ.get('JWT_IDENTITY_CLAIM'))
        ret = {
            'access_token': access_token
        }
        return jsonify(ret), HTTPStatus.OK

    def logout(self):
        jti = get_raw_jwt()['jti']
        current_user = get_jwt_identity()
        try:
            revoke_token(user=current_user, jti=jti)
            serializer = SuccessResponseSchema().load(
                {'message': 'Token revoked', 'status': HTTPStatus.OK})
            return serializer, HTTPStatus.OK
        except TokenNotFound:
            raise TokenNotFound(
                user_err_msg='The specified token was not found')

    def revoke(self, token_id):
        json_data = self.request.get_json(silent=True)
        if not json_data:
            raise ClientException(user_err_msg='Missing `revoke` in body')
        revoke = json_data.get('revoke', None)
        if revoke is None:
            raise ClientException(user_err_msg='Missing `revoke` in body')
        if not isinstance(revoke, bool):
            raise ClientException(user_err_msg='`revoke` must be a boolean')

        # Revoke or unrevoke the token based on what was passed to this function
        current_user = get_jwt_identity()
        try:
            if revoke:
                revoke_token(current_user, token_id=token_id)
            serializer = SuccessResponseSchema().load(
                {'message': 'Token revoked', 'status': HTTPStatus.OK})
            return serializer, HTTPStatus.OK
            # else:
            # TODO: NOT USED
            #    unrevoke_token(token_id, current_user)
            #    return jsonify({'msg': 'Token unrevoked'}), 200
        except TokenNotFound as e:
            raise TokenNotFound(
                user_err_msg='The specified token was not found')

    def is_valid(self):
        token = get_token(get_raw_jwt())
        OkErrorSchema = Schema.from_dict(
            {'message': fields.Boolean(), 'status': fields.Int()})
        if token:
            serializer = OkErrorSchema().load(
                {'message': True, 'status': HTTPStatus.OK})
            return serializer, HTTPStatus.OK
        serializer = OkErrorSchema().load(
            {'message': False, 'status': HTTPStatus.OK})
        return serializer, HTTPStatus.OK


class TokenResponse:

    def lists(self):
        user_identity = get_jwt_identity()
        all_tokens = get_user_tokens(user_identity)
        ret = [ToKenBlackListSchema().dump(token) for token in all_tokens]
        return jsonify(ret), HTTPStatus.OK
