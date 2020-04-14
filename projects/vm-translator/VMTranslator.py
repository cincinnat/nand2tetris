#! /bin/env python3

import argparse
import signal
import sys

from translator import Translator


def main(args):
    t = Translator()
    t.translate(args.input, dry_run=args.dry_run)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='a Hack assembler',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input', help='input files or directory')
    parser.add_argument('--dry-run', '-d', action='store_true',
        help='do not create the output file.')

    parsed_args = parser.parse_args()

    try:
        main(parsed_args)
    except BrokenPipeError:
        sys.exit(128 + signal.SIGPIPE)
    except KeyboardInterrupt:
        sys.exit(128 + signal.SIGINT)
