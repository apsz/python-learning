#!/usr/bin/python3

import xml.sax.saxutils

class XmlShadow:

    def __init__(self, attribute_name):
        self.attribute_name = attribute_name

    def __get__(self, instance, owner=None):
        return xml.sax.saxutils.escape(getattr(instance,
                                               self.attribute_name))


class XmlShadowCached:

    def __init__(self, attribute_name):
        self.attribute_name = attribute_name
        self.cache = {}

    def __get__(self, instance, owner=None):
        xml_text = self.cache.get(id(instance))
        if not xml_text:
            return self.cache.setdefault(id(instance),
                   xml.sax.saxutils.escape(getattr(instance,
                   self.attribute_name)))
        return xml_text


class Product:

    __slots__ = ('__name', 'description', 'price')

    xml_name = XmlShadow('name')
    xml_description = XmlShadowCached('description')

    def __init__(self, name, description, price):
        self.__name = name
        self.description = description
        self.price = price

    @property
    def name(self):
        return self.__name

class SubProduct(Product):
    pass
