from flask import request

from app import app
from app.jwt import get_payload
from app.devices import devices


@app.route('/v1.0', methods=['HEAD'])
def get_app_status():
    return '', 200


@app.route('/v1.0/user/unlink', methods=['POST'])
def get_unlink_status():
    request_id = request.headers['X-Request-Id']

    return {'request_id': request_id}, 200


@app.route('/v1.0/user/devices', methods=['GET'])
def get_user_devices():
    access_token = request.headers['Authorization'].split()[-1]
    request_id = request.headers['X-Request-Id']

    try:
        payload = get_payload(access_token)
    except ValueError as exc:
        return exc, 403

    devices_info = [device.yandex_info for device in devices.values()]

    return {'request_id': request_id, 'payload': {'user_id': payload['sub'], 'devices': devices_info}}, 200


@app.route('/v1.0/user/devices/query', methods=['POST'])
def get_user_device_status():
    access_token = request.headers['Authorization'].split()[-1]
    request_id = request.headers['X-Request-Id']

    try:
        get_payload(access_token)
    except ValueError as exc:
        return exc, 403

    devices_status = []
    for device in request.json['devices']:
        devices_status.append(devices[device['id']].yandex_status)

    return {'request_id': request_id, 'payload': {'devices': devices_status}}, 200


@app.route('/v1.0/user/devices/action', methods=['POST'])
def send_action_to_user_device():
    access_token = request.headers['Authorization'].split()[-1]
    request_id = request.headers['X-Request-Id']

    try:
        get_payload(access_token)
    except ValueError as exc:
        return exc, 403

    devices_action = request.json['payload']['devices']
    for i, device in enumerate(devices_action):
        capabilities = devices_action[i]['capabilities']
        devices_action[i]['capabilities'] = devices[device['id']].yandex_action(capabilities)

    return {'request_id': request_id, 'payload': {'devices': devices_action}}, 200
