import os
from lark import Lark, Transformer, v_args


class Instruction:
    def __init__(self, lineno, itype):
        self.lineno = lineno
        self.itype = itype

    def __repr__(self):
        return str(self.__dict__)


class Label(Instruction):
    def __init__(self, lineno, name):
        super().__init__(lineno, 'label')
        self.name = name


class AInstruction(Instruction):
    def __init__(self, lineno, address):
        super().__init__(lineno, 'A')
        self.address = address


class CInstruction(Instruction):
    def __init__(self, lineno, dest, comp, jmp):
        super().__init__(lineno, 'C')
        self.dest = dest
        self.comp = comp
        self.jmp = jmp


class AstTransformer(Transformer):
    ops = dict(
        op_const = 'const',
        op_lone_register = 'val',
        op_negate = 'neg',
        op_not = '!',
        op_inc = 'inc',
        op_dec = 'dec',
        op_sum = '+',
        op_diff = '-',
        op_and = '&',
        op_or = '|'
    )

    def start(self, commands):
        return commands

    @v_args(inline=True)
    def label(self, name):
        return Label(name.line, str(name))

    @v_args(inline=True)
    def a_instruction(self, address):
        return AInstruction(address.line, str(address))

    @v_args(tree=True)
    def c_instruction(self, tree):
        if tree.children[0][0] == 'dest':
            dest = tree.children[0][1]
            comp = tree.children[1][1]
        else:
            dest = None
            comp = tree.children[0][1]

        if tree.children[-1][0] == 'jmp':
            jmp = tree.children[-1][1]
        else:
            jmp = None

        return CInstruction(tree.line, dest, comp, jmp)

    def dest(self, registers):
        return ('dest', ''.join(registers))

    def comp(self, op):
        return ('comp', *op)

    @v_args(inline=True)
    def jmp(self, value):
        return ('jmp', str(value))

    @v_args(inline=True)
    def op(self, op):
        return (self.ops[op.data], *[str(c) for c in op.children])

    @v_args(inline=True)
    def register(self, name):
        return str(name)


class Parser:
    def __init__(self):
        self._grammar = self._load_grammar()
        self._parser = Lark(self._grammar, propagate_positions=True)


    def parse(self, contents):
        tree = self._parser.parse(contents)
        return AstTransformer().transform(tree)


    def parse_file(self, path):
        with open(path) as f:
            return self.parse(f.read())


    def _load_grammar(self):
        grammar_path = os.path.join(os.path.dirname(__file__), "grammar.txt")
        with open(grammar_path) as f:
            return f.read()
