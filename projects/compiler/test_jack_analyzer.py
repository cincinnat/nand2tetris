import io
import pytest

import jack_tokenizer
import jack_analyzer


def gen_tokens(source):
    tokenizer = jack_tokenizer.Tokenizer()
    return tokenizer.tokenize(io.StringIO(source))


def find_node(root, name, value):
    if root.name == name and root.value == value:
        return root
    for child in root.children:
        node = find_node(child, name, value)
        if node is not None:
            return node
    return None


@pytest.mark.parametrize('name', [
        'identifier',
        'class_name',
        'var_name',
        'subroutine_name',
    ])
def test_identifiers(name):
    tokens = gen_tokens('foo')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=getattr(a, name))
    assert find_node(tree, 'identifier', 'foo')


def test_class_dec():
    tokens = gen_tokens('''
            class Foo {
                static int static_var;
                field int field_var;

                constructor Foo new() { return this; }
                function void static_fn() { return; }
                method void method_fn() { return; }
            }
        ''')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.class_dec)

    assert find_node(tree, 'identifier', 'static_var')
    assert find_node(tree, 'identifier', 'field_var')
    assert find_node(tree, 'identifier', 'new')
    assert find_node(tree, 'identifier', 'static_fn')
    assert find_node(tree, 'identifier', 'method_fn')


def test_class_var_decs():
    tokens = gen_tokens('''
            static int static_var;
            field int field_var;
        ''')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.class_var_decs)

    assert find_node(tree, 'identifier', 'static_var')
    assert find_node(tree, 'identifier', 'field_var')


@pytest.mark.parametrize('scope', ['static', 'field'])
def test_class_var_dec(scope):
    tokens = gen_tokens(f'{scope} int x;')

    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.class_var_dec)
    assert find_node(tree, 'keyword', scope)
    assert find_node(tree, 'keyword', 'int')
    assert find_node(tree, 'identifier', 'x')


@pytest.mark.parametrize('type_name', jack_analyzer.type_names + ['MyClass'])
def test_type_name(type_name):
    tokens = gen_tokens(type_name)

    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.type_name)
    if type_name in jack_analyzer.type_names:
        assert find_node(tree, 'keyword', type_name)
    else:
        assert find_node(tree, 'identifier', type_name)


@pytest.mark.parametrize('varlist', [
        ['x', 'y', 'z'],
        ['a']
    ])
def test_var_names(varlist):
    tokens = gen_tokens(','.join(varlist))

    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.var_names)
    for var in varlist:
        assert find_node(tree, 'identifier', var)


def test_subroutine_decs():
    tokens = gen_tokens('''
            constructor Foo new() { return Foo; }
            method void fn() { return; }
        ''')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.subroutine_decs)

    assert find_node(tree, 'identifier', 'new')
    assert find_node(tree, 'identifier', 'fn')


@pytest.mark.parametrize('scope', ['constructor', 'function', 'method'])
def test_subroutine_dec(scope):
    tokens = gen_tokens(f'{scope} int name() {{ return; }}')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.subroutine_decs)

    assert find_node(tree, 'keyword', scope)
    assert find_node(tree, 'identifier', 'name')


def test_parameter_list():
    tokens = gen_tokens(f'int x, boolean y')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.parameter_list)

    assert find_node(tree, 'keyword', 'int')
    assert find_node(tree, 'identifier', 'x')
    assert find_node(tree, 'keyword', 'boolean')
    assert find_node(tree, 'identifier', 'y')


def test_subroutine_body():
    tokens = gen_tokens('''
            {
                var int x, y, z;
                let z = x + y;
                return z;
            }
        ''')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.subroutine_body)

    assert find_node(tree, 'keyword', 'var')
    assert find_node(tree, 'keyword', 'let')
    assert find_node(tree, 'keyword', 'return')


def test_var_decs():
    tokens = gen_tokens('''
            var int x;
            var boolean f;
        ''')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.var_decs)

    assert find_node(tree, 'identifier', 'x')
    assert find_node(tree, 'identifier', 'f')


@pytest.mark.parametrize('varlist', [
        ['x', 'y'],
        ['z'],
    ])
def test_var_dec(varlist):
    tokens = gen_tokens(f'var int {",".join(varlist)};')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.var_dec)

    for var in varlist:
        assert find_node(tree, 'identifier', var)


def test_statements():
    tokens = gen_tokens('''
            let x = 0;
            do Foo.foo();
            return;
        ''')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.statements)

    assert find_node(tree, 'keyword', 'let')
    assert find_node(tree, 'keyword', 'do')
    assert find_node(tree, 'keyword', 'return')


