from flask import Blueprint, request
from utils.decorators import ErrorHandler
from utils.errors import ConflictError
import datetime


DATE_FORMAT = '%Y-%m-%d'


NOW = datetime.datetime.now()
HOURS_ADDED = datetime.timedelta(
    hours=NOW.hour, minutes=NOW.minute, seconds=NOW.second)


def from_date(date: str):
    return datetime.datetime.strptime(date, DATE_FORMAT).isoformat(sep=' ')


def to_date(date: str):
    return (datetime.datetime.strptime(date, DATE_FORMAT) + HOURS_ADDED).isoformat()


def to_bool(deleted: str):
    return (deleted in ['True', 'true', 't', '1', 'yes', 'y', ''])


def to_list(q: str):
    print(q.split(' '), type(q))
    filters_list = q.split(' ')
    return q


def page_boundires(page_size: int):
    if int(page_size) > 100:
        raise ConflictError(user_err_msg='Superior Boundary Exceeded.')
    elif int(page_size) < 0:
        raise ConflictError(user_err_msg='Inferior Boundary Exceeded.')
    return page_size


def get_url_params(request, *args, **kwargs):
    filters = dict()

    page_size = request.args.get(
        'pageSize',
        default=10,
        type=int,
    )

    page_boundires(page_size)

    page = request.args.get(
        'page',
        default=1,
        type=int
    )
    date_from = request.args.get(
        'from',
        default=datetime.datetime.strptime(
            '1990-01-01', DATE_FORMAT).isoformat(),
        type=from_date
    )
    date_to = request.args.get(
        'to',
        default=datetime.datetime.now(),
        type=to_date
    )

    deleted = request.args.get(
        'deleted',
        default=False,
        type=to_bool
    )

    for k in kwargs.keys():
        filters[str(k)] = kwargs[k]

    filters['page_size'] = page_size
    filters['page'] = page
    filters['deleted'] = deleted
    filters['to'] = date_to
    filters['from'] = date_from

    return filters

    # filters = request.args.get('filters', None)

    # q = request.args.get('q', type=to_list)

    # page = request.args.get('page', default = 1, type = int)
    # filter = request.args.get('filter', default = '*', type = str)
