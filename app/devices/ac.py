# Пример управления кондиционером TCL

from enum import Enum

from tcl_cloud import TclCloud


class Mode(Enum):
    auto = 0
    cool = 1
    dry = 2
    fan_only = 3
    heat = 4


class FanSpeed(Enum):  # (windSpeed, silenceSwitch, turbo)
    auto = (0, 0, 0)
    quiet = (2, 1, 0)
    low = (2, 0, 0)
    medium = (4, 0, 0)
    high = (6, 0, 0)
    turbo = (6, 0, 1)


class TclAC:
    def __init__(self, cloud: TclCloud):
        self.__cloud = cloud

        self.device_id = 'CB0AzBFAAAE'

    def set_power(self, power: bool) -> bool:
        data = {
            'powerSwitch': int(power)
        }
        return self.__cloud.send_action(self.device_id, **data)

    def set_mode(self, mode: Mode) -> bool:
        data = {
            'workMode': mode.value
        }

        return self.__cloud.send_action(self.device_id, **data)

    def set_temperature(self, temperature: int) -> bool:
        if not 16 <= temperature <= 31:
            raise ValueError(f'Temperature must be between 16 and 31')

        data = {
            'targetTemperature': temperature
        }

        return self.__cloud.send_action(self.device_id, **data)

    def set_fan_speed(self, fan_speed: FanSpeed) -> bool:
        wind_speed, silence_switch, turbo = fan_speed.value

        data = {
            'windSpeed': wind_speed,
            'silenceSwitch': silence_switch,
            'turbo': turbo
        }

        return self.__cloud.send_action(self.device_id, **data)

    @property
    def state(self) -> dict:
        return self.__cloud.get_info(self.device_id)['state']['desired']

    @property
    def power(self) -> bool:
        return bool(self.state['powerSwitch'])

    @property
    def mode(self) -> Mode:
        return Mode(self.state['workMode'])

    @property
    def target_temperature(self) -> int:
        return self.state['targetTemperature']

    @property
    def current_temperature(self) -> int:
        return self.state['currentTemperature']

    @property
    def fan_speed(self) -> FanSpeed:
        state = self.state

        return FanSpeed((state['windSpeed'], state['silenceSwitch'], state['turbo']))

    @property
    def yandex_info(self):
        return {
            'id': 'tcl.ac',
            'name': 'Кондиционер',
            'type': 'devices.types.thermostat.ac',
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
                                'value': 'auto'
                            },
                            {
                                'value': 'cool'
                            },
                            {
                                'value': 'dry'
                            },
                            {
                                'value': 'fan_only'
                            },
                            {
                                'value': 'heat'
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
                                'value': 'auto'
                            },
                            {
                                'value': 'quiet'
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
                                'value': 'turbo'
                            }
                        ]
                    }
                },
                {
                    'type': 'devices.capabilities.range',
                    'retrievable': True,
                    'parameters': {
                        'instance': 'temperature',
                        'range': {
                            'max': 31,
                            'min': 16,
                            'precision': 1
                        },
                        'unit': 'unit.temperature.celsius'
                    }
                }
            ],
            'properties': [
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
            'id': 'tcl.ac',
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
                        'value': self.mode.name
                    }
                },
                {
                    'type': 'devices.capabilities.mode',
                    'state': {
                        'instance': 'work_speed',
                        'value': self.fan_speed.name
                    }
                },
                {
                    'type': 'devices.capabilities.range',
                    'state': {
                        'instance': 'temperature',
                        'value': self.target_temperature
                    }
                }
            ],
            'properties': [
                {
                    'type': 'devices.properties.float',
                    'state': {
                        'instance': 'temperature',
                        'value': self.current_temperature
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
                    if self.set_fan_speed(FanSpeed[capability['state']['value']]):
                        status = 'DONE'

            elif capability['type'] == 'devices.capabilities.range':
                if capability['state']['instance'] == 'temperature':
                    if self.set_temperature(capability['state']['value']):
                        status = 'DONE'

            capabilities_status.append({
                'type': capability['type'],
                'state': {'instance': capability['state']['instance'], 'action_result': {
                    'status': status
                }}})

        return capabilities_status
