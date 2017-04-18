#!/usr/bin/python3


import sys


def main():
    if len(sys.argv) < 1 or sys.argv[1] in {'--help', '-h'}:
        print('usage: {} file1 file2 fileN...')
        sys.exit()

    for file in sys.argv[1:]:
        lines = []
        fh = None
        try:
            for line in open(file):
                if line.strip():
                    lines.append(line)
            if lines:
                filename = file.split('.')[0] + '.nb'
                fh = open(filename, 'w')
                for line in lines:
                    fh.write(line)
        except EnvironmentError as env_err:
            print('file {} could not be opened: {}'.format(file, env_err))
            continue
        finally:
            if fh:
                fh.close()


main()