#!/usr/bin/python3

import os
import sys


class QuitException(Exception): pass
class NewFileError(Exception): pass


def main():
    saved = True
    deleted = 0
    added = 0
    print('{:.^40}'.format('Welcome to the ListKeeper'))
    print('Options are:\n{}\n{}\n{}\n{}'.format('[A] - Add', '[D] - Delete',
                                                '[Q] - Quit', '[S] - Save'))
    files = [file for file in os.listdir('.') if file.endswith('.lst')]
    filename, items = get_filename(files)
    try:
        while True:
            options = 'ADSQ'
            if not items and saved:
                options = 'AQ'
            elif items and saved:
                options = 'ADQ'
            items, saved, added, deleted = process_options(options, filename,
                                                           items, saved, added, deleted)
    except QuitException:
        if not saved:
            if get_str('Save unsaved changes (y/n)', default='y').lower() in {'y', 'yes'}:
                save_list(filename, items, saved, added, deleted)
        sys.exit()


def get_user_choice(options, items):
    if not items:
        print('{:-^30}'.format('There are no items in the list'))
    else:
        print_list(items)
    opt_msg = ' '.join(['[{}]'.format(letter) for letter in options])
    while True:
        option_choice = get_str(opt_msg, default='a', max_len=1)
        if validate_input(option_choice, options.lower()):
            return option_choice.lower()


def process_options(options, filename, items, saved, added, deleted):
    user_choice = get_user_choice(options, items)
    if user_choice == 'a':
        new_item = get_str('Add item')
        add_item(new_item, items)
        added += 1
        saved = False
    elif user_choice == 'd':
        item_index = get_int('Index of the item to delete (or 0 to cancel)',
                             min_val=1, max_val=len(items)+1)
        if item_index:
            del_item(item_index, items)
            deleted += 1
            saved = False
    elif user_choice == 'q':
        raise QuitException
    else:
        saved, added, deleted = save_list(filename, items, saved, added, deleted)
    return items, saved, added, deleted


def save_list(filename, items, saved, added, deleted):
    fh = None
    try:
        fh = open(filename, mode='w')
        [fh.write(item + '\n') for item in items]
        print('Successfully saved {} item{} {} added and {} deleted from last save.'.format(
              len(items), 's.' if len(items) == 1 else '.', added, deleted))
        return True, 0, 0
    except (IOError, EnvironmentError) as f_err:
        print('Error: {}'.format(f_err))
    finally:
        if fh:
            fh.close()


def add_item(item, lst):
    lst.append(item)
    return lst


def del_item(item_index, lst):
    del lst[item_index-1]
    return lst


def print_list(l):
    [print('{}: {}'.format(index, element)) for index, element in enumerate(l, 1)]


def get_filename(files):
    items = []
    filename = ''
    try:
        if files:
            print_list(files)
            file_index = get_int('Please enter index of the file you want to use (or 0 for a new file)',
                                 max_val=len(files))
            if not file_index:
                raise NewFileError
            filename = files[file_index-1]
            items = get_items(filename, mode='file')
        else:
            raise NewFileError
    except NewFileError:
        filename = get_str('Enter filename for the new file')
        files.append(filename)
    finally:
        filename = filename + '.lst' if not filename.endswith('.lst') else filename
        return filename, items


def get_items(src, mode='lst', items=None):
    items = []
    source = src
    if mode == 'file':
        try:
            source = open(src, mode='r')
        except (IOError, EnvironmentError) as f_err:
            print('Error: {}'.format(f_err))
    for item in source:
        items.append(item)
    return items


def get_int(msg, name='integer', default=None, min_val=0, max_val=100):
    msg += ': ' if not default else ' [{}]: '.format(default)
    while True:
        try:
            user_int = int(input(msg))
            if not user_int and default:
                return default
            if not min_val <= user_int <= max_val:
                print('{name} value must be between {min_val} and {max_val}'.format(**locals()))
            return user_int
        except (TypeError, ValueError) as input_err:
            print('Error: {}'.format(input_err))


def get_str(msg, name='string', default=None, min_len=1, max_len=80):
    msg += ': ' if not default else ' [{}]: '.format(default)
    while True:
        try:
            user_str = input(msg)
            if not user_str and default:
                return default
            if not min_len <= len(user_str) <= max_len:
                print('{name} must be between {min_len} and {max_len} characters long'.format(**locals()))
            return user_str
        except (TypeError, ValueError) as input_err:
            print('Error: {}'.format(input_err))


def validate_input(inp, options):
    if inp not in options:
        print('ERROR: invalid choice--enter one of {}'.format(options + options.upper()))
        return False
    return True


main()
