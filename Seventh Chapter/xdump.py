#!/usr/bin/python3

import sys
import optparse


def main():
    opts, args = get_opts_args()
    for file in args:
        fh = None
        block_count = 0
        try:
            fh = open(file, 'r+b')
            print_format = '{0:<8} {1:{5}<{2}} {3:{4}^{2}}'
            print('Attempting to read binary file {}...'.format(file))
            print(print_format.format('Block', 'Bytes', (opts.blocksize*2)+3,
                                                        opts.encoding + ' characters', '', ''))
            print(print_format.format('-'*8, '-'*((opts.blocksize*2)+3),
                                      (opts.blocksize * 2) + 3, '-'*((opts.blocksize*2)+3), '', ''))
            while True:
                text = ''
                record = fh.read(opts.blocksize)
                if not record:
                    break
                block = '{:0>8}'.format(block_count if opts.decimal
                                          else hex(block_count))
                for count, c in enumerate(record, 1):
                    text += '{} '.format(hex(c)) if not (count % 4) else hex(c)
                if text:
                    text = '0' + text.replace('0x', '')
                decoded_text = record.decode(opts.encoding)
                decoded_text = ''.join([c if c.isalnum() or c.isspace()
                                        else '.' for c in decoded_text])
                print(print_format.format(block, text, (opts.blocksize*2)+3, decoded_text, ' ', ' '))
                block_count += 1
        except (EnvironmentError, IOError) as f_err:
            print('{} error while accessing the file: {}\n'
                  ', moving on...'.format(file, f_err))
            continue
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