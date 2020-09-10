from marshmallow import Schema, fields, validate
from utils.serializers import BaseSchema
from .models import User, Seller, Costumer
# from sales.serializers import SaleSchema


# Create your serializers here.


class ManagerSchema(BaseSchema):
    user_id = fields.Int(required=True)
    user = fields.Nested(lambda: UserSchema(exclude=["created", "modified"]))


class SellerSchema(BaseSchema):
    user_id = fields.Int(required=True)
    user = fields.Nested(lambda: UserSchema(exclude=["created", "modified"]))
    # sales = fields.List(fields.Nested(SaleSchema(exclude=("seller_id",))))


class CostumerSchema(BaseSchema):
    user_id = fields.Int(required=True)
    user = fields.Nested(lambda: UserSchema())


class UserSchema(BaseSchema):
    username = fields.Str(required=True, allow_none=False,
                          validate=validate.Length(min=4))
    password = fields.Str(required=True, load_only=True,
                          validate=validate.Length(min=8))
    is_superuser = fields.Boolean(default=False)
    is_manager = fields.Boolean(default=False)
    is_costumer = fields.Boolean(default=True)
    is_seller = fields.Boolean(default=False)
    is_active = fields.Boolean(default=True)
    thumbnail = fields.Str(dump_only=True)
