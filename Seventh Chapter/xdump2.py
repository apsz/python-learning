#!/usr/bin/python3

import sys
import optparse


def main():
    opts, args = get_opts_args()
    for file in args:
        fh = None
        try:
            fh = open(file, 'r+b')
            lines = []
            mx = 0
            block_count = 0
            size = opts.blocksize
            chars_header = '{} {}'.format(opts.encoding.upper(), 'characters')
            print('\nAttempting to read binary file {}...'.format(file))
            while True:
                length = 0
                record = fh.read(opts.blocksize)
                if not record:
                    break
                decoded = record.decode(opts.encoding)
                text = ''
                for count, c in enumerate(decoded, 1):
                    hexed = hex(ord(c))
                    text += '0' + hexed.lstrip('0x') if hexed in ('0x1', '0x2') \
                        else hexed.lstrip('0x')
                    if count % 4 == 0:
                        text += ' '
                        length += 1
                block = block_count if opts.decimal else hex(block_count)
                decoded_ascii = ''.join([c if (32 <= ord(c) < 127) else '.' for c in decoded])
                lines.append((block, text.upper(), decoded_ascii))
                mx = len(text) if len(text) > mx else mx
                block_count += 1
            max_decoded = max([len(l[2]) for l in lines])
            print('{0:<8}  {1:<{3}.{3}}  {2:<{4}}'.format('Block', 'Bytes', chars_header,
                                                          mx, size))
            print('{0:-<8}  {0:-<{1}.{1}}  {0:-<{2}}'.format('-', mx, max_decoded if
                            max_decoded > len(chars_header) else len(chars_header)))
            for line in lines:
                print('{0:0>8}  {1:<{3}.{3}}  {2:<{4}}'.format(line[0], line[1],
                                                               line[2], mx, size))
        except (IOError, EnvironmentError) as fl_err:
            print('{} error: {}. Moving on...'.format(file, fl_err))
            break
        finally:
            if fh:
                fh.close()


def get_opts_args():
    parser = optparse.OptionParser()
    parser.set_usage('Usage: {} [options] [file1 [file2 [... fileN]]]\n'
                     'At least one file required.'.format(sys.argv[0]))
    parser.add_option('-b', '--blocksize', dest='blocksize', default=16,
                      type=int,
                      help=('block size (8..80) [default: 16]'))
    parser.add_option('-d', '--decimal', dest='decimal', default=False,
                      action='store_true',
                      help=('decimal block numbers [default: hexadecimal]'))
    parser.add_option('-e', '--encoding', dest='encoding', default='UTF-8',
                      type=str,
                      help=('encoding (ASCII..UTF-32) [default: UTF-8]'))
    opts, args = parser.parse_args()
    if not len(args):
        parser.print_help()
        sys.exit()
    if opts.blocksize and not (8 <= opts.blocksize <= 80):
        print('blocksize must be between 8 and 80 bytes.')
        sys.exit()
    return parser.parse_args()


main()
