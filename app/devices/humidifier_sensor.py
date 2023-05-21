# Пример управления увлажнителем Xiaomi

from enum import Enum

from app.clouds.mi_cloud import MiCloud
from app.config import MI_CLOUD_HUMIDIFIER_TOKEN

from .humidifier import Humidifier2


class FanLevel(Enum):
    one = 1
    two = 2
    three = 3
    smart = 4


class Humidifier2Sensor(Humidifier2):
    @property
    def yandex_info(self):
        return {
            'id': 'deerma.humidifier.jsq2w.sensor',
            'name': 'Метеостанция',
            'room': 'Спальня',
            'type': 'devices.types.sensor',
            'capabilities': [],
            'properties': [
                {
                    'type': 'devices.properties.float',
                    'retrievable': True,
                    'reportable': True,
                    'parameters': {
                        'instance': 'humidity',
                        'unit': 'unit.percent'
                    }
                },
                {
                    'type': 'devices.properties.float',
                    'retrievable': True,
                    'reportable': True,
                    'parameters': {
                        'instance': 'temperature',
                        'unit': 'unit.temperature.celsius'
                    }
                }
            ]
        }

    @property
    def yandex_status(self):
        return {
            'id': 'deerma.humidifier.jsq2w.sensor',
            'capabilities': [],
            'properties': [
                {
                    'type': 'devices.properties.float',
                    'state': {
                        'instance': 'temperature',
                        'value': self.temperature
                    }
                },
                {
                    'type': 'devices.properties.float',
                    'state': {
                        'instance': 'temperature',
                        'value': self.relative_humidity
                    }
                }
            ]
        }

    def yandex_action(self, capabilities):
        pass
