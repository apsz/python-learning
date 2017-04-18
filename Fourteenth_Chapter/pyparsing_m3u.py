#!/usr/bin/python


import sys
import collections
from pyparsing import (Word, Suppress, restOfLine, Combine,
                       OneOrMore, Optional, alphanums, ParseException)


M3U_SONG = collections.namedtuple('M3U_song', 'title, duration, filename')


def pyparse_m3u(file):

    def add_song(tokens):
        print(tokens)
        duration, title = tokens[0].split(',')
        new_song = M3U_SONG(title, duration, tokens[1])
        songs_list.append(new_song)


    songs_list = []
    header = '#EXTM3U'
    filename = Combine(Word(alphanums, '\\') + restOfLine)
    time_title = Suppress('#EXTINF:') + restOfLine
    info = time_title + filename
    info.addParseAction(add_song)
    parser = Optional(header) + OneOrMore(info)

    try:
        parser.parseFile(file)
    except ParseException as parse_err:
        print('Parsing error: {}', parse_err)
        return []
    return songs_list


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2 \
            or sys.argv[1] in {'-h', '--help'}:
        print('Usage: {} <filename>.pls'.format(sys.argv[0]))
        sys.exit()

    parsed_songs = pyparse_m3u(sys.argv[1])
    for song in parsed_songs:
        print('title: {0.title}\nduration: {0.duration}\n'
              'filename: {0.filename}\n'.format(song))


if __name__ == '__main__':
    main()