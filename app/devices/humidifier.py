# Пример управления увлажнителем Xiaomi

from enum import Enum

from app.clouds.mi_cloud import MiCloud
from app.config import MI_CLOUD_HUMIDIFIER_TOKEN


class FanLevel(Enum):
    one = 1
    two = 2
    three = 3
    smart = 4


class Humidifier2:
    def __init__(self, cloud: MiCloud):
        self.__cloud = cloud

        self.did = self.__cloud.get_device_id(MI_CLOUD_HUMIDIFIER_TOKEN)

        # https://home.miot-spec.com/spec/deerma.humidifier.jsq2w
        self.mapping = {
            'power': {'siid': 2, 'piid': 1},
            'fan_level': {'siid': 2, 'piid': 5},
            'target_humidity': {'siid': 2, 'piid': 6},
            'buzzer': {'siid': 5, 'piid': 1},
            'light': {'siid': 6, 'piid': 1},
            'relative_humidity': {'siid': 3, 'piid': 1},
            'temperature': {'siid': 3, 'piid': 7}
        }

    def set_power(self, power: bool) -> bool:
        return self.__cloud.set_property(did=self.did, **self.mapping['power'], value=power)

    def set_fan_level(self, fan_level: FanLevel) -> bool:
        return self.__cloud.set_property(did=self.did, **self.mapping['fan_level'], value=fan_level.value)

    def set_humidity(self, target_humidity: int) -> bool:
        if not 40 <= target_humidity <= 70:
            raise ValueError(f'Humidity must be between 40 and 70')

        return self.__cloud.set_property(did=self.did, **self.mapping['target_humidity'], value=target_humidity)

    def set_buzzer(self, buzzer: bool) -> bool:
        return self.__cloud.set_property(did=self.did, **self.mapping['buzzer'], value=buzzer)

    def set_light(self, light: bool) -> bool:
        return self.__cloud.set_property(did=self.did, **self.mapping['light'], value=light)

    @property
    def power(self) -> bool:
        return self.__cloud.get_property(did=self.did, **self.mapping['power'])

    @property
    def fan_level(self) -> str:
        return FanLevel(self.__cloud.get_property(did=self.did, **self.mapping['fan_level'])).name

    @property
    def target_humidity(self) -> int:
        return self.__cloud.get_property(did=self.did, **self.mapping['target_humidity'])

    @property
    def buzzer(self) -> bool:
        return self.__cloud.get_property(did=self.did, **self.mapping['buzzer'])

    @property
    def light(self) -> bool:
        return self.__cloud.get_property(did=self.did, **self.mapping['light'])

    @property
    def relative_humidity(self) -> int:
        print(self.__cloud.get_property(did=self.did, **self.mapping['temperature']))

        return self.__cloud.get_property(did=self.did, **self.mapping['relative_humidity'])

    @property
    def temperature(self) -> int:
        return self.__cloud.get_property(did=self.did, **self.mapping['temperature'])

    @property
    def yandex_info(self):
        return {
            'id': 'deerma.humidifier.jsq2w',
            'name': 'Увлажнитель',
            'room': 'Спальня',
            'type': 'devices.types.humidifier',
            'capabilities': [
                {
                    'type': 'devices.capabilities.on_off',
                    'retrievable': True
                },
                {
                    'type': 'devices.capabilities.mode',
                    'retrievable': True,
                    'parameters': {
                        'instance': 'program',
                        'modes': [
                            {
                                'value': 'one'
                            },
                            {
                                'value': 'two'
                            },
                            {
                                'value': 'three'
                            },
                            {
                                'value': 'smart'
                            }
                        ]
                    }
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'retrievable': True,
                    'parameters': {
                        'instance': 'mute'
                    }
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'retrievable': True,
                    'parameters': {
                        'instance': 'backlight'
                    }
                },
                {
                    'type': 'devices.capabilities.range',
                    'retrievable': True,
                    'parameters': {
                        'instance': 'humidity',
                        'range': {
                            'max': 70,
                            'min': 40,
                            'precision': 1
                        },
                        'unit': 'unit.percent'
                    }
                }
            ],
            'properties': []
        }

    @property
    def yandex_status(self):
        return {
            'id': 'deerma.humidifier.jsq2w',
            'capabilities': [
                {
                    'type': 'devices.capabilities.on_off',
                    'state': {
                        'instance': 'on',
                        'value': self.power
                    }
                },
                {
                    'type': 'devices.capabilities.mode',
                    'state': {
                        'instance': 'program',
                        'value': self.fan_level
                    }
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'state': {
                        'instance': 'mute',
                        'value': not self.buzzer
                    }
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'state': {
                        'instance': 'backlight',
                        'value': self.light
                    }
                },
                {
                    'type': 'devices.capabilities.range',
                    'state': {
                        'instance': 'humidity',
                        'value': self.target_humidity
                    }
                }
            ],
            'properties': []
        }

    def yandex_action(self, capabilities):
        capabilities_status = []

        status = 'ERROR'
        for capability in capabilities:
            if capability['type'] == 'devices.capabilities.on_off':
                if self.set_power(capability['state']['value']):
                    status = 'DONE'

            elif capability['type'] == 'devices.capabilities.mode':
                if capability['state']['instance'] == 'program':
                    if self.set_fan_level(FanLevel[capability['state']['value']]):
                        status = 'DONE'

            elif capability['type'] == 'devices.capabilities.toggle':
                if capability['state']['instance'] == 'mute':
                    if self.set_buzzer(not capability['state']['value']):
                        status = 'DONE'
                elif capability['state']['instance'] == 'backlight':
                    if self.set_light(capability['state']['value']):
                        status = 'DONE'

            elif capability['type'] == 'devices.capabilities.range':
                if capability['state']['instance'] == 'humidity':
                    if capability['state'].get('relative') is None:
                        if self.set_humidity(capability['state']['value']):
                            status = 'DONE'
                    else:
                        if self.set_humidity(self.target_humidity + capability['state']['value']):
                            status = 'DONE'

            capabilities_status.append({
                'type': capability['type'],
                'state': {'instance': capability['state']['instance'], 'action_result': {
                    'status': status
                }}})

        return capabilities_status
