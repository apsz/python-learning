#!/usr/bin/python3

class Property:

    def __init__(self, getter, setter=None):
        self.__getter = getter
        self.__setter = setter
        self.__name = getter.__name__

    def __get__(self, instance, owner=None):
        if not instance:
            return self
        return self.__getter(instance)

    def __set__(self, instance, value):
        if not self.__setter:
            raise AttributeError('"{0}" is read-only'.format(
                                    self.__name__))
        return self.__setter(instance, value)

    def setter(self, setter):
        self.__setter = setter
        return self.__setter

