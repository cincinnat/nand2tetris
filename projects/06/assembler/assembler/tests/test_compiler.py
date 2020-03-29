from ..compiler import Compiler


class Instruction:
    def __init__(self, kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return str(self.__dict__)


def test_compiler():
    prog = [
        # 0
        Instruction({'itype': 'A', 'address': '2'}),
        # 1
        Instruction({'itype': 'C', 'dest': 'D', 'comp': ('val', 'A'), 'jmp': None}),
        # 2
        Instruction({'itype': 'A', 'address': '3'}),
        # 3
        Instruction({'itype': 'C', 'dest': 'D', 'comp': ('+', 'D', 'A'), 'jmp': None}),
        # 4
        Instruction({'itype': 'A', 'address': 'result'}),
        # 5
        Instruction({'itype': 'C', 'dest': 'M', 'comp': ('val', 'D'), 'jmp': None}),
        # -
        Instruction({'itype': 'label', 'name': 'END'}),
        # 6
        Instruction({'itype': 'A', 'address': 'END'}),
        # 7
        Instruction({'itype': 'C', 'dest': None, 'comp': ('const', '0'), 'jmp': 'JMP'}),
    ]

    c = Compiler()
    instructions = c.compile(prog)

    assert c._vars['END'] == 6
    assert c._vars['result'] == 16
    assert len(instructions) == 8

    print()
    for i, inst in enumerate(instructions):
        print(i, inst)
        assert inst[0] == str(i % 2)

