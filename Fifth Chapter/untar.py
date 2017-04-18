#!/usr/bin/python3

import tarfile
import string
import sys


try:
    import bz2
    SUPPORTED_FILES = ('tar', 'tar.gz', 'tar.bz2')
except ImportError:
    SUPPORTED_FILES = ('tar', 'tar.gz')


UNTRUSTED_PREFIXES = tuple(["/", "\\"] +
                     [c + ":" for c in string.ascii_letters])


def main():
    if len(sys.argv) == 1 or sys.argv[1] in {'-h', '--help'}:
        print('usage: {} archive0 archive1 archiveN...'.format(sys.argv[0]))
        sys.exit()

    for file in sys.argv[1:]:
        if not file.endswith(SUPPORTED_FILES):
            print('Skipping {}...: unsupported file format'.format(file))
            continue
        untar(file)


def untar(archive):
    tar = None
    try:
        tar = tarfile.open(archive)
        for member in tar.getmembers():
            if member.name.startswith(UNTRUSTED_PREFIXES):
                print('untrusted prefix, exiting', member.name)
            elif '..' in member.name:
                print("suspect path, ignoring", member.name)
            else:
                tar.extract(member)
                print('unpacked', member.name)
    except (tarfile.TarError, EnvironmentError) as err:
        error(err)
    finally:
        if tar:
            tar.close()


def error(message, exit_status=1):
    print(message)
    sys.exit(exit_status)


main()


