import logging
from miio.click_common import command
from miio.miot_device import DeviceStatus, MiotDevice

_LOGGER = logging.getLogger(__name__)


# Source  https://miot-spec.org/miot-spec-v2/instance?type=urn:miot-spec-v2:device:vacuum:0000A006:ijai-v10:1
_MAPPINGS = {
    'ijai.vacuum.v10': {
        'state': {'siid': 2, 'piid': 1},
        'sweep_mode': {'siid': 2, 'piid': 4},  # 0 - Sweep, 1 - Sweep And Mop, 2 - Mop
        'start': {'siid': 2, 'aiid': 1},
        'stop': {'siid': 2, 'aiid': 2},
        'home': {'siid': 3, 'aiid': 1},  # Return to base
        'battery': {'siid': 3, 'piid': 1},  # [0, 100] step 1
        'fan_speed': {'siid': 7, 'piid': 5},  # 0 - eco, 1 - standard, 2 - medium, 3 - turbo
        'water_level': {'siid': 7, 'piid': 6},  # 0 - low, 1 - medium, 2 - high
    }
}


def _enum_as_dict(cls):
    return {x.name: x.value for x in list(cls)}


class Lite2Status(DeviceStatus):
    def __init__(self, data):
        self.data = data

    @property
    def battery(self) -> int:
        return self.data['battery']

    @property
    def state(self) -> int:
        return self.data['state']

    @property
    def fan_speed(self) -> int:
        return self.data['fan_speed']

    @property
    def sweep_mode(self) -> int:
        return self.data['sweep_mode']

    @property
    def water_level(self) -> int:
        return self.data['water_level']


class Lite2Vacuum(MiotDevice):
    _mappings = _MAPPINGS

    sweep_mode_presets = ('one', 'two', 'three')
    fan_speed_presets = ('eco', 'normal', 'medium', 'turbo')

    @command()
    def status(self) -> Lite2Status:
        return Lite2Status(
            {
                prop['did']: prop['value'] if prop['code'] == 0 else None
                for prop in self.get_properties_for_mapping()
            }
        )

    @command()
    def home(self):
        return self.call_action('home')

    @command()
    def start(self) -> None:
        return self.call_action('start')

    @command()
    def stop(self):
        return self.call_action('stop')

    @command()
    def set_fan_speed(self, fan_speed: int):
        return self.set_property('fan_speed', fan_speed)

    @command()
    def set_sweep_mode(self, sweep_mode: int):
        return self.set_property('sweep_mode', sweep_mode)

    @command()
    def set_water_level(self, water_level: int):
        return self.set_property('water_level', water_level)

    @property
    def yandex_info(self):
        return {
            'id': 'ijai.vacuum.v10',
            'name': 'Пылесос',
            'room': 'Гостиная',
            'type': 'devices.types.vacuum_cleaner',
            'capabilities': [
                {
                    'type': 'devices.capabilities.mode',
                    'retrievable': True,
                    'parameters': {
                        'instance': 'cleanup_mode',
                        'modes': [
                            {
                                'value': 'one'
                            },
                            {
                                'value': 'two'
                            },
                            {
                                'value': 'three'
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
                                'value': 'eco'
                            },
                            {
                                'value': 'normal'
                            },
                            {
                                'value': 'medium'
                            },
                            {
                                'value': 'turbo'
                            }
                        ]
                    }
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'retrievable': True,
                    'parameters': {
                        'instance': 'pause'
                    }
                },
                {
                    'type': 'devices.capabilities.on_off',
                    'retrievable': True
                }
            ],
            'properties': [
                {
                    'type': 'devices.properties.float',
                    'retrievable': True,
                    'reportable': True,
                    'parameters': {
                        'instance': 'battery_level',
                        'unit': 'unit.percent'
                    }
                }
            ]
        }

    @property
    def yandex_status(self):
        device_status = self.status()

        return {
            'id': 'ijai.vacuum.v10',
            'capabilities': [
                {
                    'type': 'devices.capabilities.mode',
                    'state': {
                        'instance': 'cleanup_mode',
                        'value': self.sweep_mode_presets[device_status.sweep_mode]
                    }
                },
                {
                    'type': 'devices.capabilities.mode',
                    'state': {
                        'instance': 'work_speed',
                        'value': self.fan_speed_presets[device_status.fan_speed]
                    }
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'state': {
                        'instance': 'pause',
                        'value': device_status.state in (1, 2)
                    }
                },
                {
                    'type': 'devices.capabilities.on_off',
                    'state': {
                        'instance': 'on',
                        'value': device_status.state in (2, 5, 6, 7)
                    }
                }
            ],
            'properties': [
                {
                    'type': 'devices.properties.float',
                    'state': {
                        'instance': 'battery_level',
                        'value': device_status.battery
                    }
                }
            ]
        }

    def yandex_action(self, capabilities):
        capabilities_status = []

        for capability in capabilities:
            if capability['type'] == 'devices.capabilities.on_off':
                if capability['state']['value']:
                    self.start()
                else:
                    self.home()

            elif capability['type'] == 'devices.capabilities.mode':
                if capability['state']['instance'] == 'cleanup_mode':
                    self.set_sweep_mode(self.sweep_mode_presets.index(capability['state']['value']))
                elif capability['state']['instance'] == 'work_speed':
                    self.set_fan_speed(self.fan_speed_presets.index(capability['state']['value']))

            elif capability['type'] == 'devices.capabilities.toggle':
                if capability['state']['instance'] == 'pause':
                    self.stop() if capability['state']['value'] else self.start()

            capabilities_status.append({
                'type': capability['type'],
                'state': {'instance': capability['state']['instance'], 'action_result': {
                    'status': 'DONE'
                }}})

        return capabilities_status
