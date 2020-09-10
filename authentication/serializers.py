from marshmallow import Schema, fields, validate
from settings.database import session
from utils.serializers import BaseSchema


# Create your serializers here.

class AuthenticationSchema(Schema):
    username = fields.Str(
        required=True,
        allow_none=False,
        validate=validate.Length(min=4)
    )
    password = fields.Str(
        required=True,
        allow_none=False,
        validate=validate.Length(min=4)
    )


class ToKenBlackListSchema(BaseSchema):
    jti = fields.Str(required=True, allow_none=False)
    token_type = fields.Str(required=True, allow_none=False,
                            validate=validate.Length(max=10))
    user_identity = fields.Str(
        required=True, allow_none=False, validate=validate.Length(max=50))
    revoked = fields.Boolean(default=False, allow_none=False)
    expires = fields.DateTime(dump_only=True)
