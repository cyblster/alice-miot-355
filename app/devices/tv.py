import socket
import struct
import subprocess
from ppadb.client import Client


class MiTvP1:
    def __init__(self, host, mac, port=5555, adb_host='127.0.0.1', adb_port=5037):
        self.host = host
        self.mac = mac
        self.port = port

        subprocess.run('adb start-server', capture_output=True)
        self._adb_client = Client(adb_host, adb_port)

    def _run_shell(self, cmd: str):
        tv = self._adb_connection
        if tv:
            return {
                'success': True,
                'stdout': tv.shell(cmd, timeout=2).rstrip()
            }
        return {
            'success': False,
            'stdout': None
        }

    def _send_keyevent(self, keycode: int):
        return self._run_shell(f'input keyevent {keycode}')['success']

    def set_mute(self, mute: bool) -> bool:
        if mute is not self.mute:
            self._send_keyevent(164)

        return True

    def set_volume(self, volume):
        volume = 0 if volume < 0 else 100 if volume > 100 else volume

        return self._run_shell(f'media volume --show --stream 3 --set {volume}')['success']

    @property
    def _adb_connection(self):
        try:
            subprocess.run(f'adb connect {self.host}:{self.port}', capture_output=True, timeout=0.5)
            return self._adb_client.device(f'{self.host}:{self.port}')
        except subprocess.TimeoutExpired:
            return None

    @property
    def is_on(self):
        shell_output = self._run_shell('dumpsys input_method | grep mInteractive=true')
        if shell_output['success']:
            return shell_output != ''

        return False

    @property
    def volume(self):
        shell_output = self._run_shell('dumpsys audio | grep STREAM_MUSIC -A 4 | grep streamVolume | cut -c17-')

        return int(shell_output['stdout']) if shell_output['success'] else 0

    @property
    def mute(self) -> bool:
        return self._run_shell(
            'dumpsys audio | grep STREAM_MUSIC -A 1 | grep Muted: | cut -c11-'
        )['stdout'] == 'true'

    @property
    def yandex_info(self):
        return {
            'id': 'xiaomi.tv.p1',
            'name': 'Телевизор',
            'room': 'Гостиная',
            'type': 'devices.types.media_device.tv',
            'capabilities': [
                {
                    'type': 'devices.capabilities.on_off',
                    'retrievable': True
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'retrievable': True,
                    'reportable': False,
                    'parameters': {
                        'instance': 'mute'
                    }
                },
                {
                    'type': 'devices.capabilities.range',
                    'retrievable': True,
                    'parameters': {
                        'instance': 'volume',
                        'unit': 'unit.percent',
                        'range': {
                            'min': 0,
                            'max': 100,
                            'precision': 5
                        }
                    }
                }
            ]
        }

    @property
    def yandex_status(self):
        return {
            'id': 'xiaomi.tv.p1',
            'capabilities': [
                {
                    'type': 'devices.capabilities.on_off',
                    'state': {
                        'instance': 'on',
                        'value': self.is_on
                    }
                },
                {
                    'type': 'devices.capabilities.toggle',
                    'state': {
                        'instance': 'mute',
                        'value': self.mute
                    }
                },
                {
                    'type': 'devices.capabilities.range',
                    'state': {
                        'instance': 'volume',
                        'value': self.volume
                    }
                }
            ]
        }

    def yandex_action(self, capabilities):
        capabilities_status = []

        for capability in capabilities:
            status = 'ERROR'
            if capability['type'] == 'devices.capabilities.toggle':
                if capability['state']['instance'] == 'mute':
                    if self.set_mute(capability['state']['value']):
                        status = 'DONE'

            elif capability['type'] == 'devices.capabilities.range':
                if capability['state']['instance'] == 'volume':
                    if capability['state'].get('relative') is None:
                        if self.set_volume(capability['state']['value']):
                            status = 'DONE'

            capabilities_status.append({
                'type': capability['type'],
                'state': {'instance': capability['state']['instance'], 'action_result': {
                    'status': status
                }}})

        return capabilities_status
