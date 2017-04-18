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
    user_list = list(sorted(users.items(), key=name_sort))
    zipped_users = list(zip(user_list[::2], user_list[1::2]))
    count = 0
    for user1, user2 in zipped_users:
        if not count or not count % 64:
            print_header()
        print(get_line((user1, user2)))
        count += 1
    if len(user_list) - (len(zipped_users)*2):
        print(get_line((user_list[-1],)))


def print_header():
    header1 = '{:<17.17} {:^6.6} {:<9.9}'.format('Name', 'ID', 'Username')
    header2 = '{} {} {}'.format('-'*17, '-'*6, '-'*9)
    print('{0} {0}\n{1} {1}'.format(header1, header2))


def get_line(user_tuple):
    line = ''
    for user in user_tuple:
        username, data = user
        name = '{0.surname}, {0.forename}'.format(data)
        if not data.middlename:
            name += ' {}'.format(data.forename[:1])
        line += '{0:.<17.17} ({1:}) {2:<9.9} '.format(name, data.id, username)
    return line


def name_sort(item):
    return item[1].surname, item[0]


main()

