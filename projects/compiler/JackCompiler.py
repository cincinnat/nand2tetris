#! /bin/env python3

import argparse
import glob
import os
import signal
import sys

from jack_compiler import Compiler


def main(args):
    c = Compiler()
    for path in args.input:
        if os.path.isdir(path):
            for fname in glob.iglob(os.path.join(path, '*.jack')):
                output_file = os.path.splitext(fname)[0] + '.vm'
                c.compile(fname, output_file)
        else:
            output_file = os.path.splitext(path)[0] + '.vm'
            c.compile(path, output_file)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='a jack compiler',
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
