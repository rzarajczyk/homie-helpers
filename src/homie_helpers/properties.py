from homie.node.property.property_boolean import Property_Boolean
from homie.node.property.property_enum import Property_Enum
from homie.node.property.property_float import Property_Float
from homie.node.property.property_integer import Property_Integer
from homie.node.property.property_string import Property_String

from .device import Property, homie_name, to_homie4_meta


class IntProperty(Property):
    def __init__(self,
                 id: str,
                 name: str = None,
                 set_handler=None,
                 unit: str = None,
                 retained: bool = True,
                 meta: dict = {},
                 min_value: int = None,
                 max_value: int = None,
                 initial_value = None):
        super().__init__(id, meta, initial_value)
        self.name = homie_name(id, name)
        self.set_handler = set_handler
        self.unit = unit
        self.retained = retained
        self.min_value = min_value
        self.max_value = max_value

    def create_homie_property(self, node):
        data_format = "%s:%s" % (
            self.min_value, self.max_value) if self.min_value is not None and self.max_value is not None else None
        return Property_Integer(node,
                                id=self.id,
                                name=self.name,
                                settable=self.set_handler is not None,
                                unit=self.unit,
                                data_format=data_format,
                                set_value=self.set_handler,
                                retained=self.retained,
                                meta=to_homie4_meta(self.meta))


class FloatProperty(Property):
    def __init__(self,
                 id: str,
                 name: str = None,
                 set_handler=None,
                 unit: str = None,
                 retained: bool = True,
                 meta: dict = {},
                 min_value: int = None,
                 max_value: int = None,
                 initial_value = None):
        super().__init__(id, meta, initial_value)
        self.name = homie_name(id, name)
        self.set_handler = set_handler
        self.unit = unit
        self.retained = retained
        self.min_value = min_value
        self.max_value = max_value

    def create_homie_property(self, node):
        data_format = "%s:%s" % (
            self.min_value, self.max_value) if self.min_value is not None and self.max_value is not None else None
        return Property_Float(node,
                              id=self.id,
                              name=self.name,
                              settable=self.set_handler is not None,
                              unit=self.unit,
                              data_format=data_format,
                              set_value=self.set_handler,
                              retained=self.retained,
                              meta=to_homie4_meta(self.meta))


class BooleanProperty(Property):
    def __init__(self,
                 id: str,
                 name: str = None,
                 set_handler=None,
                 unit: str = None,
                 retained: bool = True,
                 meta: dict = {},
                 initial_value = None):
        super().__init__(id, meta, initial_value)
        self.name = homie_name(id, name)
        self.set_handler = set_handler
        self.unit = unit
        self.retained = retained

    def create_homie_property(self, node):
        return Property_Boolean(node,
                                id=self.id,
                                name=self.name,
                                settable=self.set_handler is not None,
                                unit=self.unit,
                                set_value=self.set_handler,
                                retained=self.retained,
                                meta=to_homie4_meta(self.meta))


class EnumProperty(Property):
    def __init__(self,
                 id: str,
                 name: str = None,
                 set_handler=None,
                 unit: str = None,
                 retained: bool = True,
                 meta: dict = {},
                 values: list = [],
                 initial_value = None):
        super().__init__(id, meta, initial_value)
        self.name = homie_name(id, name)
        self.set_handler = set_handler
        self.unit = unit
        self.retained = retained
        self.values = values

    def create_homie_property(self, node):
        return Property_Enum(node,
                             id=self.id,
                             name=self.name,
                             settable=self.set_handler is not None,
                             unit=self.unit,
                             set_value=self.set_handler,
                             meta=to_homie4_meta(self.meta),
                             retained=self.retained,
                             data_format=",".join(self.values))


class StringProperty(Property):
    def __init__(self,
                 id: str,
                 name: str = None,
                 set_handler=None,
                 unit: str = None,
                 retained: bool = True,
                 meta: dict = {},
                 data_format: str = None,
                 initial_value = None):
        super().__init__(id, meta, initial_value)
        self.name = homie_name(id, name)
        self.set_handler = set_handler
        self.unit = unit
        self.retained = retained
        self.data_format = data_format

    def create_homie_property(self, node):
        return Property_String(node,
                               id=self.id,
                               name=self.name,
                               settable=self.set_handler is not None,
                               unit=self.unit,
                               set_value=self.set_handler,
                               retained=self.retained,
                               meta=to_homie4_meta(self.meta),
                               data_format=self.data_format)
