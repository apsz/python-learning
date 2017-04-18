#!/usr/bin/python3

import sys

BLOCK_SIZE = 8000
process_id = '{}: '.format(sys.argv[1]) if len(sys.argv) == 2 else ''
sys.stdin = sys.stdin.detach()
stdin = sys.stdin.read()
decoded_lines = stdin.decode('utf8', 'ignore').splitlines()
target_word = decoded_lines[0].rstrip()

for file in decoded_lines[1:]:
    filename = file.rstrip()
    previous = ''

    try:
        with open(filename, 'rb') as fh:
            while True:
                block = fh.read(BLOCK_SIZE)
                if not block:
                    break
                block_decoded = block.decode('utf8', 'ignore')
                if (target_word in block_decoded or
                        target_word in previous[-len(target_word):] +
                        block_decoded[:len(target_word)]):
                    print('{}{}'.format(process_id, filename))
                    break
                if len(block_decoded) != BLOCK_SIZE:
                    break
                previous = block_decoded
    except (EnvironmentError, IOError) as e_rr:
        print('Error {}. Skipping {}...'.format(e_rr, filename))



