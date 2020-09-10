from marshmallow import Schema, fields, ValidationError
import os

# Custom validators


def must_not_be_blank(data):
    if not data:
        raise ValidationError("Data not provided.")


def must_be_in_allowed_extension(extension: str):
    return extension in os.environ.get('ALLOWED_EXTENSIONS')


def validate_quantity(n):
    if n < 0:
        raise ValidationError("Quantity must be greater than 0.")
    if n > 30:
        raise ValidationError("Quantity must not be greater than 30.")


def validate_thumbnail(thumbnail):
    pass
