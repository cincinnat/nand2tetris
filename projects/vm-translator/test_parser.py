from parser import Parser


def test_parser():
    p = Parser()
    commands = p.parse('''
        // comment

        push constant 7  //comment
        push constant 8
        add
    ''')
    commands = list(commands)

    assert len(commands) == 3
    assert commands[1] == [4, 'push', 'constant', 8]
