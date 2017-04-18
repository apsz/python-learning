#!/usr/bin/python3

import sys
import collections

ID, FORENAME, MIDDLENAME, SURNAME, DEPARTMENT = range(5)


def main():
    sanity_check()

    users = {}
    User = collections.namedtuple("User", "id forename middlename surname department")
    for file in sys.argv[1:]:
        for line in open(file):
            users.update(get_user(line, users, User))
    print_formatted(users)


def sanity_check():
    if len(sys.argv) < 1 or sys.argv[1] in {'--help', '-h'}:
        print('usage: {} [file1] [file2] [fileN]...'.format(sys.argv[0]))
        sys.exit()


def get_user(line, users, User):
    user = User(*line.split(':'))
    username = get_username(user)
    count = 0
    while username in users:
        username = '{}{}'.format((username if not count else username[:-1]), count + 1)
        count += 1
    users[username] = user
    return users


def get_username(user):
    username = '{0:.1}{1:''<.1}{2:.{3}}'.format(user[FORENAME], user[MIDDLENAME],
                                                user[SURNAME], 6 if not user[MIDDLENAME] else 5)
    return username.lower()


def print_formatted(users):
    print('{:<40.40} {:^6.6} {:<9.9}'.format('Name', 'ID', 'Username'))
    print('{} {} {}'.format('-'*40, '-'*6, '-'*9))
    for username, data in sorted(users.items(), key=name_sort):
        name = '{0.surname}, {0.forename}'.format(data)
        if not data.middlename:
            name += ' {}'.format(data.forename[:1])
        print('{0:.<40.40} ({1:}) {2:<9.9}'.format(name, data.id, username))


def name_sort(item):
    return item[1].surname, item[0]


main()

