from http import HTTPStatus
from marshmallow import ValidationError
from utils.errors import ConflictError, NotFoundError, DBException, ClientException
from utils.decorators import error_raise_handler
from utils.serializers import ResponseSchema
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from marshmallow import Schema, fields
from typing import List, Dict, Tuple, Type
import marshmallow


class AbstractValidation:

    @error_raise_handler
    def pre_validation(self, *args, **kwargs) -> None:
        pass

    @error_raise_handler
    def post_validation(self, *args, **kwargs) -> None:
        pass

    @error_raise_handler
    def validation(self, *args, **kwargs) -> None:
        pass


class AbstractResponse:
    model = None
    schema = None

    def __init__(self, request):
        self.data = request.get_json()

    def set_response(self, status: int, total_results: int, serializer: Dict) -> Tuple[Dict, int]:
        response = dict()
        response['status'] = status
        response['totalResults'] = total_results
        response['results'] = serializer

        response_serializer = ResponseSchema().dump(response)

        return response_serializer, status


class GenericRetriveResponse:
    model = None
    schema = None

    @error_raise_handler
    def get_object(self, id: int) -> Type[model]:
        try:
            instance = self.model.query.filter_by(id=id).one()
            return instance
        except NoResultFound:
            raise ConflictError(
                user_err_msg=f'{self.model.__name__}({id}) does not exists.')

    @error_raise_handler
    def retrive(self, id: int) -> Tuple[Dict, int]:
        resultset = self.get_object(id)
        serializer = self.schema().dump(resultset)
        return serializer, HTTPStatus.OK


class GenericListResponse(AbstractResponse):
    model = None
    schema = None
    queryset = None
    session = None

    @error_raise_handler
    def get_queryset(self, *args, **kwargs) -> Tuple[List[Type[model]], int]:
        if self.queryset:
            response = self.queryset
            return response, len(response)
        if self.model:
            response = self.model.query.filter_by(**kwargs).all()
            return response, len(response)
        raise DBException(
            user_err_msg='QuerySet empty and model class not provided.')

    @error_raise_handler
    def lists(self, *args, **kwargs) -> Tuple[Dict, int]:
        queryset, total_results = self.get_queryset(**kwargs)
        return self._list_serialize(queryset, total_results)

    @error_raise_handler
    def _list_serialize(self, queryset: List[Type[model]], total_results: int) -> Tuple[Dict, int]:
        serializer = self.schema().dump(queryset, many=True)
        return self.set_response(HTTPStatus.OK, total_results, serializer)


class GenericCreateResponse(AbstractValidation):
    model = None
    schema = None
    session = None

    def __init__(self, request):
        self.data = request.get_json()

    @error_raise_handler
    def pre_create(self, *args, **kwargs) -> Dict:
        try:
            if not self.data:
                raise ClientException(user_err_msg="No input data provided")

            serializer = self.schema().load(self.data)

            self.pre_validation(*args, **kwargs)

            return serializer
        except ValidationError as e:
            raise NotFoundError(user_err_msg=e.messages)
        except Exception as e:
            raise e

    @error_raise_handler
    def create(self, *args, **kwargs) -> Tuple[Dict, int]:

        serializer = self.pre_create(*args, **kwargs)

        instance = self.create_instance()

        self.validation(*args, **kwargs)

        deserializer = self.post_create(instance)

        return deserializer, HTTPStatus.CREATED

    @error_raise_handler
    def create_instance(self) -> Type[model]:
        return self.model(**self.data)

    @error_raise_handler
    def post_create(self, instance: Type[model]) -> Dict:
        self.session.add(instance)
        self.session.commit()

        self.post_validation()

        return self.schema().dump(instance)


class GenericDeleteResponse(AbstractValidation):
    model = None
    schema = None
    session = None

    @error_raise_handler
    def get_object(self, id: int) -> Type[model]:
        try:
            instance = self.model.query.filter_by(id=id).one()
            return instance
        except NoResultFound:
            raise ConflictError(
                user_err_msg=f'{self.model.__name__}({id}) does not exists.')

    @error_raise_handler
    def delete(self, id: int) -> Tuple[Dict, int]:
        self.id = id
        instance = self.get_object(id)
        instance.deleted = True
        self.session.commit()

        deserializer = self.schema().dump(instance)

        return deserializer, HTTPStatus.OK


class GenericUpdateResponse(AbstractValidation):
    model = None
    schema = None
    session = None

    def __init__(self, request):
        self.data = request.get_json()

    @error_raise_handler
    def update(self, *args, **kwargs) -> None:
        pass

    @error_raise_handler
    def get_object(self, id: int) -> Type[model]:
        try:
            instance = self.model.query.filter_by(id=id).one()
            return instance
        except NoResultFound:
            raise ConflictError(
                user_err_msg=f'{self.model.__name__}({id}) does not exists.')

    @error_raise_handler
    def pre_update(self, *args, **kwargs) -> None:
        try:
            if not self.data:
                raise ClientException(user_err_msg="No input data provided")

            model_attributes = self.model.__table__.columns._data.keys()

            for prop in self.data.keys():
                if not prop in model_attributes:
                    raise ClientException(
                        user_err_msg=f'The key({prop}) does not exists.')
                if self.data[prop] == '' or self.data[prop] is None:
                    raise ClientException(
                        user_err_msg=f'The key({prop}) is empty or null.')

            self.pre_validation(*args, **kwargs)
        except ValidationError as e:
            raise NotFoundError(user_err_msg=e.messages)
        except Exception as e:
            raise e

    @error_raise_handler
    def partial_update(self, id, *args, **kwargs) -> Tuple[Dict, int]:

        self.pre_update(*args, **kwargs)

        instance = self.get_object(id)

        for prop in self.data.keys():
            try:
                setattr(instance, prop, self.data[prop])
            except Exception as e:
                continue

        self.update(instance, *args, **kwargs)
        self.validation(*args, **kwargs)

        deserializer = self.post_update(instance)

        return deserializer, HTTPStatus.OK

    @error_raise_handler
    def post_update(self, instance: Type[model]) -> Dict:
        self.session.commit()
        deserializer = self.schema().dump(instance)

        self.post_validation()

        return self.schema().dump(instance)
