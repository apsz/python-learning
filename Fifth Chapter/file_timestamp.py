#!/usr/bin/python3

import os
import time

date_from_name = {}
path = os.getcwd()

def main():
    for name in os.listdir(path):
        fullname = os.path.join(path, name)
        if os.path.isfile(fullname):
            date_from_name[fullname] = time.strftime('%Y-%m-%d %H:%M:%S',
                                                     time.gmtime(os.path.getmtime(name)))

    for key in date_from_name.keys():
        print(key, date_from_name[key])


main()