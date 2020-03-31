#! /bin/env python3

import argparse
import os
import signal
import sys

from parser import Parser
from code_generator import CodeGenerator


def translate(source, target, args):
    p = Parser()
    commands = p.parse_file(source)

    t = CodeGenerator()
    output = target if not args.dry_run else None
    t.translate(commands, output=output, dry_run=args.dry_run)


def main(args):
    for source in args.input:
        name, _ = os.path.splitext(source)
        target = name + '.asm'
        translate(source, target, args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='a Hack assembler',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input', nargs='+', help='input files')
    parser.add_argument('--dry-run', '-d', action='store_true',
        help='do not create the output file.')

    parsed_args = parser.parse_args()

    try:
        main(parsed_args)
    except BrokenPipeError:
        sys.exit(128 + signal.SIGPIPE)
    except KeyboardInterrupt:
        sys.exit(128 + signal.SIGINT)
