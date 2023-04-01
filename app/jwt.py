import base64
import hmac
import json
from datetime import datetime, timedelta

from app import config


CLIENT_SECRET = config.APP_SECRET
ALGORITHM = 'SHA256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 90


def _encode(payload: dict) -> str:
    header = {
        'alg': ALGORITHM,
        'typ': 'JWT'
    }

    header_encoded = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b'=').decode()
    payload_encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b'=').decode()

    message = f'{header_encoded}.{payload_encoded}'.encode()
    signature = hmac.new(CLIENT_SECRET.encode(), message, digestmod=ALGORITHM).digest()
    signature_encoded = base64.urlsafe_b64encode(signature).rstrip(b'=').decode()

    jwt_token = f'{header_encoded}.{payload_encoded}.{signature_encoded}'

    return jwt_token


def create_access_token(subject: str) -> tuple:
    payload = {
        'sub': subject,
        'typ': 'access',
        'exp': (datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).isoformat()
    }

    return _encode(payload), ACCESS_TOKEN_EXPIRE_MINUTES * 60


def create_refresh_token(subject: str) -> str:
    payload = {
        'sub': subject,
        'typ': 'refresh',
        'exp': (datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).isoformat()
    }
    return _encode(payload)


def get_payload(jwt_token: str) -> dict:
    header_encoded, payload_encoded, signature_encoded = jwt_token.split('.')

    payload = json.loads(base64.urlsafe_b64decode(payload_encoded + "==="))

    message = f"{header_encoded}.{payload_encoded}".encode()
    expected_signature = hmac.new(CLIENT_SECRET.encode(), message, digestmod=ALGORITHM).digest()
    actual_signature = base64.urlsafe_b64decode(signature_encoded + "===")

    if expected_signature != actual_signature:
        raise ValueError('Invalid token')

    return payload


def is_token_expired(payload: dict) -> bool:
    return datetime.utcnow() > datetime.fromisoformat(payload['exp'])
