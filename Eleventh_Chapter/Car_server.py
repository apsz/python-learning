#!/usr/bin/python3


import os
import sys
import socketserver
import contextlib
import pickle
import gzip
import threading
import struct
import copy
import random

class Finish(Exception): pass


class CarRegistrationServer(socketserver.ThreadingMixIn,
                            socketserver.TCPServer): pass


class Car:

    def __init__(self, seats, mileage, owner):
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
    CallLock = threading.Lock()
    Call = dict(
            GET_CAR_DETAILS=(
                lambda self, *args: self.get_car_details(*args)),
            CHANGE_MILEAGE=(
                lambda self, *args: self.change_mileage(*args)),
            CHANGE_OWNER=(
                lambda self, *args: self.change_owner(*args)),
            NEW_REGISTRATION=(
                lambda self, *args: self.new_registration(*args)),
            SHUTDOWN=lambda self, *args: self.shutdown(*args))

    def handle(self):
        SizeStruct = struct.Struct('!I')
        size_data = self.rfile.read(SizeStruct.size)
        size = SizeStruct.unpack(size_data)[0]
        data = pickle.loads(self.rfile.read(size))

        try:
            with RequestHandler.CallLock:
                function = self.Call[data[0]]
            reply = function(self, *data[1:])
        except Finish:
            return
        data = pickle.dumps(reply, 3)
        self.wfile.write(SizeStruct.pack(len(data)))
        self.wfile.write(data)

    def get_car_details(self, license):
        with RequestHandler.CarsLock:
            car = copy.copy(self.Cars.get(license, None))
        if car is not None:
            return (True, car.seats, car.mileage, car.owner)
        return (False, "This license is not registered.")

    def change_mileage(self, license, mileage):
        if mileage < 0:
            return (False, 'Cannot set a negative mileage')
        with RequestHandler.CarsLock:
            car = self.Cars.get(license, None)
        if car is not None:
            if car.mileage < mileage:
                car.mileage = mileage
                return (True, None)
            return (False, 'Cannot wind the odometer back.')
        return (False, 'This license in not registered.')

    def change_owner(self, license, owner):
        if len(owner) < 2 or not isinstance(owner, str):
            return (False, 'Invalid owner: must be a string of len > 2 chars.')
        with RequestHandler.CarsLock:
            car = self.Cars.get(license, None)
        if car is not None:
            car.owner = owner
            return (True, None)
        return (False, 'This license in not registered.')

    def new_registration(self, license, seats, mileage, owner):
        if not license:
            return (False, "Cannot set an empty license")
        if seats not in {2, 4, 5, 6, 7, 8, 9}:
            return (False, "Cannot register car with invalid seats")
        if mileage < 0:
            return (False, "Cannot set a negative mileage")
        if not owner:
            return (False, "Cannot set an empty owner")
        with RequestHandler.CarsLock:
            if license not in self.Cars:
                self.Cars[license] = Car(seats, mileage, owner)
                return (True, None)
        return (False, "Cannot register duplicate license")

    def shutdown(self, *ignore):
        self.server.shutdown()
        raise Finish()


def load(filename):
    if not os.path.exists(filename):
        # Generate fake data
        cars = {}
        owners = []
        for forename, surname in zip(("Warisha", "Elysha", "Liona",
                "Kassandra", "Simone", "Halima", "Liona", "Zack",
                "Josiah", "Sam", "Braedon", "Eleni"),
                ("Chandler", "Drennan", "Stead", "Doole", "Reneau",
                 "Dent", "Sheckles", "Dent", "Reddihough", "Dodwell",
                 "Conner", "Abson")):
            owners.append(forename + " " + surname)
        for license in ("1H1890C", "FHV449", "ABK3035", "215 MZN",
                "6DQX521", "174-WWA", "999991", "DA 4020", "303 LNM",
                "BEQ 0549", "1A US923", "A37 4791", "393 TUT", "458 ARW",
                "024 HYR", "SKM 648", "1253 QA", "4EB S80", "BYC 6654",
                "SRK-423", "3DB 09J", "3C-5772F", "PYJ 996", "768-VHN",
                "262 2636", "WYZ-94L", "326-PKF", "EJB-3105", "XXN-5911",
                "HVP 283", "EKW 6345", "069 DSM", "GZB-6052", "HGD-498",
                "833-132", "1XG 831", "831-THB", "HMR-299", "A04 4HE",
                "ERG 827", "XVT-2416", "306-XXL", "530-NBE", "2-4JHJ"):
            mileage = random.randint(0, 100000)
            seats = random.choice((2, 4, 5, 6, 7))
            owner = random.choice(owners)
            cars[license] = Car(seats, mileage, owner)
        return cars
    try:
        with contextlib.closing(gzip.open(filename, 'rb')) as fh:
            return pickle.load(fh)
    except (EnvironmentError, pickle.UnpicklingError) as err:
        print('Server cannot load data: {}'.format(err))
        sys.exit(1)


def save(filename, data):
    try:
        with contextlib.closing(gzip.open(filename, 'wb')) as fh:
            pickle.dump(data, fh)
    except (EnvironmentError, pickle.PicklingError) as err:
        print('Cannot save to file: {}'.format(err))
        sys.exit(1)


def main():
    filename = os.path.join(os.path.dirname(__file__),
                            'car_registrations.dat')
    cars = load(filename)
    print(type(cars))
    print('Loaded {} car registrations'.format(len(cars)))
    RequestHandler.Cars = cars
    server = None
    try:
        server = CarRegistrationServer(('', 5819), RequestHandler)
        server.serve_forever()
    except Exception as err:
        print('Error', err)
    finally:
        if server is not None:
            server.shutdown()
            save(filename, cars)
            print('Saved {} car registrations'.format(len(cars)))


main()