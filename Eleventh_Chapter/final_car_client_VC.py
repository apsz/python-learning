#!/usr/bin/python3

import sys
import socket
import pickle
import struct
import collections
import Console


Address = ['localhost', 9007]
Version = 1
CarInfo = collections.namedtuple('CarInfo', 'owner seats mileage')


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
    SizeStruct = struct.Struct('!IB')
    data = pickle.dumps(items, 3)

    try:
        with SocketManager(tuple(Address)) as sock:
            sock.sendall(SizeStruct.pack(len(data), Version))
            sock.sendall(data)
            if not wait_for_reply:
                return

            reply_len = sock.recv(SizeStruct.size)
            reply_size, version = SizeStruct.unpack(reply_len)
            if version != Version:
                print('Client - server version mismatch.\n'
                      'Server uses version {}'.format(version))
                quit()
            reply_data = bytearray()
            while True:
                chunk = sock.recv(4000)
                if not chunk:
                    break
                reply_data.extend(chunk)
                if len(reply_data) >= reply_size:
                    break
            return pickle.loads(reply_data)
    except socket.error as sock_err:
        print('Error: {}'.format(sock_err))
        sys.exit(1)


def shutdown(*ignore):
    handle_request('SHUTDOWN', wait_for_reply=False)
    sys.exit()


def quit(*ignore):
    sys.exit()


def retrieve_car_info(prev_license):
    license = Console.get_string('License', 'license', prev_license)
    if not license:
        return prev_license, None
    license = license.upper()
    ok, *data = handle_request('GET_CAR_INFO', license)
    if not ok:
        print(data[0])
        starts_with = Console.get_string('Start of license', 'start of license',
                                         default=license[0], min_len=1, empty_ok=True)
        matching_licenses = handle_request('GET_LICENSES_STARTING_WITH', starts_with)
        for opt_num, license_match in enumerate(matching_licenses, 1):
            print('({}) {}'.format(opt_num, license_match))
        opt_choice = Console.get_int('Enter choice (0 to cancel)', default=0,
                                      min_val=0, max_val=len(matching_licenses),
                                      empty_ok=False)
        if opt_choice == 0:
            return prev_license, None
        return retrieve_car_info(matching_licenses[opt_choice-1])
    return license, CarInfo(*data)


def show_car_info(prev_license):
    license, car = retrieve_car_info(prev_license)
    if car:
        print('License:  {license}\nSeats:  {seats}\n'
              'Mileage:  {mileage}\nOwner:  {owner}\n'.format(license=license,
                                                              **car._asdict()))
        return license
    return prev_license


def modify_mileage(prev_license):
    license, car = retrieve_car_info(prev_license)
    if not car:
        return prev_license
    mileage = Console.get_int('Mileage', 'mileage',
                              car.mileage, car.mileage, 999999, True)
    ok, *data = handle_request('MODIFY_MILEAGE', license, mileage)
    if not ok:
        print(data[0])
    else:
        print('Mileage changed.')
    return license


def modify_owner(prev_license):
    license, car = retrieve_car_info(prev_license)
    if not car:
        return prev_license
    owner = Console.get_string('Owner', 'owner', car.owner,
                               2, 30, True)
    ok, *data = handle_request('MODIFY_OWNER', license, owner)
    if not ok:
        print(data[0])
    else:
        print('Owner changed.')
    return license


def new_car_reg(prev_license):
    license = Console.get_string('License', 'license', prev_license)
    if not license:
        return prev_license
    owner = Console.get_string('Owner', 'owner',
                               min_len=2, max_len=30)
    mileage = Console.get_int('Mileage', 'mileage',
                              0, 0, 999999, True)
    seats = Console.get_int('Seats', 'seats', 4,
                              1, 12, True)
    ok, *data = handle_request('NEW_CAR_REGISTRATION',
                               license, owner, seats, mileage)
    if not ok:
        print(data[0])
    else:
        print('New car registered.')
    return license


def main():
    choice_to_func = dict(c=show_car_info, m=modify_mileage, o=modify_owner,
                n=new_car_reg, s=shutdown, q=quit)
    menu = ('(C)ar info  (M)ileage edit  (O)wner edit  '
            '(N)ew car registration  (S)hutdown server  (Q)uit')
    valid_opts = frozenset('cmonsq')

    prev_license = ''
    while True:
        user_choice = Console.get_menu_choice(menu, valid_opts, prev_license)
        prev_license = choice_to_func[user_choice.lower()](prev_license)


main()
