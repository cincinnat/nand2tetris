#! /bin/env python3

import argparse
import os
import signal
import sys

import assembler as asm


def complice_prog(source, target, args):
    p = asm.parser.Parser()
    prog = p.parse_file(source, print_tree=args.print_tree)

    c = asm.compiler.Compiler()
    output = target if not args.dry_run else None
    c.compile(prog, output=output)


def main(args):
    for source in args.input:
        name, _ = os.path.splitext(source)
        target = name + '.hack'
        complice_prog(source, target, args)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='a Hack assembler',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('input', nargs='+', help='input files')
    parser.add_argument('--print-tree', '-t', action='store_true',
        help='print out the AST tree')
    parser.add_argument('--dry-run', '-d', action='store_true',
        help='do not creat the output file.')

    parsed_args = parser.parse_args()

    try:
        main(parsed_args)
    except BrokenPipeError:
        sys.exit(128 + signal.SIGPIPE)
    except KeyboardInterrupt:
        sys.exit(128 + signal.SIGINT)
