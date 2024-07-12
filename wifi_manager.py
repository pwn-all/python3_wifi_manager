'''
    Python3 lib for managing Wi-Fi on Linux

    Using nmcli as main component for communicate with Wi-Fi
    Using subprocess.Popen as main python3 module for grab command output

    (c) pwn-all.net | PWN-ALL Auditing, Reviewing & Testing Cyber Risks CO. L.L.C
'''

from subprocess import Popen, PIPE, TimeoutExpired
from os import access, W_OK
from random import randint
from typing import List, Tuple


class WiFi_Manager:
    def __init__(self) -> None:
        self.networks: dict = {
            '2G': [],
            '5G': []
        }
        self.root = access('/etc/shadow', W_OK)

        self._insecure = 'Network is insecure, you really want to connect?'
        self._protected = 'Network have password, please enter password: '

        self.enc_types = ('WPA1', "WPA2", "WPA3")

    def __execute(self, command: list, task: str) -> Tuple[bool, bytes]:
        '''
            Executes commad passed by `command` param

            command: list - commad to execute; ex.: ['ls', '-la']
            task: str - task name for better understanding where is error if any

            Returns Tuple[no_error: bool, cmd_output: bytes]
        '''

        process = Popen(
            command,
            stdin=PIPE, stdout=PIPE, stderr=PIPE
        )

        try:
            output, error = process.communicate(timeout=15)
        except TimeoutExpired:
            print(f'Timeout on {task}')
            return (False, b'Timeout')

        if error:
            print(f"Error on {task}: {error}")
            return (False, error)

        return (True, output)

    def disconnect(self) -> bool:
        '''
            Disconnect from any active connection

            Return bool as logical result of task
        '''

        active_conn = None

        no_error, output = self.__execute(
            ['nmcli', '-t', '-f', 'state,connection', 'd', 'status'],
            "Active Wi-Fi Connection List"
        )

        if not no_error:
            return no_error

        for connection in output.decode().split('\n'):
            status, *name = connection.split(':')

            if status == 'connected':
                active_conn = ':'.join(name)
                break

        if not active_conn:
            print('No active connections. Already disconnected')
            return True

        no_error, output = self.__execute(
            ['nmcli', 'con', 'down', 'id', active_conn],
            "Disconnect From Wi-Fi"
        )

        if not no_error:
            return no_error

        if b'successfully deactivated' in output:
            return True
        else:
            print(f'Unexpected answer: {output}')
            return False

    def wifi_status(self) -> List[dict]:
        '''
            Get status for all Wi-Fi Devices

            Returns list of devices like:
            [
                {
                    'device': "...",
                    'state': "connected"|"disconnected"|"unavailable"|...,
                    'to_network': "..."
                }
            ]
        '''

        devices: list = []

        no_error, output = self.__execute(
            ['nmcli', '-t', 'd', 'status'],
            "Wi-Fi Devices Status"
        )

        if not no_error:
            return no_error

        for idevice in output.decode().split('\n'):
            if len(idevice.split(':')) < 4:
                continue

            device, dtype, dstate, *dname = idevice.split(':')

            if dtype != 'wifi':
                continue

            devices.append({
                'device': device,
                'state': dstate,
                'to_network': ':'.join(dname)
            })

        return devices

    def wifi_password(self) -> Tuple[bool, str]:
        '''
            Show password if any for active Wi-Fi connection

            Return Tuple[no_error: bool, password: str]
        '''

        password = ''

        no_error, output = self.__execute(
            ['nmcli', 'dev', 'wifi', 'show-password'],
            "Show Wi-Fi Password"
        )

        if not no_error:
            return (False, '')

        for line in output.decode().split('\n'):
            if line.startswith('Password: '):
                password = line.strip().replace('Password: ', '')

        return (True, password)

    def wifi_radio(self, enabled: bool = True) -> bool:
        '''
            Turn ON/OFF Wi-Fi Radio

            enabled: bool - if True will send signal to turn ON
                            if False will send signal to turn OFF

            Return bool as logical result of task
        '''

        enabled = 'on' if enabled else 'off'

        no_error, output = self.__execute(
            ['nmcli', 'radio', 'wifi', enabled],
            f"Wi-Fi Turn {enabled.upper()}"
        )

        return no_error

    def connect(self, bssid: str = None) -> bool:
        '''
            Connect to networks by BSSID. root is required
            Running `get_networks()` before is required

            bssid: str - network BSSID

            Return bool as logical result of task
        '''

        password = None

        if not self.root:
            print('No rights for connect to Wi-Fi')
            return False

        network = list(filter(
            lambda network: network['bssid'] == bssid, self.networks['2G']
        )) or list(filter(
            lambda network: network['bssid'] == bssid, self.networks['5G']
        ))

        if not network:
            print("Network not found. Check BSSID")
            return False

        network = network[0]

        if not network['security']:
            assert input(f'{self._insecure} [n/Y]').lower() == 'y', "User canceled"

        if any(map(lambda enc: enc in network['security'], self.enc_types)):
            password = input(f'{self._protected}')

        no_error, output = self.__execute(
            ['nmcli', 'd', 'wifi', 'connect', bssid] +
            ['password', password] if password else [],
            "Connect to Wi-Fi"
        )

        return no_error

    def choice_best(self, prefered: str = "5G") -> List[dict]:
        '''
            Let script to choice TOP-3 networks for connect. By default 5G is prefered,
            filtering by SSID (no dup). Taking networks list from `self.networks`
            Running `get_networks()` before is required. Rules: signal strengh >= 85 and best speed
    
            prefered: str - supported values is "5G" or "2G"

            Returns List[dict] or empty list if no rez. Output like:
            [
                {
                    'ssid': "...",
                    'bssid': "XX:XX:XX:XX:XX:XX",
                    'security': (|"WPA1"|"WPA2"|"WPA1", "WPA2"|...),
                    'speed': 1-2000, # Mbit/s
                    'channel': 1-120,
                    'signal': 1-100,
                }
            ]
        '''

        best = []

        if not self.networks['2G'] or not self.networks['5G']:
            print("Networks list is empty")
            return []

        if prefered not in self.networks:
            print("Wrong network type. Supported: 2G or 5G")
            return []

        for i in range(3):
            best.append(
                max(
                    filter(
                        lambda network: network['signal'] >= 85 and
                                        network['ssid'] not in map(
                                            lambda already_network: already_network['ssid'],
                                            best
                                        ),
                        self.networks[prefered]
                    ),
                    key=lambda network: network['speed']
                )
            )

        return best

    def get_networks(self) -> dict:
        '''
            Saving networks list to self.networks and returns it

            Return like: {
                '2G': [
                    {
                        'ssid': "...",
                        'bssid': "XX:XX:XX:XX:XX:XX",
                        'security': (|"WPA1"|"WPA2"|"WPA1", "WPA2"|...),
                        'speed': 1-2000, # Mbit/s
                        'channel': 1-120,
                        'signal': 1-100,
                    }
                ],
                '5G': [...]
            }
        '''

        dtlm = f'$TMP_DET_{randint(10101, 999999)}$'

        no_error, output = self.__execute(
            [
                'nmcli', '-t', '-f', 'chan,signal,rate,security,ssid,bssid,freq',
                'dev', 'wifi'
            ],
            "Scan For Wi-Fi Networks"
        )

        if not no_error:
            return self.networks

        for network in output.decode().split('\n'):
            if len(network.split(':')) < 7:
                continue

            network = network.replace('\\:', dtlm).split(':', 6)
            self.networks['5G' if network[6].startswith('5') else '2G'].append({
                'channel': int(network[0]),
                'signal': int(network[1]),
                'speed': int(network[2].replace(' Mbit/s', '')),
                'security': network[3].split(' '),
                'ssid': network[4].replace(dtlm, ':'),
                'bssid': network[5].replace(dtlm, ':'),
            })

        return self.networks
