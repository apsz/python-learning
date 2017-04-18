#!/usr/bin/python3

import math


class ExternalStorage:

    __slots__ = ('attribute_name',)
    __storage = {}

    def __init__(self, attribute_name):
        self.attribute_name = attribute_name

    def __set__(self, instance, value):
        self.__storage[id(instance), self.attribute_name] = value

    def __get__(self, instance, owner=None):
        if not instance:
            return self
        return self.__storage[id(instance), self.attribute_name]


class ExternalStorageOnlyVal:

    __slots__ = ('attribute_name',)
    __storage = {}

    def __init__(self, attribute_name):
        self.attribute_name = attribute_name

    def __set__(self, instance, value):
        self.__storage[id(instance), self.attribute_name] = value

    def __get__(self, instance, owner=None):
        return self.__storage[id(instance), self.attribute_name]


class Point:

    __slots__ = ()

    x = ExternalStorage('x')
    y = ExternalStorageOnlyVal('y')

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def distance_from_origin(self):
        return math.hypot(self.x, self.y)

    def __eq__(self, other):
        if not isinstance(other, Point):
            raise NotImplementedError()
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return 'Point({0.x:!r} {0.y:!r})'.format(self)

    def __str__(self):
        return '({0.x:!r} {0.y:!r})'.format(self)
