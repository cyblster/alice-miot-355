import requests
import random
import hmac
import base64
import hashlib
import json
import time
import os
from arc4 import ARC4


class MiCloud:
    def __init__(self, username, password, region):
        self._session = requests.session()

        self._username = username
        self._password = password
        self._region = region
        self._user_agent = self._generate_agent()
        self._device_id = self._generate_device_id()
        self._sign = None
        self._ssecurity = None
        self._userId = None
        self._cUserId = None
        self._passToken = None
        self._location = None
        self._code = None
        self._serviceToken = None

        self.two_factor_auth_url = None

        self._login()

    def _login_step_1(self):
        url = 'https://account.xiaomi.com/pass/serviceLogin?sid=xiaomiio&_json=true'
        headers = {
            'User-Agent': self._user_agent,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        cookies = {
            'userId': self._username
        }
        try:
            response = self._session.get(url, headers=headers, cookies=cookies, timeout=10)
        except:
            response = None
        successful = response is not None and response.status_code == 200 and '_sign' in self._to_json(response.text)
        if successful:
            self._sign = self._to_json(response.text)['_sign']

        return successful

    def _login_step_2(self):
        url = 'https://account.xiaomi.com/pass/serviceLoginAuth2'
        headers = {
            'User-Agent': self._user_agent,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        fields = {
            'sid': 'xiaomiio',
            'hash': hashlib.md5(str.encode(self._password)).hexdigest().upper(),
            'callback': 'https://sts.api.io.mi.com/sts',
            'qs': '%3Fsid%3Dxiaomiio%26_json%3Dtrue',
            'user': self._username,
            '_sign': self._sign,
            '_json': 'true'
        }
        try:
            response = self._session.post(url, headers=headers, params=fields, timeout=10)
        except:
            response = None
        successful = response is not None and response.status_code == 200
        if successful:
            json_resp = self._to_json(response.text)
            successful = 'ssecurity' in json_resp and len(str(json_resp['ssecurity'])) > 4
            if successful:
                self._ssecurity = json_resp['ssecurity']
                self._userId = json_resp['userId']
                self._cUserId = json_resp['cUserId']
                self._passToken = json_resp['passToken']
                self._location = json_resp['location']
                self._code = json_resp['code']
                self.two_factor_auth_url = None
            else:
                if 'notificationUrl' in json_resp:
                    self.two_factor_auth_url = json_resp['notificationUrl']
                    successful = None

        return successful

    def _login_step_3(self):
        headers = {
            'User-Agent': self._user_agent,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        try:
            response = self._session.get(self._location, headers=headers, timeout=3)
        except:
            response = None
        successful = response is not None and response.status_code == 200 and 'serviceToken' in response.cookies
        if successful:
            self._serviceToken = response.cookies.get('serviceToken')

        return successful

    def _login(self) -> bool:
        self._session.close()
        self._session = requests.session()
        self._user_agent = self._generate_agent()
        self._device_id = self._generate_device_id()
        self._session.cookies.set('sdkVersion', 'accountsdk-18.8.15', domain='mi.com')
        self._session.cookies.set('sdkVersion', 'accountsdk-18.8.15', domain='xiaomi.com')
        self._session.cookies.set('deviceId', self._device_id, domain='mi.com')
        self._session.cookies.set('deviceId', self._device_id, domain='xiaomi.com')

        return self._login_step_1() and self._login_step_2() and self._login_step_3()

    def _execute_api_call_encrypted(self, url, params):
        headers = {
            'Accept-Encoding': 'identity',
            'User-Agent': self._user_agent,
            'Content-Type': 'application/x-www-form-urlencoded',
            'x-xiaomi-protocal-flag-cli': 'PROTOCAL-HTTP2',
            'MIOT-ENCRYPT-ALGORITHM': 'ENCRYPT-RC4',
        }
        cookies = {
            'userId': str(self._userId),
            'yetAnotherServiceToken': str(self._serviceToken),
            'serviceToken': str(self._serviceToken),
            'locale': 'en_GB',
            'timezone': 'GMT+02:00',
            'is_daylight': '1',
            'dst_offset': '3600000',
            'channel': 'MI_APP_STORE'
        }
        millis = round(time.time() * 1000)
        nonce = self._generate_nonce(millis)
        signed_nonce = self._signed_nonce(nonce)
        fields = self._generate_enc_params(url, 'POST', signed_nonce, nonce, params, self._ssecurity)

        try:
            response = self._session.post(url, headers=headers, cookies=cookies, params=fields, timeout=10)
        except:
            response = None
        if response is not None and response.status_code == 200:
            decoded = self._decrypt_rc4(self._signed_nonce(fields['_nonce']), response.text)
            return json.loads(decoded)

        return None

    def _signed_nonce(self, nonce):
        hash_object = hashlib.sha256(base64.b64decode(self._ssecurity) + base64.b64decode(nonce))

        return base64.b64encode(hash_object.digest()).decode('utf-8')

    def _get_api_url(self):
        return 'https://' + ('' if self._region == 'cn' else (self._region + '.')) + 'api.io.mi.com/app'

    @staticmethod
    def _to_json(response_text):
        return json.loads(response_text.replace('&&&START&&&', ''))

    @staticmethod
    def _generate_nonce(millis: int):
        nonce_bytes = os.urandom(8) + (int(millis / 60000)).to_bytes(4, byteorder='big')

        return base64.b64encode(nonce_bytes).decode()

    @staticmethod
    def _generate_agent() -> str:
        agent_id = ''.join((chr(random.randint(65, 69)) for _ in range(13)))

        return f'Android-7.1.1-1.0.0-ONEPLUS A3010-136-{agent_id} APP/xiaomi.smarthome APPV/62830'

    @staticmethod
    def _generate_device_id() -> str:
        return ''.join((chr(random.randint(97, 122)) for _ in range(6)))

    @staticmethod
    def _generate_signature(url, signed_nonce, nonce, params):
        signature_params = [url.split('com')[1], signed_nonce, nonce]
        for k, v in params.items():
            signature_params.append(f'{k}={v}')
        signature_string = '&'.join(signature_params)
        signature = hmac.new(base64.b64decode(signed_nonce), msg=signature_string.encode(), digestmod=hashlib.sha256)

        return base64.b64encode(signature.digest()).decode()

    @staticmethod
    def _generate_enc_signature(url, method, signed_nonce, params):
        signature_params = [str(method).upper(), url.split('com')[1].replace('/app/', '/')]
        for k, v in params.items():
            signature_params.append(f'{k}={v}')
        signature_params.append(signed_nonce)
        signature_string = '&'.join(signature_params)

        return base64.b64encode(hashlib.sha1(signature_string.encode('utf-8')).digest()).decode()

    @staticmethod
    def _generate_enc_params(url, method, signed_nonce, nonce, params, ssecurity):
        params['rc4_hash__'] = MiCloud._generate_enc_signature(url, method, signed_nonce, params)
        for k, v in params.items():
            params[k] = MiCloud._encrypt_rc4(signed_nonce, v)
        params.update({
            'signature': MiCloud._generate_enc_signature(url, method, signed_nonce, params),
            'ssecurity': ssecurity,
            '_nonce': nonce,
        })

        return params

    @staticmethod
    def _encrypt_rc4(password: str, payload: str) -> str:
        r = ARC4(base64.b64decode(password))
        r.encrypt(bytes(1024))

        return base64.b64encode(r.encrypt(payload.encode())).decode()

    @staticmethod
    def _decrypt_rc4(password: str, payload: str) -> bytes:
        r = ARC4(base64.b64decode(password))
        r.encrypt(bytes(1024))

        return r.encrypt(base64.b64decode(payload))

    def get_devices(self):
        url = self._get_api_url() + '/home/device_list'
        data = {'getVirtualModel': False, 'getHuamiDevices': 0}
        params = {'data': json.dumps(data)}

        return self._execute_api_call_encrypted(url, params)['result']['list']

    def get_device_id(self, token: str):
        url = self._get_api_url() + '/home/device_list'
        data = {'getVirtualModel': False, 'getHuamiDevices': 0}
        params = {'data': json.dumps(data)}

        devices = self._execute_api_call_encrypted(url, params)['result']['list']

        for device in devices:
            if device['token'] == token:
                return device['did']
        return None

    def get_properties(self, did: str, mapping: dict):
        url = self._get_api_url() + '/miotspec/prop/get'
        data = {'datasource': 1, 'params': [{'did': did, **values} for values in mapping.values()]}
        params = {
            'data': json.dumps(data)
        }

        return self._execute_api_call_encrypted(url, params)

    def get_property(self, did: str, siid: int, piid: int):
        url = self._get_api_url() + '/miotspec/prop/get'
        data = {'datasource': 1, 'params': [{'did': did, 'siid': siid, 'piid': piid}]}
        params = {'data': json.dumps(data)}

        return self._execute_api_call_encrypted(url, params)['result'][0]['value']

    def set_property(self, did: str, siid: int, piid: int, value):
        url = self._get_api_url() + '/miotspec/prop/set'
        data = {'datasource': 1, 'params': [{'did': did, 'siid': siid, 'piid': piid, 'value': value}]}
        params = {'data': json.dumps(data)}

        return self._execute_api_call_encrypted(url, params)

    def call_action(self, did: str, siid: int, aiid: int, in_: list = None, out: list = None):
        url = self._get_api_url() + '/miotspec/action'
        data = {'params': {'did': did, 'siid': siid, 'aiid': aiid, 'in': in_ or [], 'out': out or []}}
        params = {'data': json.dumps(data)}

        return self._execute_api_call_encrypted(url, params)