@pytest.mark.parametrize('stmt', [
        'let x = 0;',
        'if (x) { let x = x; }',
        'while (x) { let x = x; }',
        'return x;',
    ])
def test_statement(stmt):
    tokens = gen_tokens(stmt)
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.statement)

    assert find_node(tree, 'keyword', stmt.split()[0])


def test_let_statements():
    tokens = gen_tokens('let x = 0;')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.let_statement)

    assert find_node(tree, 'keyword', 'let')
    assert find_node(tree, 'identifier', 'x')
    assert find_node(tree, 'int_const', 0)


def test_do_statements():
    tokens = gen_tokens('do foo.Foo();')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.do_statement)

    assert find_node(tree, 'keyword', 'do')
    assert find_node(tree, 'identifier', 'foo')
    assert find_node(tree, 'identifier', 'Foo')


def test_if_statements():
    tokens = gen_tokens('if (x) { let x = x; }')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.if_statement)

    assert find_node(tree, 'keyword', 'if')


def test_while_statements():
    tokens = gen_tokens('while (x) { let x = x; }')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.while_statement)

    assert find_node(tree, 'keyword', 'while')


@pytest.mark.parametrize('stmt', [
        'return;',
        'return x;',
    ])
def test_return_statements(stmt):
    tokens = gen_tokens(stmt)
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.return_statement)

    assert find_node(tree, 'keyword', 'return')


def test_expression():
    tokens = gen_tokens('x < y')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.expression)

    assert find_node(tree, 'identifier', 'x')
    assert find_node(tree, 'symbol', '<')
    assert find_node(tree, 'identifier', 'y')


@pytest.mark.parametrize('term', [
        '1234',
        '"qwerty"',
        *jack_analyzer.constants,
        'foo',
        'x[0]',
        'Foo.foo(x+1)',
        '(a+b)',
        '-x',
    ])
def test_term(term):
    tokens = gen_tokens(term)
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.expression)
    # should not raise an exception


@pytest.mark.parametrize('const', jack_analyzer.constants)
def test_constant(const):
    tokens = gen_tokens(const)

    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.constant)
    assert find_node(tree, 'keyword', const)


def test_int_const():
    tokens = gen_tokens('1234')

    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.int_const)
    assert find_node(tree, 'int_const', 1234)


def test_string_cons():
    tokens = gen_tokens('"qwerty"')

    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.string_const)
    assert find_node(tree, 'string_const', '"qwerty"')


@pytest.mark.parametrize('op', jack_analyzer.binary_ops)
def test_binary_op(op):
    tokens = gen_tokens(op)

    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.binary_op)
    assert find_node(tree, 'symbol', op)


@pytest.mark.parametrize('op', jack_analyzer.unary_ops)
def test_unary_op(op):
    tokens = gen_tokens(op)

    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.unary_op)
    assert find_node(tree, 'symbol', op)


@pytest.mark.parametrize('args', [
        ['a', 'b'],
        ['a+b'],
        [],
    ])
def test_subroutine_call(args):
    tokens = gen_tokens(f'Foo.foo({",".join(args)})')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.subroutine_call)

    assert find_node(tree, 'identifier', 'Foo')
    assert find_node(tree, 'identifier', 'foo')


def test_expression_list():
    tokens = gen_tokens('a+b, c')
    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.expression_list)

    assert find_node(tree, 'identifier', 'a')
    assert find_node(tree, 'identifier', 'b')
    assert find_node(tree, 'identifier', 'c')


def test_symbol():
    tokens = gen_tokens('=')

    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.symbol)
    assert find_node(tree, 'symbol', '=')


def test_keyword():
    tokens = gen_tokens('class')

    a = jack_analyzer.Analyzer()
    tree = a.start(tokens, entry_point=a.keyword)
    assert find_node(tree, 'keyword', 'class')


def test_start():
    tokens = gen_tokens('''
            class Point {
               field int _x;
               field int _y;

               constructor Point new(int x, int y) {
                   let _x = x + 1;
                   let _y = y + 1;
               }

               method void dispose() {
                   do Memory.deAlloc();
               }

               method int getX() { return _x; }
               method int getY() { return _y; }

               method boolean lt(Point other) {
                   return ((_x < other.getX())
                       | ((_x = other.getX()) & (_y < other.getY())));
               }
            }
        ''')


    a = jack_analyzer.Analyzer()
    tree = a.start(tokens)
    assert tree.name == 'start'
