#!/usr/bin/python3


def get_string(msg, item_name, default='', min_len=None, max_len=None, empty_ok=True):
    msg = '{}{}: '.format(msg, ' ({})'.format(default) if default else '')
    while True:
        usr_str = input(msg)
        if not usr_str:
            if default:
                return default
            if empty_ok:
                return
            print('{} cannot be empty'.format(item_name.capitalize()))
            continue
        if ((not min_len or min_len <= len(usr_str)) and
                (not max_len or max_len >= len(usr_str))):
            return usr_str
        print('{} invalid length.{}{}'.format(item_name.capitalize(),
                                               ' Min len is {}.'.format(min_len)
                                               if min_len else '',
                                               ' Max len is {}.'.format(min_len)
                                               if min_len else '', ))


def get_int(msg, item_name, default=None,
            min_val=None, max_val=None, empty_ok=False):
    msg = '{}{}: '.format(msg, ' ({})'.format(default) if default else '')
    while True:
        try:
            usr_int = int(input(msg))
            if usr_int == 0 and empty_ok:
                return usr_int
            if ((not min_val or min_val <= usr_int) and
                    (not max_val or max_val >= usr_int)):
                return usr_int
            print('Invalid {} value.'.format(item_name))
        except (ValueError, TypeError):
            if default and empty_ok:
                return default
            print('Not a valid integer.')


def get_bool(msg, default=''):
    while True:
        usr_input = input(msg)
        if not usr_input:
            if default:
                return False
            continue
        return True


def get_menu_option(opts_menu, valid, default=None):
    opts_menu += ' [{}]: '.format(default) if default else ''
    while True:
        usr_opt = input(opts_menu)
        if not usr_opt and default:
            return default
        if usr_opt in valid:
            return usr_opt
        print('Invalid option.')