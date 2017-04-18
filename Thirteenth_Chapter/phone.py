#!/usr/bin/python3


import re


def main():
    us_phone_re = re.compile(r'[\b(]?(\d{3})\)?(?:[- ])?(\d{3})(?:[- ])?(\d{4})\b')
    while True:
        try:
            match = re.match(us_phone_re, input('U.S. phone number: '))
            if match:
                print('({}) {} {}'.format(match.group(1), match.group(2), match.group(3)))
            else:
                raise ValueError
        except (ValueError, TypeError):
            print('Not a valid US phone number.')


if __name__ == '__main__':
    main()