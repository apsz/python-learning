#!/usr/bin/python3
# regex parsing

import sys
import re


RE_HEADER = re.compile(r'[.[^]]*]')
RE_KEY_VALUE = re.compile(r'(?P<key>\w+)\s*=\s*(?P<value>\w+)$')


def parse_pls(file, lowercase_keys=False):
    pls_dict = {}
    try:
        with open(file) as fh:
            for line_num, line in enumerate(fh, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                key_val_match = RE_KEY_VALUE.match(line)
                if key_val_match:
                    key = key_val_match.group('key')
                    if lowercase_keys:
                        key = key.lower()
                    pls_dict[key] = key_val_match.group('value')
                else:
                    if RE_HEADER.match(line):
                        continue
                    print('Error while parsing line {}: {}'.format(line_num, line))
    except (EnvironmentError, IOError) as file_err:
        print('Error while processing {}: {}'.format(file, file_err))
        sys.exit()