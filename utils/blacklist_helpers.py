from datetime import datetime

from sqlalchemy.orm.exc import NoResultFound
from flask_jwt_extended import decode_token

from .errors import TokenNotFound
from authentication.models import TokenBlacklist
from settings.database import session


def _epoch_utc_to_datetime(epoch_utc):
    """
    Helper function for converting epoch timestamps (as stored in JWTs) into
    python datetime objects (which are easier to use with sqlalchemy).
    """
    return datetime.fromtimestamp(epoch_utc)


def add_token_to_database(encoded_token, identity_claim):
    """
    Adds a new token to the database. It is not revoked when it is added.
    :param identity_claim:
    """
    decoded_token = decode_token(encoded_token)
    jti = decoded_token['jti']
    token_type = decoded_token['type']
    user_identity = decoded_token[identity_claim]
    expires = _epoch_utc_to_datetime(decoded_token['exp'])
    revoked = False

    db_token = TokenBlacklist(
        jti=jti,
        token_type=token_type,
        user_identity=user_identity['username'],
        expires=expires,
        revoked=revoked,
    )
    session.add(db_token)
    session.commit()


def get_token(decoded_token):
    try:
        jti = decoded_token['jti']
        token = TokenBlacklist.query.filter_by(jti=jti).one()
        return token
    except NoResultFound:
        return None


def is_token_revoked(decoded_token):
    """
    Checks if the given token is revoked or not. Because we are adding all the
    tokens that we create into this database, if the token is not present
    in the database we are going to consider it revoked, as we don't know where
    it was created.
    """
    token = get_token(decoded_token)
    if token:
        return token.revoked
    return false


def get_user_tokens(user_identity):
    """
    Returns all of the tokens, revoked and unrevoked, that are stored for the
    given user
    """
    return TokenBlacklist.query.filter_by(user_identity=user_identity['username']).all()


def revoke_token(user, jti: str = None, token_id: int = None):
    """
    Revokes the given token. Raises a TokenNotFound error if the token does
    not exist in the database
    """
    try:
        if token_id:
            token = TokenBlacklist.query.filter_by(
                id=token_id,
                user_identity=user['username']
            ).one()
        elif jti:
            token = TokenBlacklist.query.filter_by(
                jti=jti,
                user_identity=user['username']
            ).one()
        token.revoked = True
        session.commit()
    except NoResultFound:
        raise TokenNotFound(
            user_err_msg=f"Could not find the token {token_id}")


def unrevoke_token(token_id, user):
    """
    Unrevokes the given token. Raises a TokenNotFound error if the token does
    not exist in the database
    """
    try:
        token = TokenBlacklist.query.filter_by(
            id=token_id, user_identity=user['username']).one()
        token.revoked = False
        session.commit()
    except NoResultFound:
        raise TokenNotFound("Could not find the token {}".format(token_id))


# TODO MAKE AN CRON TASK
def prune_database():
    """
    Delete tokens that have expired from the database.
    How (and if) you call this is entirely up you. You could expose it to an
    endpoint that only administrators could call, you could run it as a cron,
    set it up with flask cli, etc.
    """
    now = datetime.now()
    expired = TokenBlacklist.query.filter(TokenBlacklist.expires < now).all()
    for token in expired:
        session.delete(token)
    session.commit()
