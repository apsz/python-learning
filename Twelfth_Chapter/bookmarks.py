#!/usr/bin/python3


import os
import sys
import pickle
import shelve
import Cmd


DISPLAY_LIMIT = 10


def quit(*ignore):
    sys.exit()


def http_name_fix(name):
    return ('http://' + name) if not (name.startswith('http://')
                                      or name.startswith('https://')) else name


def add_bookm(db):
    title = Cmd.get_string('Bookmark title', 'bookmark title')
    if not title:
        return
    url = Cmd.get_string('URL', 'url')
    if not url:
        return
    url = http_name_fix(url)
    db[title] = http_name_fix(url)
    db.sync()


def edit_bookm(db):
    old_title = find_bookmark(db, 'edit')
    if not old_title:
        return
    title = Cmd.get_string('Bookmark title', 'bookmark title',
                           default=old_title)
    url = Cmd.get_string('URL', 'url', default=db[old_title])
    db[title] = http_name_fix(url)
    if old_title != title:
        del db[old_title]
    db.sync()


def remove_bookm(db):
    title = find_bookmark(db, 'remove')
    if not title:
        return
    confirmation = Cmd.get_bool('Remove {}?'.format(title), 'no')
    if confirmation:
        del db[title]
        db.sync()


def list_bookm(db):
    start_str = ''
    if len(db.keys()) > DISPLAY_LIMIT:
        start_str = Cmd.get_string('Start of) bookmark title to display '
                                   '[ENTER=all]', 'bookmark title')
    for index, bookm_name in enumerate(sorted(db.keys()), 1):
        if not start_str or bookm_name.lower().startswith(start_str.lower()):
            print('{} {:.<30} {:.40}'.format(index, bookm_name, db[bookm_name]))


def find_bookmark(db, action):
    msg = '(Start of) bookmark title to {}'.format(action)
    while True:
        lookup_title = Cmd.get_string(msg, 'bookmark title')
        if not lookup_title:
            return
        matches = []
        for title in db.keys():
            if title.lower().startswith(lookup_title.lower()):
                matches.append(title)
        if not matches:
            return None
        elif len(matches) == 1:
            return matches[0]
        elif len(matches) > DISPLAY_LIMIT:
            print('Too many bookmarks to show.'
                  'Please narrow your search.')
            continue
        else:
            for index, matched_bookm in enumerate(sorted(matches), 1):
                print('{}: {}'.format(index, matched_bookm))
            index_choice = Cmd.get_int('Index (or 0 to cancel)', 'index',
                                       min_val=1, max_val=len(matches),
                                       empty_ok=True)
            return matches[index_choice-1] if index_choice else None


def main():
    filename = os.path.join(os.path.dirname(__file__), 'bookmarks.dbm')
    menu = '(A)dd  (E)dit  (L)ist  (R)emove  (Q)uit'
    opt_to_func = dict(a=add_bookm, e=edit_bookm, l=list_bookm,
                       r=remove_bookm, q=quit)
    valid = frozenset('aelrq')

    menu_choice = 'l'
    db = None
    try:
        db = shelve.open(filename, protocol=pickle.HIGHEST_PROTOCOL)
        while True:
            menu_choice = Cmd.get_menu_option(menu, valid, default=menu_choice)
            opt_to_func[menu_choice.lower()](db)
    except (EnvironmentError, pickle.PickleError) as err:
        print('Error: ', err)
        sys.exit()
    finally:
        if db:
            db.close()


if __name__ == '__main__':
    main()

