#!/usr/bin/python3


import sys
import collections
import ply.lex


M3U_SONG = collections.namedtuple('Song', 'title duration filename')


def get_file_handle(filename):
    try:
        return open(filename)
    except (EnvironmentError, IOError) as file_err:
        print('Error opening {}: {}'.format(filename, file_err))
        sys.exit()



def parse_m3u_ply(fh):

    tokens = ['M3U', 'INFO', 'SECONDS', 'TITLE', 'FILENAME']
    states = [('info', 'exclusive'), ('filename', 'exclusive')]

    t_M3U = r'\#EXTM3U'
    t_ANY_ignore = '\t\n'

    def t_INFO(t):
        r'\#EXTINF:'
        t.lexer.begin('info')
        return None

    def t_info_SECONDS(t):
        r'-?\d+,'
        t.value = int(t.value[:-1])
        return t

    def t_info_TITLE(t):
        r'[^\n]+'
        t.lexer.begin('filename')
        return t

    def t_filename_FILENAME(t):
        r'[^\n]+'
        t.lexer.begin('INITIAL')
        return t

    def t_ANY_newline(t):
        r'\n'
        t.lexer.lineno += len(t.value)

    def t_ANY_error(t):
        line = t.value.lstrip()
        new_line_index = line.find('\n')
        line = line[:new_line_index] if new_line_index != -1 else line
        print('Failed to parse line {}: {}'.format(t.lineno + 1, line))

    lexer = ply.lex.lex()
    lexer.input(fh.read())

    songs = []
    seconds = title = None
    for token in lexer:
        if token.type == 'SECONDS':
            seconds = token.value
        elif token.type == 'TITLE':
            title = token.value
        elif token.type == 'FILENAME':
            if seconds is None or title is None:
                print('Cannot parse {}: no previous title/duration'.format(
                    token.value))
            else:
                songs.append(M3U_SONG(title, seconds, token.value))
                seconds = title = None
    return songs


def main():
    if len(sys.argv) == 1 or len(sys.argv) > 2 or \
                    sys.argv[1] in {'-h', '--help'}:
        print('Usage: {} <file>.pls'.format(sys.argv[0]))
        sys.exit()

    fh = get_file_handle(sys.argv[1])
    songs_list = parse_m3u_ply(fh)
    for song in songs_list:
        print(song)


if __name__ == '__main__':
    main()