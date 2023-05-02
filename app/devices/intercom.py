# Пример управления домофоном DomRu

import requests
import random


class DomRuApi:
    def __init__(self, token: str, place_id: int, control_id: int):
        self._token = token
        self._place_id = place_id
        self._control_id = control_id

    def open_door(self):
        url = f'https://api-mh.ertelecom.ru/rest/v1/places/{self._place_id}/accesscontrols/{self._control_id}/actions'
        headers = {
            'User-Agent': self.__generate_agent(),
            'Authorization': f'Bearer {self._token}'
        }
        data = {
            'name': 'accessControlOpen'
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json()['data']['status']

        return False

    @staticmethod
    def __generate_agent() -> str:
        agent_id = ''.join((chr(random.randint(65, 69)) for _ in range(13)))

        return f'Android-7.1.1-1.0.0-ONEPLUS A3010-136-{agent_id}'

    @property
    def yandex_info(self):
        return {
            'id': 'domru.intercom.355',
            'name': 'Домофон',
            'room': 'Улица',
            'type': 'devices.types.openable',
            'capabilities': [
                {
                    'type': 'devices.capabilities.on_off',
                    'retrievable': False
                }
            ],
            'properties': []
        }

    @property
    def yandex_status(self):
        return {
            'id': 'domru.intercom.355',
            'capabilities': [],
            'properties': []
        }

    def yandex_action(self, capabilities):
        capabilities_status = []

        status = 'ERROR'
        for capability in capabilities:
            if capability['type'] == 'devices.capabilities.on_off':
                if self.open_door():
                    status = 'DONE'

            capabilities_status.append({
                'type': capability['type'],
                'state': {'instance': capability['state']['instance'], 'action_result': {
                    'status': status
                }}})

        return capabilities_status
