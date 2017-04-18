#!/usr/bin/python3
# regex parsing using finite state automata

import sys
import re
import collections


M3U_SONG = collections.namedtuple('M3U_song', 'title duration filename')
RE_INFO = re.compile(r'#EXTINF:(?P<duration>[-]?\w+)\s*,\s*(?P<title>.*)$')
NEED_INFO, NEED_FILENAME = range(2)


def parse_m3u(file):
    songs = []
    try:
        with open(file) as fh:
            if fh.readline().strip() != '#EXTM3U':
                print('Invalid m3u file.')
                sys.exit()
            state = NEED_INFO
            title = duration = ''
            for line_num, line in enumerate(fh, 2):
                line = line.strip()
                if not line:
                    continue
                if state == NEED_INFO:
                    info_match = RE_INFO.match(line)
                    if info_match:
                        title = info_match.group('title')
                        duration = info_match.group('duration')
                        state = NEED_FILENAME
                    else:
                        print('Error while parsing line {}:{}'.format(line_num, line))
                else:
                    songs.append(M3U_SONG(title, duration, line))
                    title = duration = ''
                    state = NEED_INFO
        return songs
    except (EnvironmentError, IOError) as file_err:
        print('Error processing file {}: {}'.format(file, file_err))
        sys.exit()


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2 or sys.argv[1] in {'-h', '--help'}:
        print('Usage: {} file.m3u')
        sys.exit()

    songs = parse_m3u(sys.argv[1])
    for song in songs:
        print(song)


if __name__ == '__main__':
    main()