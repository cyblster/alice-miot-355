from enum import Enum

from app.cloud import MiCloud


class FanLevel(Enum):
    one = 1
    two = 2
    three = 3
    four = 4


class Mode(Enum):
    normal = 0
    auto = 1


class Angle(Enum):
    min = 30
    low = 60
    medium = 90
    high = 120
    max = 140


class Standing2Fan:
    def __init__(self, cloud: MiCloud):
        self.__cloud = cloud

        self.did = '411582808'

        # https://home.miot-spec.com/spec/dmaker.fan.p18
        self.mapping = {
            'power': {'siid': 2, 'piid': 1},
            'mode': {'siid': 2, 'piid': 3},
            'fan_level': {'siid': 2, 'piid': 2},
            'oscillation': {'siid': 2, 'piid': 4},
            'angle': {'siid': 2, 'piid': 5},
            'child_lock': {'siid': 3, 'piid': 1},
            'buzzer': {'siid': 2, 'piid': 8},
            'light': {'siid': 2, 'piid': 7}
        }

    def set_power(self, power: bool) -> bool:
        return self.__cloud.set_property(did=self.did, **self.mapping['power'], value=power)

    def set_mode(self, mode: Mode) -> bool:
        return self.__cloud.set_property(did=self.did, **self.mapping['mode'], value=mode.value)

    def set_fan_level(self, fan_level: FanLevel) -> bool:
        return self.__cloud.set_property(did=self.did, **self.mapping['fan_level'], value=fan_level.value)

    def set_oscillation(self, oscillation: bool) -> bool:
        return self.__cloud.set_property(did=self.did, **self.mapping['oscillation'], value=oscillation)

    def set_angle(self, angle: Angle) -> bool:
        return self.__cloud.set_property(did=self.did, **self.mapping['angle'], value=angle.value)

    def set_child_lock(self, child_lock: bool) -> bool:
        return self.__cloud.set_property(did=self.did, **self.mapping['child_lock'], value=child_lock)

    def set_buzzer(self, buzzer: bool) -> bool:
        return self.__cloud.set_property(did=self.did, **self.mapping['buzzer'], value=buzzer)

    def set_light(self, light: bool) -> bool:
        return self.__cloud.set_property(did=self.did, **self.mapping['light'], value=light)

    @property
    def power(self) -> bool:
        return self.__cloud.get_property(did=self.did, **self.mapping['power'])

    @property
    def mode(self) -> str:
        return Mode(self.__cloud.get_property(did=self.did, **self.mapping['mode'])).name

    @property
    def fan_level(self) -> str:
        return FanLevel(self.__cloud.get_property(did=self.did, **self.mapping['fan_level'])).name

    @property
    def oscillation(self) -> bool:
        return self.__cloud.get_property(did=self.did, **self.mapping['oscillation'])

    @property
    def angle(self) -> str:
        return Angle(self.__cloud.get_property(did=self.did, **self.mapping['angle'])).name

    @property
    def child_lock(self) -> bool:
        return self.__cloud.get_property(did=self.did, **self.mapping['child_lock'])

    @property
    def buzzer(self) -> bool:
        return self.__cloud.get_property(did=self.did, **self.mapping['buzzer'])

    @property
    def light(self) -> bool:
        return self.__cloud.get_property(did=self.did, **self.mapping['light'])

    @property
    def yandex_info(self):
        return {
            'id': 'dmaker.fan.p18',
            'name': 'Вентилятор',
            'room': 'Гостиная',
            'type': 'devices.types.fan',
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
                                'value': 'normal'
                            },
                            {
                                'value': 'auto'
                            }
                        ]
                    }
                },
                {
                    'type': 'devices.capabilities.mode',
                    'retrievable': True,
                    'parameters': {
                        'instance': 'work_speed',
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
                                'value': 'four'
                            }
                        ]
                    }
                },
                {
                    'type': 'devices.capabilities.mode',
                    'retrievable': True,
                    'parameters': {
                        'instance': 'swing',
                        'modes': [
                            {
                                'value': 'min'
                            },
                            {
                                'value': 'low'
                            },
                            {
                                'value': 'medium'
                            },
                            {
                                'value': 'high'
                            },
                            {
                                'value': 'max'
                            }
                        ]
                    }
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'retrievable': True,
                    'parameters': {
                        'instance': 'oscillation'
                    }
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'retrievable': True,
                    'parameters': {
                        'instance': 'controls_locked'
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
                }
            ],
            'properties': []
        }

    @property
    def yandex_status(self):
        return {
            'id': 'dmaker.fan.p18',
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
                        'value': self.mode
                    }
                },
                {
                    'type': 'devices.capabilities.mode',
                    'state': {
                        'instance': 'work_speed',
                        'value': self.fan_level
                    }
                },
                {
                    'type': 'devices.capabilities.mode',
                    'state': {
                        'instance': 'swing',
                        'value': self.angle
                    }
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'state': {
                        'instance': 'oscillation',
                        'value': self.oscillation
                    }
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'state': {
                        'instance': 'controls_locked',
                        'value': self.child_lock
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
                }
            ]
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
                    if self.set_mode(Mode[capability['state']['value']]):
                        status = 'DONE'
                elif capability['state']['instance'] == 'work_speed':
                    if self.set_fan_level(FanLevel[capability['state']['value']]):
                        status = 'DONE'
                elif capability['state']['instance'] == 'swing':
                    if self.set_angle(Angle[capability['state']['value']]):
                        status = 'DONE'

            elif capability['type'] == 'devices.capabilities.toggle':
                if capability['state']['instance'] == 'oscillation':
                    if self.set_oscillation(capability['state']['value']):
                        status = 'DONE'
                elif capability['state']['instance'] == 'controls_locked':
                    if self.set_child_lock(capability['state']['value']):
                        status = 'DONE'
                elif capability['state']['instance'] == 'mute':
                    if self.set_buzzer(not capability['state']['value']):
                        status = 'DONE'
                elif capability['state']['instance'] == 'backlight':
                    if self.set_light(capability['state']['value']):
                        status = 'DONE'

            capabilities_status.append({
                'type': capability['type'],
                'state': {'instance': capability['state']['instance'], 'action_result': {
                    'status': status
                }}})

        return capabilities_status
