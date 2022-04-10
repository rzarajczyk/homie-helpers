# homie-helpers

Yet another python implementation of [Homie Convection](https://homieiot.github.io/)

In fact, it's a wrapper around another library [Homie4](https://github.com/mjcumming/homie4) - just with changed API

# Quick start

There are two possible approaches - choose one that suits you more!

### Approach 1: setting properties using device object
```python
# Let's create settings first...
SETTINGS = HomieSettings('mqtt.eclipseprojects.io', port=1883, username='...' password='...')

# Callback for 'ison' property
def set_enabled(value):
    print('Turning %s' % ('on' if value else 'off'))

# Create Homie object
# At this moment the MQTT messages will be sent!
homie = Homie(SETTINGS, "my-thermometer", nodes=[
    Node("status", properties=[
        FloatProperty("temperature", unit="C"),             # client cannot modify this property
        BooleanProperty('ison', set_handler=set_enabled)    # client CAN modify this property - will call callback
    ])
])

homie['temperature'] = 20.0
```

### Approach 2: setting properties using property objects
```python
# Let's create settings first...
SETTINGS = HomieSettings('mqtt.eclipseprojects.io', port=1883, username='...' password='...')

# Callback for 'ison' property
def set_enabled(value):
    print('Turning %s' % ('on' if value else 'off'))

property_temperature = FloatProperty("temperature", unit="C"),      # client cannot modify this property
property_ison = BooleanProperty('ison', set_handler=set_enabled)    # client CAN modify this property - will call callback 
    
# Create Homie object
# At this moment the MQTT messages will be sent!
homie = Homie(SETTINGS, "my-thermometer", nodes=[
    Node("status", properties=[property_temperature, property_ison])

property_temperature.value = 20.0
```