import re
from enum import Enum, auto

import homie.device_base
from homie.device_base import Device_Base
from homie.node.node_base import Node_Base
from homie.node.property.property_base import Property_Base


def homie_name(id: str, name: str):
    return id.capitalize().replace('-', " ") if name is None else name


def to_homie4_meta(meta: dict) -> dict:
    result = {}
    for key in meta:
        value = meta[key]
        result[create_homie_id(key)] = {
            'name': key,
            'value': value
        }
    return result


def create_homie_id(group_name: str) -> str:
    normalized = group_name \
        .lower() \
        .replace('ł', 'l') \
        .replace('ę', 'e') \
        .replace('ó', 'o') \
        .replace('ą', 'a') \
        .replace('ś', 's') \
        .replace('ł', 'l') \
        .replace('ż', 'z') \
        .replace('ź', 'z') \
        .replace('ć', 'c') \
        .replace('ń', 'n')
    return re.sub(r'[^a-z0-9]', '-', normalized).lstrip('-')


class Property:
    def __init__(self, id: str, meta: dict, initial_value):
        self.id = id
        self._meta_as_key_value_dict = meta
        self._homie4_property = None
        self._initial_value = initial_value

    def setup_homie4_property(self, node: Node_Base):
        self._homie4_property = self.create_homie_property(node)
        node.add_property(self._homie4_property)

    def create_homie_property(self, node):
        # this should be overridden
        pass

    @property
    def value(self):
        return self._homie4_property.value

    @value.setter
    def value(self, value):
        self._homie4_property.value = value

    @property
    def meta(self):
        return self._meta_as_key_value_dict

    @meta.setter
    def meta(self, meta):
        self._meta_as_key_value_dict = meta
        self._homie4_property.meta = to_homie4_meta(meta)
        self._homie4_property.publish_meta()

    def raw_property(self) -> Property_Base:
        return self._homie4_property


class Node:
    def __init__(self, id: str, name: str = None, type: str = None, properties: list[Property] = []):
        self.id = id
        self.name = homie_name(id, name)
        self.type = type if type is not None else self.id
        self.properties = properties


class HomieSettings:
    def __init__(self, broker: str, port: int = 1883, username: str = None, password: str = None, topic: str = "homie"):
        self.broker = broker
        self.port = port
        self.username = username
        self.password = password
        self.topic = topic

    def to_homie4_mqtt_settings(self):
        return {
            'MQTT_BROKER': self.broker,
            'MQTT_PORT': self.port,
            'MQTT_USERNAME': self.username,
            'MQTT_PASSWORD': self.password,
            'MQTT_SHARE_CLIENT': True
        }

    def to_homie4_homie_settings(self):
        result = homie.device_base.HOMIE_SETTINGS.copy()
        result['topic'] = self.topic
        return result


class DeviceBaseWrapper(Device_Base):
    def __init__(self, settings: HomieSettings,
                 id: str,
                 name: str = None,
                 nodes: list[Node] = []):
        super().__init__(device_id=id,
                         name=homie_name(id, name),
                         mqtt_settings=settings.to_homie4_mqtt_settings(),
                         homie_settings=settings.to_homie4_homie_settings())
        self.__registered_properties_by_id = {}
        for node in nodes:
            homie4_node = Node_Base(self, node.id, node.name, node.type)
            self.add_node(homie4_node)
            for property in node.properties:
                property.setup_homie4_property(homie4_node)
                self.__registered_properties_by_id[property.id] = property
        self.start()
        for property in self.__registered_properties_by_id.values():
            if property._initial_value is not None:
                property.value = property._initial_value

    def get_property_by_id(self, property_id) -> Property:
        return self.__registered_properties_by_id[property_id]


class MetaAccessor:
    def __init__(self, device: Device_Base):
        self.device = device

    def __getitem__(self, property_id):
        return self.device.get_property_by_id(property_id).meta

    def __setitem__(self, property_id, meta_as_key_value_dict):
        self.device.get_property_by_id(property_id).meta = meta_as_key_value_dict


class State(Enum):
    READY = auto()
    ALERT = auto()
    INIT = auto()
    DISCONNECTED = auto()
    SLEEPING = auto()
    LOST = auto()

    @staticmethod
    def to_homie4_string(state):
        if state == State.READY:
            return 'ready'
        if state == State.ALERT:
            return 'alert'
        if state == State.INIT:
            return 'init'
        if state == State.DISCONNECTED:
            return 'disconnected'
        if state == State.SLEEPING:
            return 'sleeping'
        if state == State.LOST:
            return 'lost'
        raise "Unsupported state: " + state

    @staticmethod
    def from_homie4_string(str):
        if str == 'ready':
            return State.READY
        if str == 'alert':
            return State.ALERT
        if str == 'init':
            return State.INIT
        if str == 'disconnected':
            return State.DISCONNECTED
        if str == 'sleeping':
            return State.SLEEPING
        if str == 'lost':
            return State.LOST
        raise "Unsupported Homie4 state: " + str


class Homie:
    def __init__(self, settings: HomieSettings,
                 id: str,
                 name: str = None,
                 nodes: list[Node] = []):
        self._device = DeviceBaseWrapper(settings, id, name, nodes)
        self.meta = MetaAccessor(self._device)

    def __getitem__(self, property_id):
        return self._device.get_property_by_id(property_id).value

    def __setitem__(self, property_id, value):
        self._device.get_property_by_id(property_id).value = value

    @property
    def state(self):
        return State.from_homie4_string(self._device.state)

    @state.setter
    def state(self, value: State):
        self._device.state = State.to_homie4_string(value)