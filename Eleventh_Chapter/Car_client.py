#!/usr/bin/python3


import sys
import collections
import socket
import struct
import pickle
import Console


Address = ['localhost', 5819]
CarTuple = collections.namedtuple('CarInfo', 'seats mileage owner')


class SocketManager:

    def __init__(self, addr_tuple):
        self.addr_tuple = addr_tuple

    def __enter__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.addr_tuple)
        return self.sock

    def __exit__(self, *ignore):
        self.sock.close()


def handle_request(*items, wait_for_reply=True):
    SizeStruct = struct.Struct('!I')
    data = pickle.dumps(items, 3)

    try:
        with SocketManager(tuple(Address)) as sock:
            sock.sendall(SizeStruct.pack(len(data)))
            sock.sendall(data)
            if not wait_for_reply:
                return

            size_data = sock.recv(SizeStruct.size)
            size = SizeStruct.unpack(size_data)[0]
            result = bytearray()
            while True:
                data = sock.recv(4000)
                if not data:
                    break
                result.extend(data)
                if len(result) >= size:
                    break
        return pickle.loads(result)
    except socket.error as err:
        print('{}: is the server running?'.format(err))
        sys.exit(1)


def quit(*ignore):
    sys.exit()


def stop_server(*ignore):
    handle_request('SHUTDOWN', wait_for_reply=False)
    sys.exit()


def retrieve_car_info(prev_license):
    license = Console.get_string('License: ', 'license', prev_license)
    if not license:
        return prev_license, None
    license = license.upper()
    ok, *data = handle_request('GET_CAR_DETAILS', license)
    if not ok:
        print(data[0])
        return prev_license, None
    return license, CarTuple(*data)


def get_car_info(prev_license):
    license, car = retrieve_car_info(prev_license)
    if car is not None:
        print('License:  {license}\nSeats:  {seats}\nMileage:  {mileage}\n'
              'Owner:  {owner}\n'.format(license=license, **car._asdict()))


def change_mileage(prev_license):
    license, car = retrieve_car_info(prev_license)
    if car is None:
        return prev_license
    mileage = Console.get_int('Mileage: ', 'mileage',
                              default=car.mileage, empty_ok=True)
    if mileage == 0:
        return license
    ok, *data = handle_request('CHANGE_MILEAGE', license, mileage)
    if not ok:
        print(data[0])
    else:
        print('Mileage successfully updated.')
    return license


def change_owner(prev_license):
    license, car = retrieve_car_info(prev_license)
    if not car:
        return prev_license
    owner = Console.get_string('Owner: ', 'owner',
                               default=car.owner, min_len=2, empty_ok=True)
    ok, *data = handle_request('CHANGE_OWNER', license, owner)
    if not ok:
        print(data[0])
    else:
        print('Owner successfully update.')
    return license


def new_registration(prev_license):
    license = Console.get_string('License: ', 'license', prev_license)
    if not license:
        return prev_license
    owner = Console.get_string('Owner: ', 'owner', min_len=2, empty_ok=True)
    mileage = Console.get_int('Mileage: ', 'mileage', empty_ok=True)
    seats = Console.get_int('Seats: ', 'seats', empty_ok=True)
    ok, *data = handle_request('NEW_REGISTRATION', license, seats,
                               mileage, owner)
    if not ok:
        print(data[0])
    else:
        print('Registration of {} successfully completed.'.format(license))
    return license


def main():
    if len(sys.argv) > 1:
        Address[0] = sys.argv(1)
    calls = dict(c=get_car_info, m=change_mileage,
                 o=change_owner, n=new_registration, s=stop_server, q=quit)
    menu = ('(C)ar  (M)ileage  (O)wner  (N)ew car  '
            '(S)top server  (Q)uit)')
    valid = frozenset('cmonsq')

    previous_license = ''
    while True:
        choice = Console.get_menu_choice(menu, valid, 'c', True)
        previous_license = calls[choice.lower()](previous_license)


main()