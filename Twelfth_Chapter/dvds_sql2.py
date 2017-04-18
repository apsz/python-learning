#!/usr/bin/python3


import os
import sys
import sqlite3
import datetime
import xml.etree
from xml.etree.ElementTree import ElementTree, Element
from xml.parsers.expat import ExpatError
import Cmd


DISPLAY_LIMIT = 30


def quit(*ignore):
    sys.exit()


def connect(filename):
    first_time = os.path.exists(filename)
    db = sqlite3.connect(filename)
    if not first_time:
        cursor = db.cursor()
        cursor.execute('CREATE TABLE directors ('
                       'id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, '
                       'name TEXT UNIQUE NOT NULL)')
        cursor.execute('CREATE TABLE dvds ('
                       'id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL,'
                       'title TEXT NOT NULL,'
                       'year INTEGER NOT NULL,'
                       'duration INTEGER NOT NULL,'
                       'director_id INTEGER NOT NULL,'
                       'FOREIGN KEY (director_id) REFERENCES directors)')
        db.commit()
    return db


def add_dvd(db):
    title = Cmd.get_string('Title', 'title')
    if not title:
        return
    director = Cmd.get_string('Director', 'director')
    if not director:
        return
    director_id = get_set_director(db, director)
    year = Cmd.get_int('Year', 'year', min_val=1896,
                        max_val=datetime.date.today().year)
    duration = Cmd.get_int('Duration', 'duration',
                            min_val=0, max_val=60*48)
    cursor = db.cursor()
    cursor.execute('INSERT INTO dvds (title, year, duration, director_id) '
                   'VALUES (?, ?, ?, ?)', (title, year, duration, director_id))
    db.commit()

def get_set_director(db, name):
    director_id = find_director(db, name)
    if director_id:
        return director_id
    cursor = db.cursor()
    cursor.execute('INSERT INTO directors (name) '
                   'VALUES (?)', (name,))
    db.commit()
    return find_director(db, name)


def find_director(db, name):
    cursor = db.cursor()
    cursor.execute('SELECT id '
                   'FROM directors '
                   'WHERE name=?', (name,))
    result = cursor.fetchone()
    return result[0] if result else None


def edit_dvd(db):
    title, dvd_id = find_dvd(db, 'edit')
    if not title:
        return
    cursor = db.cursor()
    cursor.execute('SELECT dvds.year, dvds.duration, directors.name '
                   'FROM dvds, directors '
                   'WHERE dvds.director_id = directors.id AND '
                   'dvds.id=:id', dict(id=dvd_id))
    year, duration, directors_name = cursor.fetchone()
    director = Cmd.get_string('Director', 'director', directors_name)
    if not director:
        return
    director_id = get_set_director(db, directors_name)
    year = Cmd.get_int('Year', 'year', default=year, min_val=1896,
                        max_val=datetime.date.today().year, empty_ok=True)
    duration = Cmd.get_int('Duration', 'duration', default=duration,
                            min_val=0, max_val=60*48, empty_ok=True)
    cursor.execute('UPDATE dvds SET title=:title, year=:year, '
                   'duration=:duration, director_id=:director_id '
                   'WHERE id=:dvd_id', (locals()))
    db.commit()


def remove_dvd(db):
    title, dvd_id = find_dvd(db, 'remove')
    if not title:
        return
    confirm = Cmd.get_bool('Remove {}?'.format(title), 'no')
    if confirm:
        cursor = db.cursor()
        cursor.execute('DELETE FROM dvds '
                       'WHERE id=?', (dvd_id,))
        db.commit()


def list_directors(db):
    cursor = db.cursor()
    sql =('SELECT directors.name from directors, dvds '
          'WHERE directors.id = dvds.director_id')
    start = None
    if directors_count(db) > DISPLAY_LIMIT:
        start = Cmd.get_string("List those starting with "
                               "[Enter=all]", "start")
        sql += ' AND directors.name LIKE ?'
    sql += ' ORDER BY directors.name'
    print()
    if start is None:
        cursor.execute(sql)
    else:
        cursor.execute(sql, (start + '%'))
    directors_list = cursor.fetchall()
    for index, name in enumerate(directors_list, 1):
        print('{}: {}'.format(index, name[0]))


