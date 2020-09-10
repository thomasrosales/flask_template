import uuid
import os
import base64
import binascii
from os import path
from utils.errors import ConflictError

BASE_DIR = path.abspath(path.join(path.dirname(__file__), '..'))
DEFAULT_IMAGE = 'no-picture.png'


def allowed_file(extension):
    return extension in os.environ.get('ALLOWED_EXTENSIONS')


def save_to_image(blueprint, image_file=None, extension='.png'):

    if allowed_file(extension) and is_base64(image_file):
        image_directory = os.path.join(
            BASE_DIR,
            blueprint,
            'static',
            'images'
        )
        image_name = f'{str(uuid.uuid4())}.{extension}'
        image_path = os.path.join(image_directory, image_name)
        image = open(image_path, "wb")
        image.write(base64.b64decode(image_file))
        image.close()
    else:
        # TODO: MUST BE A BETTER ERROR
        raise ConflictError('EXTENSION NO !')

    return f'/{blueprint}/static/images/{image_name}'


def is_base64(image_name):
    try:
        image_data = base64.b64decode(image_name, validate=True)
        return True
    except binascii.Error:
        raise ConflictError(
            user_err_msg=f'Image must be a binary base64 string.')
