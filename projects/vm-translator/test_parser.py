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


def test_branching_commands():
    p = Parser()
    commands = p.parse('''
        label start
        push constant 0
        if-goto start
        goto end
        label end
    ''')
    commands = list(commands)

    assert len(commands) == 5


def test_function():
    p = Parser()
    commands = p.parse('''   // 0
        function fn 0        // 1
            push argument 0  // 2
            push argument 1  // 3
            add              // 4
            return           // 5
                             // 6
        push constant 10     // 7
        push constant 20     // 8
        call fn 2            // 9
    ''')
    commands = list(commands)

    assert len(commands) == 8
    assert commands[0] == [1, 'function', 'fn', 0]
    assert commands[7] == [9, 'call', 'fn', 2]
