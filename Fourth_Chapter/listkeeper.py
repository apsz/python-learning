#!/usr/bin/python3

import sys
import os
import collections

class CancelledError(Exception): pass
class NewFileError(Exception): pass


Options = collections.namedtuple("Options", "full add_qui add_del_qui")
OPTIONS = Options('AaDdSsQq', 'AaQq', 'AaDdQq')
PATH = '.'
EXTENSION = '.lst'


def main():
    saved = False
    items = []
    filename = ''
    mode = 'r'
    try:
        files = [file for file in os.listdir(PATH) if file.endswith(EXTENSION)]
        while True:
            if not filename and not items:
                filename, mode = get_filename(files)
            else:
                print_list(items)
            items = load_list(items, filename=filename)
            options = OPTIONS.full
            if not items:
                print('{:-^30}'.format('no items are in the list'))
                options = OPTIONS.add_qui
            if saved and items:
                options = OPTIONS.add_del_qui
            items, saved = process_options(options, items, filename, mode, saved)
    except CancelledError:
        if not saved:
            if (get_string('Save unsaved changes (y/n)', default='y').lower()) in {'yes', 'y'}:
                saved = save_items(items, filename, saved)
            sys.exit()


def process_options(options, items, filename, mode, saved):
    user_choice = print_options_get_choice(options)
    if user_choice in 'aA':
        new_item = get_string('Add item', 'new item', max_len=80)
        items, saved = add_item(new_item, items, saved)
    elif user_choice in 'Dd':
        while True:
            item_index = get_integer('Delete item number (or 0 to cancel)', 'item index',
                                   max_val=len(items) -1)
            if not item_index:
                break
            items, saved = del_item(item_index, items, saved)
            break
    elif user_choice in 'sS':
        saved = save_items(items, filename, saved)
    else:
        raise CancelledError
    return items, saved


def save_items(items, filename, saved, mode='w'):
    fh = None
    try:
        fh = open(filename, mode=mode)
        [fh.write(item) for item in items]
        print('Items saved in the list.')
        return True
    except (IOError, EnvironmentError) as file_err:
        print('Error while accessing the file: {}'.format(file_err))
    finally:
        if fh:
            fh.close()

def add_item(value, items, saved):
    items.append(value)
    return items, False


def del_item(index, items, saved):
    del items[index-1]
    return items, False


def print_options_get_choice(options):
    opt_msg = '[A]dd [D]elete [S]ave [Q]uit'
    if options == OPTIONS.add_qui:
        opt_msg = '[A]dd [Q]uit'
    elif options == OPTIONS.add_del_qui:
        opt_msg = '[A]dd [D]elete [Q]uit'
    while True:
        user_choice = get_string(opt_msg, 'option', 'a')
        if input_validation(user_choice):
            break
    return user_choice


def get_filename(files, mode='r'):
    try:
        if files:
            print_list(files)
            file_index = get_integer('Enter the number of the file you want or 0 for a new file',
                                     'filename', max_val=len(files) + 1)
            if not file_index:
                raise NewFileError
            return files[file_index-1], mode
        raise NewFileError
    except NewFileError:
        filename = get_string('Enter new file name', 'filename', max_len=30)
        return filename, 'w'


def open_file(filename, mode='r'):
    fh = None
    filename += EXTENSION if not filename.endswith(EXTENSION) else ''
    try:
        fh = open(filename, mode=mode)
        return fh
    except (IOError, EnvironmentError) as file_err:
        print('Error while accessing the file: {}'.format(file_err))


def load_list(l, filename='', enum_start=1, allow_empty_lines=False):
    new_list = []
    source = l
    if filename and not l:
        source = open_file(filename, mode='r')
    for index, element in enumerate(source, enum_start):
        if not element and not allow_empty_lines:
            continue
        new_list.append(element)
    return new_list


def print_list(list):
    width = 2
    if len(list) <= 10:
        width = 1
    elif len(list) > 100:
        width = 3
    if list:
        [print('{0:.{width}}: {1}'.format(str(num), element, width=width)) for num, element in enumerate(list, 1)]


def get_string(msg, name='string', default=None, min_len=1, max_len=1):
    msg += ': ' if not default else '[{}]: '.format(default)
    while True:
        try:
            value = input(msg)
            if not value:
                if default:
                    return default
            if not min_len <= len(value) <= max_len:
                print("{name} must be between {min_len} and {max_len} characters long".format(**locals()))
            return value
        except (ValueError, TypeError) as input_err:
            print('{name} must be a valid string: {input_err}'.format(**locals()))


def get_integer(msg, name='index', default=None, min_val=0, max_val=100):
    msg += ': ' if not default else '[{}]: '.format(default)
    while True:
        try:
            value = int(input(msg))
            if not min_val <= value <= max_val:
                print('{name} must be between {min_val} and {max_val}'.format(**locals()))
            return value
        except (ValueError, TypeError) as input_err:
            print('{name} must be a valid integer: {input_err}'.format(**locals()))


def input_validation(value, options=OPTIONS.full):
    if value not in options:
        print("ERROR: invalid choice--enter one of '{}'".format(options))
        return False
    return True


main()
