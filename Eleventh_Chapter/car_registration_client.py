#!/usr/bin/python3


import sys
import collections
import pickle
import struct
import socket
import Console


Address = ['localhost', 6770]
CarInfo = collections.namedtuple('CarInfo', 'seats mileage owner')


class SocketManager:

    def __init__(self, conn_tuple):
        self.conn_tuple = conn_tuple

    def __enter__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.conn_tuple)
        return self.sock

    def __exit__(self, *ignore):
        self.sock.close()


def handle_request(*items, wait_for_reply=False):
    SizeStruct = struct.Struct('!I')
    data = pickle.dumps(items, 3)

    try:
        with SocketManager(tuple(Address)) as sock:
            sock.sendall(SizeStruct.pack(len(data)))
            sock.sendall(data)
            if not wait_for_reply:
                return

            get_data_size = sock.recv(SizeStruct.size)
            size = SizeStruct.unpack(get_data_size)[0]
            result = bytearray()
            while True:
                chunk = sock.recv(4000)
                if not chunk:
                    break
                result.extend(chunk)
                if len(result) >= size:
                    break
        return pickle.loads(result)
    except socket.error as err:
        print('Error: {}. Is the server up?'.format(err))
        sys.exit(1)


def stop_server(*ignore):
    handle_request('SHUTDOWN', wait_for_reply=False)
    sys.exit()


def quit(*ignore):
    sys.exit()


def retrieve_car_info(prev_license):
    license = Console.get_string('License: ', 'license',
                                 default=prev_license)
    if not license:
        return prev_license, None
    ok, *data = handle_request('GET_CAR_INFO', license)
    if not ok:
        print(data[0])
        return prev_license, None
    return license, CarInfo(*data)


def show_car_details(prev_license):
    license, car = retrieve_car_info(prev_license)
    if car is None:
        return prev_license
    print('License:  {license}\nSeats:  {seats}\n'
          'Mileage:  {mileage}\nOwner:  {owner}\n'.format(license=license,
                                                          **car._asdict()))
    return license


def change_mileage(prev_license):
    license, car = retrieve_car_info(prev_license)
    if not car:
        return prev_license
    mileage = Console.get_int('Mileage: ', 'mileage', car.mileage,
                              car.mileage, 999999, True)
    ok, *data = handle_request('CHANGE_MILEAGE', license, mileage)
    if not ok:
        print(data[0])
    else:
        print('Mileage adjusted.')
    return license


def change_owner(prev_license):
    license, car = retrieve_car_info(prev_license)
    if not car:
        return prev_license
    owner = Console.get_string('Owner: ', 'owner', car.owner,
                                2, 40, True)
    ok, *data = handle_request('CHANGE_OWNER', license, owner)
    if not ok:
        print(data[0])
    else:
        print('Owner adjusted.')
    return license


def new_registration(prev_license):
    license = Console.get_string('License: ', 'license',
                                 default=prev_license)
    if not license:
        return prev_license
    owner = Console.get_string('Owner: ', 'owner',
                               min_len=2, max_len=40)
    mileage = Console.get_int('Mileage: ', 'mileage', 0,
                              0, 999999, True)
    seats = Console.get_int('Seats: ', 'seats')
    ok, *data = handle_request('NEW_CAR', license, owner,
                               mileage, seats)
    if not ok:
        print(data[0])
    else:
        print('Car with license {} registered.'.format(license))
    return license


def main():
    if len(sys.argv) > 1:
        Address[0] = sys.argv[1]
    choice_to_func = dict(c=show_car_details, m=change_mileage,
                          o=change_owner, n=new_registration,
                          s=stop_server, q=quit)
    menu = ('(C)ar  (M)ileage  (O)wner  (N)ew car  '
            '(S)top server  (Q)uit)')
    valid_opts = frozenset('cmonsq')

    previous_license = ''
    while True:
        option_choice = Console.get_menu_choice(menu, valid_opts,
                                                previous_license)
        previous_license = choice_to_func[option_choice](previous_license)


main()

