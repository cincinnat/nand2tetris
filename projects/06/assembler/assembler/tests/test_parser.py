from ..parser import Parser


def test_parse():
    p = Parser()
    instructions = p.parse('''
        // comment
        @2  // other comment
        D=A
        @3
        D=D+A
        @0
        M=D

        (END)
        @END
        0;JMP
    ''')

    assert len(instructions) == 9
