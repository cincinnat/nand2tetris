#! /bin/env python3

import argparse
import os
import signal
import sys

import assembler as asm


def complice_prog(source, target):
    p = asm.parser.Parser()
    prog = p.parse_file(source)

    c = asm.compiler.Compiler()
    c.compile(prog, output=target)


def main(args):
    for source in args.input:
        name, _ = os.path.splitext(source)
        target = name + '.hack'
        complice_prog(source, target)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='a Hack assembler',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input', nargs='+', help='input files')

    parsed_args = parser.parse_args()

    try:
        main(parsed_args)
    except BrokenPipeError:
        sys.exit(128 + signal.SIGPIPE)
    except KeyboardInterrupt:
        sys.exit(128 + signal.SIGINT)
