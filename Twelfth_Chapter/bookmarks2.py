#!/usr/bin/python3

import os
import sys
import shelve
import pickle
import Cmd


fix_input_url = (lambda x: 'http://' + x
    if not (x.startswith('http://') or x.startswith('https://')) else x)


def list_bookm(db):
    for index, bookm_name in enumerate(sorted(db), 1):
        print('({}) {:.<30} {:.40}'.format(index, bookm_name, db[bookm_name]))


def add_bookm(db):
    bookm_title = Cmd.get_string('Bookmark title', 'bookmark title')
    if not bookm_title:
        return
    url = Cmd.get_string('URL', 'url')
    if not url:
        return
    db[bookm_title] = fix_input_url(url)
    db.sync()


def edit_bookm(db):
    old_name = find_bookmark(db, 'edit')
    if not old_name:
        return
    bookm_title = Cmd.get_string('Bookmark title', 'bookmark title', old_name)
    if not bookm_title:
        return
    url = Cmd.get_string('URL', 'url', db[old_name])
    if not url:
        return
    db[bookm_title] = fix_input_url(url)
    if bookm_title != old_name:
        del db[old_name]
    db.sync()


def remove_bookm(db):
    bookm_name = find_bookmark(db, 'remove')
    if not bookm_name:
        return
    confirmation = Cmd.get_bool('Remove {}?'.format(bookm_name), 'no')
    if confirmation:
        del db[bookm_name]
        db.sync()


def find_bookmark(db, action):
    msg = 'Index of bookmark to {}'.format(action)
    index = Cmd.get_int(msg, 'bookmark index', min_val=0, max_val=len(db))
    if not index:
        return
    for idx, name in enumerate(sorted(db.keys()), 1):
        if index == idx:
            return name


def quit(*ignore):
    sys.exit()


def main():
    filename = os.path.join(os.path.dirname(__file__), 'bookmarks2.dbm')
    menu = '(A)dd  (E)dit  (L)ist  (R)emove  (Q)uit'
    opt_to_func = dict(a=add_bookm, e=edit_bookm, l=list_bookm,
                       r=remove_bookm, q=quit)

    db = None
    try:
        db = shelve.open(filename, protocol=pickle.HIGHEST_PROTOCOL)
        while True:
            print('Bookmarks ({})'.format(os.path.split(filename)[1]))
            list_bookm(db)
            choice = Cmd.get_menu_option(menu, 'aelrq', 'l' if len(db) else 'a')
            opt_to_func[choice.lower()](db)
    finally:
        if db:
            db.close()


if __name__ == '__main__':
    main()
