#!/usr/bin/python3

def get_string(msg, arg_name='', default=None,
               min_len=0, max_len=100, empty_ok=True):
    msg += ' [{}]:'.format(default) if default else ':'
    while True:
        user_choice = input(msg)
        if not user_choice:
            if default and empty_ok:
                return default
            continue
        if not (min_len <= len(user_choice) <= max_len):
            print('Invalid {}: must be between {} and {} '
                  'chars'.format(arg_name, min_len, max_len))
            continue
        return user_choice


def get_int(msg, arg_name='', default=None,
            min_val=0, max_val=100, empty_ok=True):
    msg += ' [{}]:'.format(default) if default else ':'
    while True:
        user_choice = input(msg)
        if not user_choice:
            if default and empty_ok:
                return default
            continue
        try:
            user_choice = int(user_choice)
            if min_val <= user_choice <= max_val:
                return user_choice
            print('Invalid {}: must be between {} and {}'.format(
                  arg_name, min_val, max_val))
        except (ValueError, TypeError):
            print('Not a valid integer.')


def get_menu_choice(menu, valid_choices, default=None, empty_ok=False):
    default_str = '{}'.format(' [{}] '.format(default) if default else '')
    while True:
        user_choice = input('{}{}:'.format(menu, default_str))
        if not user_choice:
            if empty_ok and default:
                return default
            continue
        else:
            if user_choice.lower() in valid_choices:
                return user_choice
            continue