def list_dvds(db):
    cursor = db.cursor()
    sql = ('SELECT dvds.title, dvds.year, dvds.duration, '
           'directors.name '
           'FROM dvds, directors '
           'WHERE dvds.director_id = directors.id')
    start = None
    if dvd_count(db) > DISPLAY_LIMIT:
        start = Cmd.get_string('List those starting with '
                               '[Enter=all]', 'start')
        sql += ' AND dvds.title LIKE ?'
    sql += ' ORDER BY dvds.title'
    print()
    if start is None:
        cursor.execute(sql)
    else:
        cursor.execute(sql, (start + '%'))
    dvds_list = cursor.fetchall()
    for dvd in dvds_list:
        print('Title: {0[0]} | Director: {0[3]} |'
              ' Year: {0[1]} | Duration: {0[2]}'.format(dvd))


def dvd_count(db):
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM dvds')
    return cursor.fetchone()[0]


def directors_count(db):
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM directors')
    return cursor.fetchone()[0]


def find_dvd(db, action):
    msg = '(Start of) title to {}'.format(action)
    while True:
        usr_title = Cmd.get_string(msg, 'title', empty_ok=True)
        if not usr_title:
            return (None, None)
        cursor = db.cursor()
        cursor.execute('SELECT title, id '
                       'FROM dvds '
                       'WHERE title LIKE ? '
                       'ORDER BY title', (usr_title + '%',))
        matches = cursor.fetchall()
        if not matches:
            print('No matches found. Try using different characters.')
            continue
        elif len(matches) == 1:
            return matches[0]
        elif len(matches) > DISPLAY_LIMIT:
            print('Too many matches found. Please try to be more specific.')
            continue
        else:
            for index, matched_title in enumerate(matches, 1):
                print('{}: {}'.format(index, matched_title[0]))
            chosen_title = Cmd.get_int('Index (0 to cancel)',
                                        'index', min_val=1,
                                        max_val=len(matches), empty_ok=True)
            return matches[chosen_title-1] if chosen_title else (None, None)


def export_xml(db):
    filename = os.path.join(os.path.dirname(__file__), 'test2_db.xml')

    root = xml.etree.ElementTree.Element('dvds')
    cursor = db.cursor()
    cursor.execute('SELECT dvds.title, dvds.year, dvds.duration, '
                   'directors.name '
                   'FROM dvds, directors '
                   'WHERE dvds.director_id = directors.id '
                   'ORDER BY dvds.title')
    dvds_list = cursor.fetchall()
    for dvd in dvds_list:
        dvd_element = xml.etree.ElementTree.Element('dvd',
                                                    title=dvd[0],
                                                    year=str(dvd[1]),
                                                    duration=str(dvd[2]),
                                                    director=dvd[3])
        root.append(dvd_element)
    tree = xml.etree.ElementTree.ElementTree(root)
    try:
        tree.write(filename, 'UTF-8')
        print('Xml exported.')
        return True
    except (EnvironmentError, IOError, ExpatError) as xml_exp_err:
        print('Error: ', xml_exp_err)
        return False


def import_xml(db):
    filename = os.path.join(os.path.dirname(__file__), 'test2_db.xml')
    try:
        data = xml.etree.ElementTree.parse(filename)
    except (EnvironmentError, IOError, ExpatError) as xml_imp_err:
        print('Error: ', xml_imp_err)
        return False

    cursor = db.cursor()
    cursor.execute('DELETE FROM directors')
    cursor.execute('DELETE FROM dvds')

    imported_dvds = data.findall('dvd')
    for dvd in imported_dvds:
        try:
            title = dvd.get('title')
            year = int(dvd.get('year'))
            duration = int(dvd.get('duration'))
            director_id = get_set_director(db, dvd.get('director'))
            cursor.execute('INSERT INTO dvds '
                           '(title, year, duration, director_id) '
                           'VALUES (?, ?, ?, ?)', (title, year,
                                                   duration, director_id))
        except (ValueError, sqlite3.Error) as data_err:
            print('Error: ', data_err)
            db.rollback()
            break
    else:
        print('Import successful.')
        db.commit()


def main():
    filename = os.path.join(os.path.dirname(__file__), 'test2_db_sql')
    menu = ('(A)dd  (E)dit  (R)emove  (L)ist  List (D)irectors  '
            'E(X)port  (I)mport  (Q)uit: ')
    input_to_func = dict(a=add_dvd, e=edit_dvd, r=remove_dvd, l=list_dvds,
                         d=list_directors, x=export_xml, i=import_xml, q=quit)
    valid = frozenset('aerldxiq')

    db = None
    try:
        db = connect(filename)
        while True:
            user_choice = Cmd.get_menu_option(menu, valid)
            input_to_func[user_choice.lower()](db)
    except (EnvironmentError, IOError) as file_err:
        print('File Error: ', file_err)
        sys.exit()
    except sqlite3.Error as db_err:
        print('Database Error: ', db_err)
        sys.exit()
    finally:
        if db:
            db.close()


if __name__ == '__main__':
    main()
