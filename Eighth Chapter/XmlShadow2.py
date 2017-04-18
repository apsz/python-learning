#!/usr/bin/python3

import xml.sax.saxutils

class XmlShadow:

    def __init__(self, attribute_name):
        self.attribute_name = attribute_name

    def __get__(self, instance, owner=None):
        return xml.sax.saxutils.escape(getattr(instance,
                                               self.attribute_name))

class XmlShadowCached:

    __slots__ = ('attribute_name',)
    cache = {}

    def __init__(self, attribute_name):
        self.attribute_name = attribute_name

    def __get__(self, instance, owner=None):
        xml_text = self.cache.get(id(instance))
        if xml_text:
            return xml_text
        return self.cache.setdefault(id(instance),
                                     xml.sax.saxutils.escape(
                                     getattr(self.attribute_name)))