#!/usr/bin/python3

import os
import sys
import gzip
import copy
import struct
import bisect
import pickle
import threading
import contextlib
import socketserver


Version = 1


class Finish(Exception): pass


class CarRegistrationServer(socketserver.ThreadingMixIn,
                            socketserver.TCPServer): pass


class Car:

    def __init__(self, owner, seats, mileage):
        self.__seats = seats
        self.mileage = mileage
        self.owner = owner

    @property
    def seats(self):
        return self.__seats

    @property
    def mileage(self):
        return self.__mileage

    @mileage.setter
    def mileage(self, mileage):
        self.__mileage = mileage

    @property
    def owner(self):
        return self.__owner

    @owner.setter
    def owner(self, owner):
        self.__owner = owner


class RequestHandler(socketserver.StreamRequestHandler):

    CarsLock = threading.Lock()
    CallsLock = threading.Lock()
    Calls = dict(
        GET_CAR_INFO = lambda self, *args: self.get_car_info(*args),
        MODIFY_MILEAGE = lambda self, *args: self.mod_mileage(*args),
        MODIFY_OWNER=lambda self, *args: self.mod_owner(*args),
        NEW_CAR_REGISTRATION=lambda self, *args: self.new_reg(*args),
        GET_LICENSES_STARTING_WITH=lambda self, *args: self.licenses_starting_with(*args),
        SHUTDOWN=lambda self, *args: self.shutdown(*args))

    def handle(self):
        SizeStruct = struct.Struct('!IB')
        inc_data_len_enc = self.rfile.read(SizeStruct.size)
        inc_data_len, client_version = SizeStruct.unpack(inc_data_len_enc)
        data = pickle.loads(self.rfile.read(inc_data_len))

        try:
            with RequestHandler.CallsLock:
                func = self.Calls[data[0]]
            reply = func(self, *data[1:])
        except Finish:
            return

        reply_pkl = pickle.dumps(reply, 3)
        reply_len = SizeStruct.pack(len(reply_pkl), Version)
        self.wfile.write(reply_len)
        self.wfile.write(reply_pkl)

    def get_car_info(self, license):
        with RequestHandler.CarsLock:
            car = copy.copy(self.Cars.get(license, None))
        if car:
            return (True, car.owner, car.seats, car.mileage)
        return(False, 'License not found.')

    def licenses_starting_with(self, start_str):
        matching_licenses = []
        with RequestHandler.CarsLock:
            licenses = sorted([key.lower() for key in self.Cars.keys()])
        start_idx = bisect.bisect_left(licenses, start_str.lower())
        if start_idx != len(licenses):
            while True:
                if licenses[start_idx].startswith(start_str.lower()):
                    matching_licenses.append(str(licenses[start_idx]))
                    start_idx += 1
                else:
                    break
        return matching_licenses

    def mod_mileage(self, license, mileage):
        if not mileage or (mileage < 0):
            return (False, 'Mileage cannot be empty or negative.')
        with RequestHandler.CarsLock:
            car = self.Cars.get(license)
        if car:
            if car.mileage < mileage:
                car.mileage = mileage
                return (True, None)
            return (False, 'New mileage cannot be lower than current.')
        return (False, 'License not found.')

    def mod_owner(self, license, owner):
        if not owner or len(owner) < 2:
            return (False, 'Owner cannot be empty or less than 2 chars.')
        with RequestHandler.CarsLock:
            car = self.Cars.get(license)
        if car:
                car.owner = owner
                return (True, None)
        return (False, 'License not found.')

    def new_reg(self, license, owner, seats, mileage):
        if not license:
            return (False, 'License cannot be empty.')
        if not owner or len(owner) < 2:
            return (False, 'Owner cannot be empty or less than 2 chars.')
        if seats not in {1, 2, 3, 4, 5, 6, 7, 8, 9}:
            return (False, 'Seats cannot be set to invalid value.')
        if not mileage or (mileage < 0):
            return False, 'Mileage cannot be blank or negative.'
        with RequestHandler.CarsLock:
            if license not in self.Cars:
                self.Cars[license] = Car(owner, seats, mileage)
                return (True, None)
        return (False, 'Cannot register duplicate license.')

    def shutdown(self, *ignore):
        self.server.shutdown()
        raise Finish()


def save(db_name, cars):
    try:
        with contextlib.closing(gzip.open(db_name, 'wb')) as fh:
            pickle.dump(cars, fh)
    except (EnvironmentError, pickle.PicklingError) as save_err:
        print('Error while saving registrations: {}'.format(save_err))
        sys.exit(1)


def load(db_name):
    try:
        with contextlib.closing(gzip.open(db_name, 'rb')) as fh:
            return pickle.load(fh)
    except (EnvironmentError, pickle.UnpicklingError) as load_err:
        print('Error while loading registrations: {}'.format(load_err))
        sys.exit(1)


def main():
    db_name = os.path.join(os.path.dirname(__file__),
                           'car_registrations.dat')
    cars = load(db_name)
    print('Loaded {} car registrations.'.format(len(cars)))
    RequestHandler.Cars = cars
    server = None
    try:
        server = CarRegistrationServer(('', 9007), RequestHandler)
        server.serve_forever()
    except Exception as err:
        print('Error: ', err)
    finally:
        if server:
            server.shutdown()
            save(db_name, cars)
            print('{} car registrations saved.'.format(len(cars)))


main()