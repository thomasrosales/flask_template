from settings.database import (
    init_db as initialize_database,
    drop_db as drop_database,
    session
)
from pathlib import Path
import click
import os
from flaskr import create_app, bcrypt
from settings.settings import (
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig
)
from utils.click_styles import (
    Aborted,
    Created,
    Dropped,
    Initialized
)
from flask_bcrypt import generate_password_hash
from flask import jsonify
from workforce.models import User
from workforce.serializers import UserSchema


ROOT = Path(os.path.dirname(os.path.abspath(__file__)))


def callback(ctx, param, value):
    if not value:
        ctx.abort()


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    '-n',
    '--name',
    'name',
    prompt='Superuser Name',
    help='Superuser Name',
    type=str,
    metavar='<text>'
)
def createsuperuser(name):
    """Create a superuser admin"""
    try:
        app = create_app()
        app.app_context().push()
        with app.app_context():
            user = User.query.filter(User.username == name).first()
            if user:
                raise Exception(f'The {user} already exists.')
            else:

                password_crypt = bcrypt.generate_password_hash(
                    'admin', 10).decode('utf-8')

                user = User(name, password_crypt, True, False, False, False)

                session.add(user)
                session.commit()

                serializer = UserSchema().dump(user)

                response = dict()
                response['user'] = serializer
                response['password'] = 'The password is: `admin`. INSECURE ! CHANGE IT PLEASE.'
                click.echo(Created(f'{response}'))
    except Exception as e:
        click.echo(
            Aborted(f'Create superuser produce the followings errors: {e}.'))


@cli.command()
@click.option(
    '--env',
    type=click.Choice(['development', 'production',
                       'testing'], case_sensitive=False),
    default='development',
    help='Start the application.'
)
def runserver(env):
    """Run Application Server"""
    if env in ['development', 'testing']:
        try:
            app = create_app(DevelopmentConfig())
            app.run()
        except Exception as e:
            click.echo(Aborted(f'The following error occur: {e}.'))
    elif env in ['production']:
        try:
            app = create_app(ProductionConfig())
            app.run()
        except Exception as e:
            click.echo(Aborted(f'The following error occur: {e}.'))


@cli.command()
@click.option(
    '--yes',
    is_flag=True,
    callback=callback,
    expose_value=False,
    prompt='Do you want to continue?',
    help='Continue or abort execution',
)
def init_db():
    """Init database"""
    try:
        initialize_database()
        click.echo(Initialized(f'Database initialized.'))
    except Exception as e:
        click.echo(Aborted(f'Init database produce the following error: {e}.'))


@cli.command()
@click.option(
    '--yes',
    is_flag=True,
    callback=callback,
    expose_value=False,
    prompt='Do you want to continue?',
    help='Continue or abort execution',
)
def drop_db():
    """Drop database"""
    try:
        drop_database()
        click.echo(Dropped(f'Database dropped.'))
    except Exception as e:
        click.echo(
            Aborted(f'Dropped database produce the following error: {e}.'))


@ cli.command()
@ click.option(
    '-n',
    '--name',
    'name',
    prompt='Application Name',
    help='The application name',
    type=str,
    metavar='<text>'
)
def startapp(name):
    """Create an application

    NAME is the name of the application, must be unique.
    """

    module = name + '.py'

    main_dir_names = ["static", "templates"]
    main_fil_names = [
        {'__init__.py': ''},
        {'models.py':
            'from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Table\nfrom sqlalchemy.orm import relationship\nfrom settings.database import Base\nfrom utils.models import DateAware\nfrom flask_jwt_extended import (\n    create_access_token,\n    get_jwt_identity,\n    jwt_required\n)\n\n# Create your model here.\n\n'},
        {'responses.py':
            'from sqlalchemy.exc import DatabaseError, IntegrityError\nfrom marshmallow import ValidationError\nfrom utils.errors import (\n    ConflictError,\n    NotFoundError,\n    ClientException\n)\nfrom utils.responses import (\n    GenericCreateResponse,\n    GenericListResponse,\n    GenericRetriveResponse,\n    GenericDeleteResponse\n)\nfrom settings.database import session\nfrom http import HTTPStatus\n\n# Create your responses here.\n\n'},
        {'serializers.py': 'from marshmallow import Schema, fields, validate\nfrom utils.serializers import BaseSchema\nfrom utils.serializer_validations import must_not_be_blank\n\n\n# Create your serializers here.\n\n'},
        {module: 'from flask import Blueprint, request\nfrom flask_jwt_extended import jwt_required\nfrom authentication.permissions import admin_required, manager_required, staff_required\nfrom utils.decorators import ErrorHandler\nimport logging\nfrom flask_cors import CORS\n\n\n' +
            f"{name} = Blueprint('{name}', __name__, template_folder='templates', static_folder='static')\n\nCORS({name})\n\nlogger = logging.getLogger('app')\n\n\n# Create your end-points here.\n\n"}
    ]

    directory = os.path.join(ROOT, name)

    if not os.path.exists(directory):
        for i in range(0, len(main_dir_names)):
            try:
                dirname = directory + '/' + str(main_dir_names[i])
                os.makedirs(dirname)
                if main_dir_names[i] == 'static':
                    dirname = dirname + '/images'
                    os.makedirs(dirname)
            except FileExistsError:
                click.echo(Aborted(f'Directory {directory} already exists.'))
        for item in main_fil_names:
            for k, v in item.items():
                try:
                    dirname = directory + '/' + str(k)
                    with open(dirname, 'w') as out_file:
                        out_file.write(v)
                except FileExistsError:
                    click.echo(
                        Aborted(f'Directory {directory} already exists.'))
        click.echo(Created(f'{name} application created.'))
    else:
        click.echo(Aborted(f'Directory {directory} already exists.'))


if __name__ == '__main__':
    cli()
