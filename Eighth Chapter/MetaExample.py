#!/usr/bin/python3

import collections


class LoadableSavable(type):

    def __init__(cls, cls_name, base_classes, class_dictionary):
        super().__init__(cls_name, base_classes, class_dictionary)
        assert hasattr(cls_name, 'load') and \
                isinstance(getattr(cls_name, 'load'), collections.Callable), \
                '{} has no {} method.'.format(cls_name, 'load')
        assert hasattr(cls_name, 'save') and \
                isinstance(getattr(cls_name, 'save'), collections.Callable), \
                '{} has no {} method.'.format(cls_name, 'save')

# tests:
# class Bad(metaclass=LoadableSavable):
#   pass
#
# class Good(metaclass=LoadableSavable):
#   def load(self): pass
#   def save(self): pass


class AutoSlotProperties(type):

    def __new__(mcls, cls_name, base_classes, cls_dict):
        slots = list(cls_dict.get('__slots__', []))
        for getter_name in [key for key in cls_dict
                            if key.startswith('get_')]:
            if isinstance(getter_name, collections.Callable):
                name = getter_name[4:]
                slots.append('__' + name)
                getter = cls_dict.pop(getter_name)
                setter_name = 'set_' + name
                setter = cls_dict.get(setter_name, None)
                if setter and isinstance(setter, collections.Callable):
                    del cls_dict[setter_name]
                cls_dict[name] = property(getter, setter)
        cls_dict['__slots__'] = tuple(slots)
        super().__new__(mcls, cls_name, base_classes, cls_dict)


class Product(metaclass=AutoSlotProperties):

    def __init__(self, barcode, description):
        self.__barcode = barcode
        self.description = description

    def get_barcode(self):
        return self.__barcode

    def get_description(self):
        return self.__description

    def set_description(self, description):
        if description is None or len(description) < 3:
            self.__description = '<Invalid description>'
        else:
            self.__description = description




