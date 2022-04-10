import time

import paho.mqtt.client as mqtt
import pytest

from .device import Homie, Node, State, HomieSettings
from .properties import IntProperty, FloatProperty, StringProperty, BooleanProperty, EnumProperty

TOPIC = 'test-homie'
SETTINGS = HomieSettings('mqtt.eclipseprojects.io', topic=TOPIC)


class TestHomieMqttClient:
    def __init__(self, settings: HomieSettings):
        self.topic_value_cache = {}
        self.client = mqtt.Client()
        self.client.on_connect = lambda client, user, flags, rc: client.subscribe(f'{settings.topic}/#')
        self.client.on_message = self.on_message
        self.client.connect(settings.broker, settings.port)
        self.client.loop_start()

    def on_message(self, client, user, msg):
        self.topic_value_cache[msg.topic] = msg.payload.decode('utf-8')

    def wait_for_messages(self):
        time.sleep(2)  # wild guess; maybe later I'll find a better way to wait for messages

    def cleanup(self, topic_prefix):
        for topic in self.topic_value_cache:
            if topic.startswith(topic_prefix):
                self.client.publish(topic, payload=None, qos=0, retain=True).wait_for_publish()

    def disconnect(self):
        self.client.disconnect()

    def debug(self):
        for key in self.topic_value_cache:
            print(" - %s = %s" % (key, self.topic_value_cache[key]))

    def __getitem__(self, path):
        return self.topic_value_cache[path] if path in self.topic_value_cache else None


DEV_ID = 'test-device'


