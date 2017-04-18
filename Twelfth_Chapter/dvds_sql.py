#!/usr/bin/python3


import os
import sys
import sqlite3
import datetime
from xml.etree import ElementTree
from xml.etree.ElementTree import SubElement
from xml.parsers import expat
import Cmd


DISPLAY_MAX = 10


def quit(*ignore):
    sys.exit()


def connect(filename):
    create = os.path.exists(filename)
    db = sqlite3.connect(filename)
    if not create:
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
    cursor.execute('INSERT INTO dvds (title, year, duration, director_id)'
                   'VALUES (?, ?, ?, ?)', (title, year, duration, director_id))
    db.commit()


def get_set_director(db, director):
    director_id = get_director_id(db, director)
    if director_id:
        return director_id
    cursor = db.cursor()
    cursor.execute('INSERT INTO directors (name) VALUES (?)',
                   (director,))
    db.commit()
    return get_director_id(db, director)


def get_director_id(db, director):
    cursor = db.cursor()
    cursor.execute('SELECT id FROM directors WHERE name=?',
                   (director,))
    fields = cursor.fetchone()
    return fields[0] if fields is not None else None


def edit_dvd(db):
    title, identity = find_dvd(db, 'edit')
    if not title:
        return
    title = Cmd.get_string('Title', 'title', default=title)
    if not title:
        return
    cursor = db.cursor()
    cursor.execute('SELECT dvds.year, dvds.duration, directors.name '
                   'FROM dvds, directors '
                   'WHERE dvds.director_id = directors.id AND ' 
                   'dvds.id=:id', dict(id=identity))
    year, duration, director = cursor.fetchone()
    year = Cmd.get_int('Year', 'year', default=year, min_val=1896,
                       max_val=datetime.date.today().year, empty_ok=True)
    duration = Cmd.get_int('Duration', 'duration', default=duration,
                           min_val=0, max_val=60*48, empty_ok=True)
    director_id = get_set_director(db, director)
    cursor.execute('UPDATE dvds SET title=:title, year=:year, '
                   'duration=:duration, director_id=:director_id '
                   'WHERE id=:identity', locals())
    db.commit()


def remove_dvd(db):
    title, identity = find_dvd(db, 'remove')
    if not title:
        return
    confirm = Cmd.get_bool("Remove {0}?".format(title), "no")
    if confirm:
        cursor = db.cursor()
        cursor.execute("DELETE FROM dvds WHERE id=?", (identity,))
        db.commit()


def list_dvds(db):
    cursor = db.cursor()
    sql = ("SELECT dvds.title, dvds.year, dvds.duration, "
           "directors.name FROM dvds, directors "
           "WHERE dvds.director_id = directors.id")
    start = None
    if dvd_count(db) > DISPLAY_MAX:
        start = Cmd.get_string("List those starting with "
                               "[Enter=all]", "start")
        sql += " AND dvds.title LIKE ?"
    sql += " ORDER BY dvds.title"
    print()
    if start is None:
        cursor.execute(sql)
    else:
        cursor.execute(sql, (start + "%",))
    for record in cursor:
        print("{0[0]} ({0[1]}) {0[2]} minutes, by {0[3]}".format(
            record))


def list_directors(db):
    cursor = db.cursor()
    sql = ("SELECT directors.name "
           "FROM directors, dvds "
           "WHERE dvds.director_id = directors.id")
    start = None
    if dvd_count(db) > DISPLAY_MAX:
        start = Cmd.get_string("List those starting with "
                               "[Enter=all]", "start")
        sql += " AND directors.name LIKE ?"
    sql += " ORDER BY directors.name"
    print()
    if start is None:
        cursor.execute(sql)
    else:
        cursor.execute(sql, (start + "%",))
    for director in cursor:
        print('{}'.format(director[0]))


def dvd_count(db):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM dvds")
    return cursor.fetchone()[0]


def find_dvd(db, action):
    msg = '(Start of) title to {}'.format(action)
    cursor = db.cursor()
    while True:
        title = Cmd.get_string(msg, 'title', empty_ok=True)
        if not title:
            return (None, None)
        cursor.execute('SELECT title, id FROM dvds '
                       'WHERE title LIKE ? ORDER BY title',
                       (title + "%",))
        matches = cursor.fetchall()
        if len(matches) == 0:
            print('No matches. Try using different characters')
            continue
        elif len(matches) == 1:
            return matches[0]
        elif len(matches) > DISPLAY_MAX:
            print('Too many values to display.'
                  'Please narrow your search.')
            continue
        else:
            for enum, matched_title in enumerate(matches, 1):
                print('{}: {}'.format(enum, matched_title[0]))
            title_choice = Cmd.get_int('Number (or 0 to cancel)',
                                           min_val=1, max_val=len(matches), empty_ok=True)
            return matches[title_choice-1] if title_choice else (None, None)


def export_xml(db):
    pass


def import_xml(db):
    pass


def main():
    filename = os.path.join(os.path.dirname(__file__), 'dvds_sql_db')
    menu = '(A)dd  (E)dit  (R)emove  (L)ist  List (D)irectors  E(X)port  (I)mport  (Q)uit: '
    input_to_func = dict(a=add_dvd, e=edit_dvd, r=remove_dvd, l=list_dvds,
                         d=list_directors, x=export_xml, i=import_xml, q=quit)
    valid = frozenset('aerldxiq')

    db = None
    try:
        db = connect(filename)
        while True:
            chosen_opt = Cmd.get_menu_option(menu, valid)
            input_to_func[chosen_opt.lower()](db)
    except (EnvironmentError, IOError, sqlite3.Error) as process_err:
        print('Error: ', process_err)
        sys.exit()
    finally:
        if db:
            db.close()


if __name__ == '__main__':
    main()