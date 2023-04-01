import logging
from enum import Enum

from miio.click_common import command
from miio.miot_device import DeviceStatus, MiotDevice

_LOGGER = logging.getLogger(__name__)


# Source  https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:vacuum:0000A006:ijai-v10:1
_MAPPINGS = {
    'dmaker.fan.p18': {
        'power': {'siid': 2, 'piid': 1},
        'fan_speed': {'siid': 2, 'piid': 10},
        'child_lock': {'siid': 3, 'piid': 1},
        'swing_mode': {'siid': 2, 'piid': 4},
        'swing_angle': {'siid': 2, 'piid': 5},
        'buzzer': {'siid': 2, 'piid': 8},
        'light': {'siid': 2, 'piid': 7},
        'mode': {'siid': 2, 'piid': 3},
    }
}


class FanSpeed(Enum):
    one = 1
    two = 35
    three = 70
    four = 100


class SwingMode(Enum):
    normal = 0
    auto = 1


class SwingAngle(Enum):
    min = 30
    low = 60
    medium = 90
    high = 120
    max = 140


class Standing2Status(DeviceStatus):
    def __init__(self, data):
        self.data = data

    @property
    def power(self) -> str:
        return 'on' if self.data['power'] else 'off'

    @property
    def is_on(self) -> bool:
        return self.data['power']

    @property
    def mode(self) -> SwingMode:
        return SwingMode(self.data["mode"])

    @property
    def fan_speed(self) -> FanSpeed:
        return FanSpeed(self.data["fan_speed"])

    @property
    def oscillate(self) -> bool:
        return self.data['swing_mode']

    @property
    def angle(self) -> SwingAngle:
        return SwingAngle(self.data["swing_angle"])

    @property
    def led(self) -> bool:
        return self.data['light']

    @property
    def buzzer(self) -> bool:
        return self.data['buzzer']

    @property
    def child_lock(self) -> bool:
        return self.data['child_lock']


class Standing2Fan(MiotDevice):
    _mappings = _MAPPINGS

    @command()
    def status(self) -> Standing2Status:
        return Standing2Status(
            {
                prop['did']: prop['value'] if prop['code'] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    @command()
    def on(self):
        return self.set_property('power', True)

    @command()
    def off(self):
        return self.set_property('power', False)

    @command()
    def set_mode(self, mode: SwingMode):
        return self.set_property("mode", mode.value)

    @command()
    def set_fan_speed(self, speed: FanSpeed):
        return self.set_property('fan_speed', speed.value)

    @command()
    def set_angle(self, angle: SwingAngle):
        return self.set_property('swing_angle', angle.value)

    @command()
    def set_oscillate(self, oscillate: bool):
        return self.set_property('swing_mode', oscillate)

    @command()
    def set_led(self, led: bool):
        return self.set_property('light', led)

    @command()
    def set_buzzer(self, buzzer: bool):
        return self.set_property('buzzer', buzzer)

    @command()
    def set_child_lock(self, lock: bool):
        return self.set_property('child_lock', lock)

    @property
    def yandex_info(self):
        return {
            'id': 'dmaker.fan.p18',
            'name': 'Вентилятор',
            'room': 'Гостиная',
            'type': 'devices.types.fan',
            'capabilities': [
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
                },
                {
                    'type': 'devices.capabilities.on_off',
                    'retrievable': True
                }
            ],
            'properties': []
        }

    @property
    def yandex_status(self):
        device_status = self.status()

        return {
            'id': 'dmaker.fan.p18',
            'capabilities': [
                {
                    'type': 'devices.capabilities.mode',
                    'state': {
                        'instance': 'program',
                        'value': device_status.mode.name
                    }
                },
                {
                    'type': 'devices.capabilities.mode',
                    'state': {
                        'instance': 'work_speed',
                        'value': device_status.fan_speed.name
                    }
                },
                {
                    'type': 'devices.capabilities.mode',
                    'state': {
                        'instance': 'swing',
                        'value': device_status.angle.name
                    }
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'state': {
                        'instance': 'oscillation',
                        'value': device_status.oscillate
                    }
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'state': {
                        'instance': 'controls_locked',
                        'value': device_status.child_lock
                    }
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'state': {
                        'instance': 'mute',
                        'value': not device_status.buzzer
                    }
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'state': {
                        'instance': 'backlight',
                        'value': device_status.led
                    }
                },
                {
                    'type': 'devices.capabilities.on_off',
                    'state': {
                        'instance': 'on',
                        'value': device_status.is_on
                    }
                }
            ]
        }

    def yandex_action(self, capabilities):
        capabilities_status = []

        for capability in capabilities:
            if capability['type'] == 'devices.capabilities.on_off':
                if capability['state']['value']:
                    self.on()
                else:
                    self.off()

            elif capability['type'] == 'devices.capabilities.mode':
                if capability['state']['instance'] == 'program':
                    self.set_mode(SwingMode[capability['state']['value']])
                elif capability['state']['instance'] == 'work_speed':
                    self.set_fan_speed(FanSpeed[capability['state']['value']])
                elif capability['state']['instance'] == 'swing':
                    self.set_angle(SwingAngle[capability['state']['value']])

            elif capability['type'] == 'devices.capabilities.toggle':
                if capability['state']['instance'] == 'oscillation':
                    self.set_oscillate(capability['state']['value'])
                elif capability['state']['instance'] == 'controls_locked':
                    self.set_child_lock(capability['state']['value'])
                elif capability['state']['instance'] == 'mute':
                    self.set_buzzer(not capability['state']['value'])
                elif capability['state']['instance'] == 'backlight':
                    self.set_led(capability['state']['value'])

            capabilities_status.append({
                'type': capability['type'],
                'state': {'instance': capability['state']['instance'], 'action_result': {
                    'status': 'DONE'
                }}})

        return capabilities_status
