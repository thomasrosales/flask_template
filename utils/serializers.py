from marshmallow import Schema, fields, validates, ValidationError
from settings.database import session
from utils.serializer_validations import must_not_be_blank, must_be_in_allowed_extension
import os


class ResponseSchema(Schema):
    status = fields.Int(dump_only=True)
    offset = fields.Int(dump_only=True)
    totalResults = fields.Int(dump_only=True)
    results = fields.Dict(dump_only=True)


class BaseSchema(Schema):
    id = fields.Int(dump_only=True)
    created = fields.DateTime(dump_only=True)
    modified = fields.DateTime(dump_only=True)
    deleted = fields.Boolean(dump_only=True)


class SuccessResponseSchema(Schema):
    message = fields.Str()
    status = fields.Int()


class ImageSchema(Schema):
    thumbnail = fields.Str(
        required=True,
        validate=must_not_be_blank,
        allow_none=False
    )
    extension = fields.Str(
        required=True,
        validate=must_not_be_blank,
        allow_none=False
    )

    @validates("extension")
    def validate_extension(self, value):
        if not must_be_in_allowed_extension(value):
            raise ValidationError(
                f"Extension must be one of the followings types: { os.environ.get('ALLOWED_EXTENSIONS')} ")
