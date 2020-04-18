#! /bin/env python3

import argparse
import glob
import os
import signal
import sys

from jack_parser import Parser


def main(args):
    p = Parser()
    for path in args.input:
        if os.path.isdir(path):
            for fname in glob.iglob(os.path.join(path, '*.jack')):
                p.parse(fname)
        else:
            p.parse(path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='a jack language parser',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input', nargs='+',
        help='input .jack files or directories containing .jack files')

    parsed_args = parser.parse_args()

    try:
        main(parsed_args)
    except BrokenPipeError:
        sys.exit(128 + signal.SIGPIPE)
    except KeyboardInterrupt:
        sys.exit(128 + signal.SIGINT)
