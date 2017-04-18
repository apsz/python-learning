#!/usr/bin/python3


import os
import sys
import gzip
import copy
import struct
import pickle
import threading
import contextlib
import socketserver


class Finish(Exception): pass


class CarServer(socketserver.ThreadingMixIn,
                socketserver.TCPServer): pass


class RequestHandler(socketserver.StreamRequestHandler):

    Cars = None
    CarLock = threading.Lock()
    CallLock = threading.Lock()
    Calls = dict(
        GET_CAR_INFO=lambda self, *args: self.get_car_info(*args),
        CHANGE_MILEAGE=lambda self, *args: self.change_mileage(*args),
        CHANGE_OWNER=lambda self, *args: self.change_owner(*args),
        NEW_CAR_REGISTRATION=lambda self, *args: self.new_car_registration(*args),
        SHUTDOWN=lambda self, *args: self.shutdown(*args))

    def handle(self):
        SizeStruct = struct.Struct('!I')
        read_size = self.rfile.read(SizeStruct.size)
        data_size = SizeStruct.unpack(read_size)[0]
        data = pickle.loads(self.rfile.read(data_size))

        try:
            with RequestHandler.CallLock:
                func = RequestHandler.Calls[data[0]]
            reply = func(*data[1:])
        except Finish:
            return

        data = pickle.dumps(reply, 3)
        data_size = SizeStruct.pack(len(data))
        self.wfile.write(data_size)
        self.wfile.write(data)

    def get_car_info(self, license):
        with RequestHandler.CarLock:
            car = copy.copy(self.Cars.get(license, None))
        if car:
            return (True, car.seats, car.mileage, car.owner)
        return (False, 'License {} not found '
                       'in the database.'.format(license()))

    def change_mileage(self, license, mileage):
        if mileage < 0:
            return (False, 'Cannot set negative mileage.')
        with RequestHandler.CarLock:
            car = self.Cars.get(license, None)
        if car:
            if car.mileage < mileage:
                car.mileage = mileage
                return (True, None)
            return (False, 'Cannot set lower mileage than current')
        return (False, 'License {} not found '
                       'in the database.'.format(license()))

    def change_owner(self, license, owner):
        if not owner or len(owner) < 2:
            return (False, 'Owner cannot be empty or less than 2 chars')
        with RequestHandler.CarLock:
            car = self.Cars.get(license, None)
        if car:
            car.owner = owner
            return (True, None)
        return (False, 'License {} not found '
                       'in the database.'.format(license()))

    def new_car_registration(self, license, seats, mileage, owner):
        if not license:
            return (False, 'License cannot be blank.')
        if seats not in {1, 2, 4, 5, 6, 7, 8, 9}:
            return (False, 'Cannot set invalid seats number')
        if mileage < 0:
            return (False, 'Cannot set negative mileage.')
        if not owner or len(owner) < 2:
            return (False, 'Owner cannot be blank or less than 2 chars')
        with RequestHandler.CarLock:
            if license not in self.Cars:
                self.Cars[license] = Car(owner, mileage, seats)
                return (True, None)
        return (False, 'License {} already registered'.format(license))


class Car:

    def __init__(self, owner, mileage, seats):
        self.owner = owner
        self.mileage = mileage
        self.__seats = seats

    @property
    def owner(self):
        return self.__owner

    @owner.setter
    def owner(self, owner):
        self.__owner = owner

    @property
    def mileage(self):
        return self.__mileage

    @mileage.setter
    def mileage(self, mileage):
        self.__mileage = mileage

    @property
    def seats(self):
        return self.__seats


def save(db_file, cars):
    try:
        with contextlib.closing(gzip.open(db_file, 'wb')) as fh:
            pickle.dump(db_file, fh)
    except (EnvironmentError, pickle.PicklingError) as save_err:
        print('Cannot save to file: {}'.format(save_err))
        sys.exit(1)


def load(db_file):
    try:
        with contextlib.closing(gzip.open(db_file, 'rb')) as fh:
            return pickle.load(fh)
    except (EnvironmentError, pickle.UnpicklingError) as load_err:
        print('Could not load the file: {}'.format(load_err))
        sys.exit(1)


def main():
    db_file = os.path.join(os.path.dirname(__file__),
                           'car_registrations.dat')
    cars = load(db_file)
    print('Loaded {} car registrations.'.format(len(cars)))
    RequestHandler.Cars = cars
    server = None

    try:
        server = CarServer(('', 6770), RequestHandler)
        server.serve_forever()
    except Exception as err:
        print('Error: {}'.format(err))
    finally:
        if server:
            server.shutdown()
            save(db_file, cars)
            print('Saved {} car registrations.'.format(len(cars)))


main()
