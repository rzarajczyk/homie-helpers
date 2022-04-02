# homie-helpers

Set of helpers for making https://github.com/mjcumming/Homie4 more developer-friendly.

## Example

```python
from homie.device_base import Device_Base
from homie_helpers import add_property_int, add_property_boolean, add_property_string


class SonyBravia(Device_Base):
    def __init__(self, device_id, mqtt_settings):
        super().__init__(device_id=device_id, name="Sony Bravia Android TV", mqtt_settings=mqtt_settings)

        self.property_volume = add_property_int(self, "volume-level",
                                                parent_node_id='volume',
                                                min_value=0,
                                                max_value=80,
                                                set_handler=self.set_volume)

        add_property_boolean(self, "reboot", parent_node_id='power', retained=False, set_handler=self.reboot)

        self.property_player_app = add_property_string(self, "player-app", parent_node_id="player")
```

## Available helpers

```python
def add_property_int(device: Device_Base,
                     property_id: str,
                     property_name: str = None,
                     parent_node_id: str = "status",
                     parent_node_name: str = None,
                     set_handler=None,
                     unit=None,
                     min_value: int = None,
                     max_value: int = None,
                     meta: dict = {}) -> Property
```

```python
def add_property_float(device: Device_Base,
                       property_id: str,
                       property_name: str = None,
                       parent_node_id: str = "status",
                       parent_node_name: str = None,
                       set_handler=None,
                       unit=None,
                       min_value: int = None,
                       max_value: int = None,
                       meta: dict = {}) -> Property
```

```python
def add_property_boolean(device: Device_Base,
                         property_id: str,
                         property_name: str = None,
                         parent_node_id: str = "status",
                         parent_node_name: str = None,
                         set_handler=None,
                         retained: bool = True,
                         unit=None,
                         meta: dict = {}) -> Property
```

```python
def add_property_enum(device: Device_Base,
                      property_id: str,
                      property_name: str = None,
                      parent_node_id: str = "status",
                      parent_node_name: str = None,
                      set_handler=None,
                      unit=None,
                      values: list = [],
                      meta: dict = {}) -> Property
```

```python
def add_property_string(device: Device_Base,
                        property_id: str,
                        property_name: str = None,
                        parent_node_id: str = "status",
                        parent_node_name: str = None,
                        retained: bool = True,
                        unit: str = None,
                        data_format: str = None,
                        set_handler=None,
                        meta: dict = {}) -> Property
```

All of these helpers return an object of class `Property`, which is a wrapper around `Property_Base` from Homie4.
`Property` has the following members:

* property `value` - the value of property
* property `meta` - the metadata in a simple key-value dict format
* method `raw_property()` - returns the underlying `Property_Base` object

All of these helpers accept `meta` as dict (a simple key-value dict). It will be automatically converted to required
format.