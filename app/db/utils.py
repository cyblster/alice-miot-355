from uuid import UUID
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from . import db, models


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def object_as_dict(obj):
    return dict(filter(lambda item: not item[0].startswith('_'), obj.__dict__.items()))


def get_user_by_username(username: str) -> dict:
    user = models.User.query.filter_by(username=username).first()

    return object_as_dict(user) if user else {}


def get_user_by_code(code: str) -> dict:
    user = models.User.query.filter_by(code=code).first()

    return object_as_dict(user) if user else {}


def add_user(username: str, password: str) -> bool:
    try:
        db.session.add(models.User(username=username, hashed_password=get_password_hash(password)))
        db.session.commit()
        return True
    except IntegrityError:
        db.session.rollback()
        return False


def update_user_code(username: str, code: UUID) -> None:
    user = models.User.query.filter_by(username=username).first()
    user.code = code

    db.session.commit()


def get_user_refresh_token(username: str) -> str:
    user = models.User.query.filter_by(username=username).first()

    return user.refresh_token


def update_user_refresh_token(username: str, refresh_token: str) -> None:
    user = models.User.query.filter_by(username=username).first()
    user.refresh_token = refresh_token

    db.session.commit()
