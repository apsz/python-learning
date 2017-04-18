#!/usr/bin/python3


import sys


BLOCK_SIZE = 8000
process_id = '{}: '.format(sys.argv[1]) if len(sys.argv) == 2 else ''
sys.stdin = sys.stdin.detach()
stdin = sys.stdin.read()
lines = stdin.decode('utf8', 'ignore').splitlines()
word = lines[0].rstrip()

for file in lines[1:]:
    file = file.rstrip()
    previous = ''

    try:
        with open(file, 'rb') as fh:
            while True:
                block = fh.read(BLOCK_SIZE)
                if not block:
                    break
                block_decoded = block.decode('utf8', 'ignore')
                if (word in block_decoded or
                    word in previous[-len(word):] +
                    block_decoded[:len(word)]):
                    print('{}{}'.format(process_id, file))
                    break
                if len(block_decoded) != BLOCK_SIZE:
                    break
                previous = block_decoded
    except (EnvironmentError, IOError) as file_err:
        print('{}{}{}\n\tSkipping...'.format(process_id, file, file_err))