# Python3 Wi-Fi Manager Library

Simple library for managing Wi-Fi connection on Linux by Python3. Using `nmcli` as main component.
**Available actions**: connect, disconnect, view password, disable/enable Wi-Fi, find top 3 best networks to connect to and find out the current status for Wi-Fi devices.

# Example

```python
from json import dumps

wifi = WiFi_Manager()
wifi.get_networks()

print(dumps(wifi.choice_best(), indent=4))
'''
[
    {
        "channel": 60,
        "signal": 100,
        "speed": 270,
        "security": [
            "WPA1",
            "WPA2"
        ],
        "ssid": "WifiNetwork",
        "bssid": "XX:XX:XX:XX:XX:XX"
    },
    ...
]
'''

if wifi.connect('XX:XX:XX:XX:XX:XX', "SuperSecurePassword"):
    print('Connected to network!')
else:
    print('Failed!')
```

# Docs
### Disconnect from network
```python
def disconnect(self) -> bool:
```
Disconnect from any active connection. Return bool as logical result of task

### Connect to network
```python
def connect(self, bssid: str = None, password: str = None) -> bool:
```
Connect to networks by BSSID. root is required. 

Running `get_networks()` before is required

`bssid: str` - network BSSID

`password: str` - password for network or will be requested in `input()`

Return bool as logical result of task

Example:
```python
wifi = WiFi_Manager()
wifi.get_networks()

if wifi.connect('XX:XX:XX:XX:XX:XX', "SuperSecurePassword"):
    print('Connected to network!')
else:
    print('Failed!')
```

### Show Wi-Fi Devices Status
```python
def wifi_status(self) -> List[dict]:
```
Get status for all Wi-Fi Devices

Returns list of devices like:
```json
[
    {
        "device": "wdev1",
        "state": "connected",
        "to_network": "TestWifi"
    }
]
```

### Show Wi-Fi Password
```python
def wifi_password(self) -> Tuple[bool, str]:
```
Show password if any for active Wi-Fi connection

Return like: (True, "SuperSecurePassword")

### Wi-Fi Radio Power
```python
def wifi_radio(self, enabled: bool = True) -> bool:
```
Turn ON/OFF Wi-Fi Radio

Example:
```python
WiFi_Manager.wifi_radio(False)  # Wi-Fi Poweroff
```
```
enabled: bool - if True will send signal to turn ON
                if False will send signal to turn OFF
```

Return bool as logical result of task

### Choice Best Networks
```python
def choice_best(self, prefered: str = "5G") -> List[dict]:
```
Let script to choice TOP-3 networks for connect. By default 5G is prefered, filtering by SSID (no dup). Taking networks list from `self.networks`. Running `get_networks()` before is required.

Rules: signal `strengh >= 85` and best speed

`prefered: str` - supported values is `"5G"` or `"2G"`

Returns [{..}] or empty list if no rez. Output like:
```json
[
    {
        "ssid": "TestWifi",
        "bssid": "XX:XX:XX:XX:XX:XX",
        "security": ["WPA2"],
        "speed": 480,
        "channel": 100,
        "signal": 100,
    }
]
```

### Get All Available Networks
```python
def get_networks(self) -> dict:
```
Saving networks list to `self.networks` and returns it
```json
[
    {
        "ssid": "TestWifi",
        "bssid": "XX:XX:XX:XX:XX:XX",
        "security": ["WPA2"],
        "speed": 480,
        "channel": 100,
        "signal": 100,
    }
]
```
