from sqlalchemy.exc import DatabaseError, IntegrityError
from marshmallow import ValidationError
from .models import (
    Costumer,
    User,
    Seller
)
from .serializers import(
    CostumerSchema,
    UserSchema,
    SellerSchema
)
from utils.errors import (
    ConflictError,
    NotFoundError,
    ClientException
)
from utils.responses import (
    AbstractResponse,
    GenericCreateResponse,
    GenericListResponse,
    GenericRetriveResponse,
    GenericDeleteResponse
)
from utils.serializers import ImageSchema
from utils.images_helpers import save_to_image
from settings.database import session
from flask_bcrypt import generate_password_hash
from flaskr import bcrypt
from http import HTTPStatus


# Create your responses here.


class UserResponse(GenericCreateResponse, GenericRetriveResponse, GenericListResponse):
    model = User
    schema = UserSchema
    session = session

    def pre_validation(self):
        user = User.query.filter_by(
            username=self.data['username']).first()

        if user:
            raise ConflictError(
                user_err_msg=f'{user} already exists.')

    def create_instance(self):
        user = User(**self.data)

        password_crypt = bcrypt.generate_password_hash(
            user.password, 10).decode('utf-8')

        user.password = password_crypt

        return user


class UserImageResponse(GenericRetriveResponse, GenericCreateResponse):
    model = User
    schema = ImageSchema

    def create(self, blueprint_name, id):

        serializer = self.pre_create()

        user = self.get_object(id)

        image_name = save_to_image(
            blueprint_name,
            image_file=serializer['thumbnail'],
            extension=serializer['extension']
        )

        user.thumbnail = image_name

        session.commit()

        deserializer = UserSchema().dump(user)

        return deserializer, HTTPStatus.OK


class SellerResponse(GenericCreateResponse, GenericRetriveResponse, GenericListResponse):
    model = Seller
    schema = SellerSchema
    session = session

    def pre_validation(self):
        user = User.query.filter_by(
            id=self.data['user_id'], deleted=False).first()

        if not user:
            raise ConflictError(
                user_err_msg=f'User({user}) does not exists.')

        seller_by_user = Seller.query.join(Seller.user).filter(
            User.id == self.data['user_id']).first()

        if seller_by_user:
            raise ConflictError(
                user_err_msg=f'Already exists a seller to the {user}')


class SellerDeleteResponse(GenericDeleteResponse):
    model = Seller
    schema = SellerSchema
    session = session