class TestDevice:

    def setup_method(self, method):
        self.mqtt = TestHomieMqttClient(SETTINGS)

    def teardown_method(self, method):
        self.mqtt.cleanup(f'{TOPIC}/{DEV_ID}')
        self.mqtt.disconnect()

    def test_should_create_device(self):
        # when
        homie = Homie(SETTINGS, DEV_ID, nodes=[])
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/$state'] == 'ready'
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/$homie'] == '4.0.0'

    @pytest.mark.parametrize("set_name, expected_name", [
        (None, 'Test device'),
        ('Exactly Given Device Name', 'Exactly Given Device Name')
    ])
    def test_should_create_device_with_correct_name(self, set_name, expected_name):
        # when
        homie = Homie(SETTINGS, DEV_ID, name=set_name, nodes=[])
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/$name'] == expected_name

    def test_should_create_node(self):
        # when:
        homie = Homie(SETTINGS, DEV_ID, nodes=[
            Node("status", properties=[]),
            Node("measurements", name='Custom Name', properties=[]),
            Node("with-type", type='xyz', properties=[]),
        ])
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/$nodes'] == 'status,measurements,with-type'
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/$name'] == 'Status'
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/$type'] == 'status'
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/measurements/$name'] == 'Custom Name'
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/measurements/$type'] == 'measurements'
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/with-type/$name'] == 'With type'
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/with-type/$type'] == 'xyz'

    @pytest.mark.parametrize("property, mqtt_datatype", [
        (IntProperty("prop"), 'integer'),
        (FloatProperty("prop"), 'float'),
        (BooleanProperty("prop"), 'boolean'),
        (StringProperty("prop"), 'string'),
        (EnumProperty("prop", values=["a"]), 'enum'),
    ])
    def test_should_create_property_of_type(self, property, mqtt_datatype):
        # when
        homie = Homie(SETTINGS, DEV_ID, nodes=[
            Node("status", properties=[property])
        ])
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/$properties'] == 'prop'
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$datatype'] == mqtt_datatype

    @pytest.mark.parametrize("type", [IntProperty, FloatProperty, BooleanProperty, StringProperty, EnumProperty])
    @pytest.mark.parametrize("set,expected", [
        (None, "Prop"),
        ("Custom Name", "Custom Name")
    ])
    def test_should_create_property_with_name(self, type, set, expected):
        # when
        homie = Homie(SETTINGS, DEV_ID, nodes=[
            Node("status", properties=[create_property(type, id="prop", name=set)])
        ])
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$name'] == expected

    @pytest.mark.parametrize("type", [IntProperty, FloatProperty, BooleanProperty, StringProperty, EnumProperty])
    @pytest.mark.parametrize("set,expected", [
        (None, None),
        ("kg", "kg")
    ])
    def test_should_create_property_with_unit(self, type, set, expected):
        # when
        homie = Homie(SETTINGS, DEV_ID, nodes=[
            Node("status", properties=[create_property(type, id="prop", unit=set)])
        ])
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$unit'] == expected

    @pytest.mark.parametrize("type", [IntProperty, FloatProperty, BooleanProperty, StringProperty, EnumProperty])
    @pytest.mark.parametrize("set,expected", [
        (False, "false"),
        (True, "true"),
        (None, "true")
    ])
    def test_should_create_property_with_retained(self, type, set, expected):
        # when
        homie = Homie(SETTINGS, DEV_ID, nodes=[
            Node("status", properties=[create_property(type, id="prop", retained=set)])
        ])
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$retained'] == expected

    @pytest.mark.parametrize("type", [IntProperty, FloatProperty, BooleanProperty, StringProperty, EnumProperty])
    @pytest.mark.parametrize("set,expected", [
        (None, "false"),
        (lambda x: "", "true"),
    ])
    def test_should_create_property_with_set_handler(self, type, set, expected):
        # when
        homie = Homie(SETTINGS, DEV_ID, nodes=[
            Node("status", properties=[create_property(type, id="prop", set_handler=set)])
        ])
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$settable'] == expected

    @pytest.mark.parametrize("type", [IntProperty, FloatProperty, BooleanProperty, StringProperty, EnumProperty])
    def test_should_not_set_property_value_initially(self, type):
        # when
        homie = Homie(SETTINGS, DEV_ID, nodes=[
            Node("status", properties=[create_property(type, id="prop")])
        ])
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop'] is None

    @pytest.mark.parametrize("type,set,expected", [
        (IntProperty, 5, "5"),
        (FloatProperty, 6.0, "6.0"),
        (BooleanProperty, True, "true"),
        (StringProperty, "a", "a"),
        (EnumProperty, "a", "a")
    ])
    def test_should_create_property_with_initial_value(self, type, set, expected):
        # given
        homie = Homie(SETTINGS, DEV_ID, nodes=[
            Node("status", properties=[create_property(type, id="prop", initial_value=set)])
        ])

        # when
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop'] == expected

    @pytest.mark.parametrize("type,set,expected", [
        (IntProperty, 5, "5"),
        (FloatProperty, 6.0, "6.0"),
        (BooleanProperty, True, "true"),
        (StringProperty, "a", "a"),
        (EnumProperty, "a", "a")
    ])
    def test_should_set_property_value_using_device(self, type, set, expected):
        # given
        homie = Homie(SETTINGS, DEV_ID, nodes=[
            Node("status", properties=[create_property(type, id="prop")])
        ])

        # when
        homie['prop'] = set
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop'] == expected

    @pytest.mark.parametrize("type,set,expected", [
        (IntProperty, 5, "5"),
        (FloatProperty, 6.0, "6.0"),
        (BooleanProperty, True, "true"),
        (StringProperty, "a", "a"),
        (EnumProperty, "a", "a")
    ])
    def test_should_set_property_value_using_property(self, type, set, expected):
        # given
        property = create_property(type, id="prop")
        homie = Homie(SETTINGS, DEV_ID, nodes=[
            Node("status", properties=[property])
        ])

        # when
        property.value = set
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop'] == expected

    @pytest.mark.parametrize("type", [IntProperty, FloatProperty, BooleanProperty, StringProperty, EnumProperty])
    def test_should_create_property_without_meta(self, type):
        # when
        homie = Homie(SETTINGS, DEV_ID, nodes=[
            Node("status", properties=[create_property(type, id="prop")])
        ])
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$meta/$mainkey-ids'] is None

        # and
        assert homie.meta['prop'] == {}

    @pytest.mark.parametrize("type", [IntProperty, FloatProperty, BooleanProperty, StringProperty, EnumProperty])
    def test_should_create_property_with_meta(self, type):
        # when
        homie = Homie(SETTINGS, DEV_ID, nodes=[
            Node("status", properties=[create_property(type, id="prop", meta={'a': 'b', 'c': 'd'})])
        ])
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$meta/$mainkey-ids'] == "a,c"
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$meta/a/$key'] == "a"
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$meta/a/$value'] == "b"
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$meta/c/$key'] == "c"
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$meta/c/$value'] == "d"

        # and
        assert homie.meta['prop'] == {'a': 'b', 'c': 'd'}

    @pytest.mark.parametrize("type", [IntProperty, FloatProperty, BooleanProperty, StringProperty, EnumProperty])
    def test_should_update_metadata_using_device(self, type):
        # given
        homie = Homie(SETTINGS, DEV_ID, nodes=[
            Node("status", properties=[create_property(type, id="prop")])
        ])

        # when
        homie.meta['prop'] = {'a': 'b', 'c': 'd'}
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$meta/$mainkey-ids'] == "a,c"
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$meta/a/$key'] == "a"
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$meta/a/$value'] == "b"
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$meta/c/$key'] == "c"
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$meta/c/$value'] == "d"

        # and
        assert homie.meta['prop'] == {'a': 'b', 'c': 'd'}

    @pytest.mark.parametrize("type", [IntProperty, FloatProperty, BooleanProperty, StringProperty, EnumProperty])
    def test_should_update_metadata_using_property(self, type):
        # given
        property = create_property(type, id="prop")
        homie = Homie(SETTINGS, DEV_ID, nodes=[
            Node("status", properties=[property])
        ])

        # when
        property.meta = {'a': 'b', 'c': 'd'}
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$meta/$mainkey-ids'] == "a,c"
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$meta/a/$key'] == "a"
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$meta/a/$value'] == "b"
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$meta/c/$key'] == "c"
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$meta/c/$value'] == "d"

        # and
        assert homie.meta['prop'] == {'a': 'b', 'c': 'd'}

    @pytest.mark.parametrize("type", [IntProperty, FloatProperty])
    @pytest.mark.parametrize("min, max, expected", [
        (0, 100, "0:100"),
        (None, 100, None),
        (0, None, None)
    ])
    def test_should_create_numeric_property_with_constraints(self, type, min, max, expected):
        # given
        homie = Homie(SETTINGS, DEV_ID, nodes=[
            Node("status", properties=[create_property(type, id="prop", min_value=min, max_value=max)])
        ])

        # when
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$format'] == expected

    @pytest.mark.parametrize("type", [StringProperty])
    def test_should_create_property_with_custom_data_format(self, type):
        # given
        homie = Homie(SETTINGS, DEV_ID, nodes=[
            Node("status", properties=[create_property(type, id="prop", data_format="test")])
        ])

        # when
        self.mqtt.wait_for_messages()

        # then
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/status/prop/$format'] == "test"

    @pytest.mark.parametrize("set,expected", [
        (State.READY, "ready"),
        (State.LOST, "lost"),
        (State.SLEEPING, "sleeping"),
        (State.DISCONNECTED, "disconnected"),
        (State.ALERT, "alert"),
        (State.INIT, "init"),
    ])
    def test_should_set_device_state(self, set, expected):
        # given
        homie = Homie(SETTINGS, DEV_ID, nodes=[])

        # when
        homie.state = set
        self.mqtt.wait_for_messages()

        # then
        self.mqtt.debug()
        assert self.mqtt[f'{TOPIC}/{DEV_ID}/$state'] == expected


def create_property(type,
                    id="prop",
                    name=None,
                    unit=None,
                    retained=None,
                    set_handler=None,
                    meta=None,
                    min_value=None,
                    max_value=None,
                    data_format=None,
                    initial_value=None):
    args = {"id": id}
    if name is not None:
        args['name'] = name
    if unit is not None:
        args['unit'] = unit
    if retained is not None:
        args['retained'] = retained
    if set_handler is not None:
        args['set_handler'] = set_handler
    if meta is not None:
        args['meta'] = meta
    if min_value is not None:
        args['min_value'] = min_value
    if max_value is not None:
        args['max_value'] = max_value
    if data_format is not None:
        args['data_format'] = data_format
    if initial_value is not None:
        args['initial_value'] = initial_value

    if type == EnumProperty:
        args['values'] = ['a', 'b', 'c']
    return type(**args)
