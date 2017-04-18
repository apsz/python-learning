#!/usr/bin/python3

import re
import numbers


class GenericDescriptor:

    def __init__(self, getter, setter):
        self.getter = getter
        self.setter = setter

    def __get__(self, instance, owner=None):
        if not instance:
            return self
        return self.getter(instance)

    def __set__(self, instance, value):
        return self.setter(instance, value)


def valid_string(attr_name, empty_allowed=False, regex=None,
                 acceptable=None):
    def decorator(cls):
        name = '__' + attr_name
        def getter(self):
            return getattr(self, name)
        def setter(self, value):
            assert isinstance(value, str), '{} must be a valid string.'.format(name)
            if not empty_allowed and not value:
                raise ValueError('{} value may not be empty.'.format(name))
            if ((acceptable and value not in acceptable) or
                (regex and not regex.match(value))):
                    raise ValueError('{} cannot be set to value {}'.format(name, value))
            setattr(self, name, value)
        setattr(cls, attr_name, GenericDescriptor(getter, setter))
        return cls
    return decorator


def valid_number(attr_name, minimum=None, maximum=None):
    def decorator(cls):
        name = '__' + attr_name
        def getter(self):
            return getattr(self, name)
        def setter(self, value):
            assert isinstance(value, numbers.Number), '{} must ' \
                                                      'be a valid number.'.format(value)
            if ((minimum is None or value > minimum) and
                (maximum is None or value < maximum)):
                    setattr(self, name, value)
            else:
                raise ValueError('{} must be between {} and {}'.format(value,
                                                                       minimum, maximum))
        setattr(cls, attr_name, GenericDescriptor(getter, setter))
        return cls
    return decorator


@valid_string("name", empty_allowed=False)
@valid_string("productid", empty_allowed=False,
              regex=re.compile(r"[A-Z]{3}\d{4}"))
@valid_string("category", empty_allowed=False, acceptable=
              frozenset(["Consumables", "Hardware", "Software", "Media"]))
@valid_number("price", minimum=0, maximum=1e6)
@valid_number("quantity", minimum=1, maximum=1000)
class StockItem:
    def __init__(self, name, product_id, category, price, quantity):
        self.name = name
        self.product_id = product_id
        self.category = category
        self.price = price
        self.quantity = quantity