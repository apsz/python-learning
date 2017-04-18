#!/usr/bin/python


import sys
import collections
from pyparsing import (Word, Suppress, restOfLine, Combine, LineEnd,
                       OneOrMore, Optional, nums, ParseException)


M3U_SONG = collections.namedtuple('M3U_song', 'title, duration, filename')


def pyparse_m3u(file):

    def add_song(tokens):
        new_song = M3U_SONG(tokens.title, tokens.seconds, tokens.filename)
        song_list.append(new_song)

    song_list = []
    title = restOfLine('title')
    filename = restOfLine('filename')
    seconds = Combine(Optional('-') + Word(nums)).setParseAction(
        lambda tokens: int(tokens[0]))('seconds')
    sec_title = Suppress('#EXTINF:') + seconds + Suppress(',') + title
    info = LineEnd() + sec_title + LineEnd() + filename
    info.addParseAction(add_song)
    parser = Suppress('#EXTM3U') + OneOrMore(info)

    try:
        parser.parseFile(file)
    except ParseException as parse_err:
        print('Parsing error: {}', parse_err)
        return []
    return song_list


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