from enum import Enum

from app.cloud import MiCloud


class SweepMode(Enum):
    one = 0
    two = 1
    three = 2


class WorkSpeed(Enum):
    eco = 0
    normal = 1
    medium = 2
    turbo = 3


class WaterLevel(Enum):
    low = 0
    medium = 1
    high = 2


class Lite2Vacuum:
    def __init__(self, cloud: MiCloud):
        self.__cloud = cloud

        self.did = '474203165'

        # https://home.miot-spec.com/spec/ijai.vacuum.v10
        self.mapping = {
            'state': {'siid': 2, 'piid': 1},
            'sweep_mode': {'siid': 2, 'piid': 4},
            'work_speed': {'siid': 7, 'piid': 5},
            'water_level': {'siid': 7, 'piid': 6},
            'start': {'siid': 2, 'aiid': 1},
            'stop': {'siid': 2, 'aiid': 2},
            'home': {'siid': 3, 'aiid': 1},
            'battery': {'siid': 3, 'piid': 1}
    }

    def set_state(self, state: bool) -> bool:
        if state:
            return self.__cloud.call_action(did=self.did, **self.mapping['start'])
        return self.__cloud.call_action(did=self.did, **self.mapping['home'])

    def set_pause(self, pause: bool) -> bool:
        if pause:
            return self.__cloud.call_action(did=self.did, **self.mapping['stop'])
        return self.__cloud.call_action(did=self.did, **self.mapping['start'])

    def set_sweep_mode(self, sweep_mode: str) -> bool:
        return self.__cloud.set_property(did=self.did, **self.mapping['sweep_mode'],
                                         value=SweepMode[sweep_mode].value)

    def set_work_speed(self, work_speed: str) -> bool:
        return self.__cloud.set_property(did=self.did, **self.mapping['work_speed'],
                                         value=WorkSpeed[work_speed].value)

    def set_water_level(self, water_level: str) -> bool:
        return self.__cloud.set_property(did=self.did, **self.mapping['water_level'],
                                         value=WaterLevel[water_level].value)

    @property
    def state(self) -> bool:
        return self.__cloud.get_property(did=self.did, **self.mapping['state'])

    @property
    def sweep_mode(self) -> str:
        return SweepMode(self.__cloud.get_property(did=self.did, **self.mapping['sweep_mode'])).name

    @property
    def work_speed(self) -> str:
        return WorkSpeed(self.__cloud.get_property(did=self.did, **self.mapping['work_speed'])).name

    @property
    def water_level(self) -> str:
        return WaterLevel(self.__cloud.get_property(did=self.did, **self.mapping['water_level'])).name

    @property
    def battery(self) -> int:
        return self.__cloud.get_property(did=self.did, **self.mapping['battery'])

    @property
    def yandex_info(self):
        return {
            'id': 'ijai.vacuum.v10',
            'name': 'Пылесос',
            'room': 'Гостиная',
            'type': 'devices.types.vacuum_cleaner',
            'capabilities': [
                {
                    'type': 'devices.capabilities.on_off',
                    'retrievable': True
                },
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
        return {
            'id': 'ijai.vacuum.v10',
            'capabilities': [
                {
                    'type': 'devices.capabilities.on_off',
                    'state': {
                        'instance': 'on',
                        'value': self.state in (2, 5, 6, 7)
                    }
                },
                {
                    'type': 'devices.capabilities.mode',
                    'state': {
                        'instance': 'cleanup_mode',
                        'value': self.sweep_mode
                    }
                },
                {
                    'type': 'devices.capabilities.mode',
                    'state': {
                        'instance': 'work_speed',
                        'value': self.work_speed
                    }
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'state': {
                        'instance': 'pause',
                        'value': self.state in (1, 2)
                    }
                }
            ],
            'properties': [
                {
                    'type': 'devices.properties.float',
                    'state': {
                        'instance': 'battery_level',
                        'value': self.battery
                    }
                }
            ]
        }

    def yandex_action(self, capabilities):
        capabilities_status = []

        status = 'ERROR'
        for capability in capabilities:
            if capability['type'] == 'devices.capabilities.on_off':
                if self.set_state(capability['state']['value']):
                    status = 'DONE'

            elif capability['type'] == 'devices.capabilities.mode':
                if capability['state']['instance'] == 'cleanup_mode':
                    if self.set_sweep_mode(capability['state']['value']):
                        status = 'DONE'
                elif capability['state']['instance'] == 'work_speed':
                    if self.set_work_speed(capability['state']['value']):
                        status = 'DONE'

            elif capability['type'] == 'devices.capabilities.toggle':
                if capability['state']['instance'] == 'pause':
                    if self.set_pause(capability['state']['value']):
                        status = 'DONE'

            capabilities_status.append({
                'type': capability['type'],
                'state': {'instance': capability['state']['instance'], 'action_result': {
                    'status': status
                }}})

        return capabilities_status
