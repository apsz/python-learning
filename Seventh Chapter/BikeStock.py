#!/usr/bin/python3


import os
import struct
from . import BinaryRecordFile


_BIKE_STRUCT = struct.Struct('<8s30sid')


class Bike:

    def __init__(self, identity, name, quantity, price):
        self.__identity = identity
        self.name = name
        self.quantity = quantity
        self.price = price

    @property
    def identity(self):
        return self.__identity

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        assert len(name), 'name cannot be empty'
        self.__name = name

    @property
    def quantity(self):
        return self.__quantity

    @quantity.setter
    def quantity(self, quantity):
        assert quantity > 0 and isinstance(quantity, int), \
            'quantity must be int > 0'
        self.__quantity = quantity

    @property
    def price(self):
        return self.__price

    @price.setter
    def price(self, price):
        assert price > 0 and isinstance(price, float), \
            'price must be float > 0'
        self.__price = price


def _bike_from_record(record):
    data = list(_BIKE_STRUCT.unpack(record))
    data[0] = data[0].decode('utf-8').rstrip(b'\x00')
    data[1] = data[1].decode('utf-8').rstrip(b'\x00')
    return Bike(*data)


def _record_from_bike(bike):
    id = bike.identity.encode('utf-8').strip()
    name = bike.name.encode('utf-8').strip()
    packed = _BIKE_STRUCT.pack(id, name,
                               bike.quantity, bike.price)
    return packed


class BikeStock:

    def __int__(self, filename):
        self.__fh = BinaryRecordFile.BinaryRecordFile(filename,
                                                      _BIKE_STRUCT.size)
        self.__identity_to_index = {}
        for index in range(len(self.__fh)):
            record = self.__fh[index]
            if record is not None:
                bike = _bike_from_record(record)
                self.__identity_to_index[bike.identity] = index

    def __iter__(self):
        for i in self.__identity_to_index.keys():
            record = self.__fh[i]
            if record:
                yield _bike_from_record(record)

    def __delitem__(self, identity):
        del self.__fh[self.__identity_to_index[identity]]

    def __getitem__(self, identity):
        data = self.__fh[self.__identity_to_index[identity]]
        return _bike_from_record(data) if data else None

    def append(self, bike):
        assert isinstance(bike, Bike), ('invalid data type: '
                                        'must be Bike class')
        record = _record_from_bike(bike)
        index = len(self.__fh)
        self.__fh[index] = record
        self.__identity_to_index[bike.identity] = index

    def __change_stock(self, identity, change_amount):
        assert change_amount > 0, 'quantity cannot be less than 0'
        record = self.__fh[self.__identity_to_index[identity]]
        if not record:
            return None
        bike = _bike_from_record(record)
        bike.quantity += change_amount
        record = _record_from_bike(bike)
        self.__fh[bike.identity] = record
        return True

    def __change_name_or_price(self, identity, name=None, price=None):
        record = self.__fh[self.__identity_to_index[identity]]
        if not record:
            return None
        bike = _bike_from_record(record)
        if not name and price:
            return False
        if name:
            bike.name = name
        if price:
            bike.price = price
        self.__fh[bike.identity] = _record_from_bike(bike)
        return True

    increase_stock = (lambda self, identity, amount:
                        self.__change_stock(self, identity, amount))
    decrease_stock = (lambda self, identity, amount:
                        self.__change_stock(self, identity, -amount))
    change_name = (lambda self, identity, name:
                    self.__change_name_or_price(self, identity, name=name))
    change_price = (lambda self, identity, price:
                    self.__change_name_or_price(self, identity, price=price))

