#!/usr/bin/python3


import optparse


def main():
    parser = optparse.OptionParser()
    parser.add_option('-w', '--maxwidth', dest='maxwidth', default=80, type=int, help=('Help for maxwidth'))
    parser.add_option('-o', '--optimize', dest='optimize', default='-CC', type=str, help=('Help for optimize'))
    opts, args = parser.parse_args()
    print(opts.maxwidth)
    print()

main()


