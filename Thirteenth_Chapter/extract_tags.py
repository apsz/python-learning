#!/usr/bin/python3


import re
import sys


def main():
    if not len(sys.argv) > 1 or sys.argv[1] in {'-h', '--help'}:
        print('Usage: {} .xml/.html file1 [.xml/.html file2]...')
        sys.exit()

    re_tag_attr = re.compile(r'(?:<(?P<tag>\w+)\s+(?<!<))*'
                             r'(?P<attr>\b\w+)[\s+]*?(?==)')
    re_val = re.compile(r'=(?:[\s+]*)([\'\"])(.*?)(?=\1)'
                        r'|=(?:[\s+]*)([^\W\'\"].[^\s>]*)',
                        flags=re.DOTALL)
    for file in sys.argv[1:]:
        try:
            with open(file) as fh:
                text = fh.read()
                val_matches = re_val.findall(text)
                val_count = 0
                for match in re_tag_attr.finditer(text):
                    if match.group('tag'):
                        print(match.group('tag'))
                    if match.group('attr'):
                        print('  {}: {}'.format(match.group('attr'),
                                                val_matches[val_count][1]))
                        val_count += 1
        except (EnvironmentError, IOError) as file_err:
            print('Error processing {}: {}'.format(file, file_err))
            continue


if __name__ == '__main__':
    main()