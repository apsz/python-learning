#!/usr/bin/python3


import os
import sys
import datetime
import pickle
import shelve
import xml
from xml.etree import ElementTree
from xml.etree.ElementTree import SubElement
from xml.parsers import expat
import Cmd


DISPLAY_LIMIT = 10
DIRECTOR, YEAR, DURATION = range(3)


def add_dvd(db):
    title = Cmd.get_string('Title', 'title')
    if not title:
        return
    director = Cmd.get_string('Director', 'director')
    if not title:
        return
    year = Cmd.get_int('Year', 'year', min_val=1896,
                       max_val=datetime.date.today().year)
    duration = Cmd.get_int('Duration', 'duration',
                           min_val=0, max_val=60*48)
    db[title] = (director, year, duration)
    db.sync()


def edit_dvd(db):
    old_title = find_dvd(db, 'edit')
    if not old_title:
        return
    title = Cmd.get_string('Title', 'title', default=old_title)
    if not title:
        return
    director, year, duration = db[title]
    director = Cmd.get_string('Director', 'director', default=director)
    year = Cmd.get_int('Year', 'year', default=year, min_val=1896,
                       max_val=datetime.date.today().year, empty_ok=True)
    duration = Cmd.get_int('Duration', 'duration', default=duration,
                           min_val=0, max_val=60*48, empty_ok=True)
    db[title] = (director, year, duration)
    if old_title != title:
        del db[old_title]
    db.sync()


def remove_dvd(db):
    title = find_dvd(db, 'remove')
    if not title:
        return
    confirmation = Cmd.get_bool('Remove {}? '.format(title), 'no')
    if confirmation:
        del db[title]
        db.sync()


def list_dvds(db):
    start_str = ''
    if len(db) > DISPLAY_LIMIT:
        start_str = Cmd.get_string('List titles starting with'
                                   ' [Enter=all]', 'title')
    for title in db.keys():
        if not start_str or title.lower().startswith(start_str.lower()):
            director, year, duration = db[title]
            print('Title: {title} | Director: {director} |'
                  ' Year: {year} | Duration: {duration}'.format(**locals()))


def find_dvd(db, action):
    msg = '(Start of) title to {}'.format(action)
    while True:
        matches = []
        start_str = Cmd.get_string(msg, 'title', empty_ok=True)
        if not start_str:
            return
        for title in db.keys():
            if title.lower().startswith(start_str.lower()):
                matches.append(title)
        if not matches:
            print('No matching titles found.\n'
                  'Try adding some characters.')
            continue
        elif len(matches) == 1:
            return matches[0]
        elif len(matches) > DISPLAY_LIMIT:
            print('Too many dvd start with {}.'
                  'Try adding some characters.'.format(start_str))
            continue
        else:
            for id, matched_title in enumerate(matches, 1):
                print('{}: {}'.format(id, matched_title))
            title_choice = Cmd.get_int('Number (or 0 to cancel)', 'number',
                                           min_val=1, max_val=len(matches), empty_ok=True)
            return matches[title_choice - 1] if title_choice else ''


def export_xml(db):
    filename = os.path.join(os.path.dirname(__file__), 'backup.xml')

    root = xml.etree.ElementTree.Element('dvds')
    for title in db.keys():
        dvd = xml.etree.ElementTree.Element('dvd',
                                            title=title,
                                            director=db[title][DIRECTOR],
                                            year=str(db[title][YEAR]),
                                            duration=str(db[title][DURATION]))
        root.append(dvd)
    tree = xml.etree.ElementTree.ElementTree(root)
    try:
        tree.write(filename, 'UTF-8')
        print('XML exported.')
        return True
    except (EnvironmentError, IOError, xml.parsers.expat.ExpatError) \
            as save_err:
        print('Error while exporting to xml: {}'.format(save_err))
        return False


def import_xml(db):
    filename = os.path.join(os.path.dirname(__file__), 'backup.xml')

    try:
        tree = xml.etree.ElementTree.parse(filename)
    except (EnvironmentError, IOError, xml.parsers.expat.ExpatError) \
            as load_err:
        print('Error while loading xml: {}'.format(load_err))
        return False

    db.clear()
    for dvd in tree.findall('dvd'):
        try:
            imported_dvd = {}
            imported_dvd[dvd.get('title')] = (
                dvd.get('director'),
                int(dvd.get('year')),
                int(dvd.get('duration')))
            db.update(imported_dvd)
        except (LookupError, KeyError) as data_err:
            print('{} corrupted data: {}'.format(filename, data_err))
            return False
    return True


def quit(*ignore):
    sys.exit()


def main():
    filename = os.path.join(os.path.dirname(__file__), 'test.db')
    menu = '(A)dd  (E)dit  (R)emove  (L)ist  E(X)port  (I)mport  (Q)uit: '
    input_to_func = dict(a=add_dvd, e=edit_dvd, r=remove_dvd, l=list_dvds,
                         x=export_xml, i=import_xml, q=quit)
    valid = frozenset('aerlxiq')

    db = None
    try:
        db = shelve.open(filename, protocol=pickle.HIGHEST_PROTOCOL)
        while True:
            menu_choice = Cmd.get_menu_option(menu, valid)
            input_to_func[menu_choice.lower()](db)
    except (EnvironmentError, pickle.PickleError) as file_err:
        print('Error: {}'.format(file_err))
    finally:
        if db:
            db.close()


if __name__ == '__main__':
    main()
