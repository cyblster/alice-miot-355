from flask import request

from app import app
from app.jwt import get_payload
from app.devices import fan, vacuum, tv


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
    except ValueError:
        return 'Invalid token', 403

    devices = [device.yandex_info for device in (fan, vacuum, tv)]

    return {'request_id': request_id, 'payload': {'user_id': payload['sub'], 'devices': devices}}, 200


@app.route('/v1.0/user/devices/query', methods=['POST'])
def get_user_device_status():
    access_token = request.headers['Authorization'].split()[-1]
    request_id = request.headers['X-Request-Id']

    try:
        get_payload(access_token)
    except ValueError:
        return 'Invalid token', 403

    devices = []
    for device in request.json['devices']:
        devices.append({
            'ijai.vacuum.v10': vacuum,
            'dmaker.fan.p18': fan,
            'xiaomi.tv.p1': tv,
        }[device['id']].yandex_status)

    return {'request_id': request_id, 'payload': {'devices': devices}}, 200


@app.route('/v1.0/user/devices/action', methods=['POST'])
def send_action_to_user_device():
    access_token = request.headers['Authorization'].split()[-1]
    request_id = request.headers['X-Request-Id']

    try:
        get_payload(access_token)
    except ValueError:
        return 'Invalid token', 403

    actions_status = request.json
    for i, device in enumerate(actions_status['payload']['devices']):
        actions_status['payload']['devices'][i]['capabilities'] = {
            'ijai.vacuum.v10': vacuum,
            'dmaker.fan.p18': fan,
            'xiaomi.tv.p1': tv,
        }[device['id']].yandex_action(actions_status['payload']['devices'][i]['capabilities'])

    return {'request_id': request_id, 'payload': actions_status['payload']}, 200
