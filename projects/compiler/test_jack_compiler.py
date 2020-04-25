import io
import pytest

from vm_emulator import VMEmulator
from jack_compiler import Compiler


@pytest.fixture
def vm():
    return VMEmulator()

def test_do_statement(vm):
    c = Compiler()
    vm.load(c.compile(io.StringIO('''
        class Main {
            static int _member_fn_calls;
            static int _static_fn_calls;

            constructor Main new() {
                let _member_fn_calls = 0;
                let _static_fn_calls = 0;
                return this;
            }

            method void _member_fn(int x, int y) {
                let _member_fn_calls = _member_fn_calls + 1;
                return;
            }

            method void member_fn(int x, int y) {
                let _member_fn_calls = _member_fn_calls + 1;
                do _member_fn(x, y);
                return;
            }

            function void static_fn() {
                let _static_fn_calls = _static_fn_calls + 1;
                return;
            }

            function void run() {
                var Main v;
                let v = Main.new();

                do Main.static_fn();
                do v.member_fn(0, 1);
                return;
            }
        }
    ''')))

    vm.execute([
        'call Main.run 0',
    ])

    assert vm.memory['static'][0] == 2  # _member_fn_calls
    assert vm.memory['static'][1] == 1  # _static_fn_calls
    assert vm.stack == [0]


def test_let_statement(vm):
    c = Compiler()
    vm.load(c.compile(io.StringIO('''
        class Main {
            function in sum(int x, int y) {
                var int res;
                let res = x + y;
                return res;
            }
        }
    ''')))

    vm.execute([
        'push constant 10',
        'push constant 20',
        'call Main.sum 2',
    ])

    assert vm.stack == [30]


def test_if_statement(vm):
    c = Compiler()
    vm.load(c.compile(io.StringIO('''
        class Main {
            function in fn() {
                var int x;
                let x = 0;
                if (x = 0) {
                    let x = x + 1;
                } else {
                    let x = x + 10;
                }
                if (x = 0) {
                    let x = x + 100;
                } else {
                    let x = x + 200;
                }
                if (x < 200) {
                    let x = x - 100;
                }
                if (x > 200) {
                    let x = x + 100;
                }
                return x;
            }
        }
    ''')))

    vm.execute([
        'call Main.fn 0',
    ])

    assert vm.stack == [301]


def test_while_statement(vm):
    c = Compiler()
    vm.load(c.compile(io.StringIO('''
        class Main {
            function in fn() {
                var int i, x;
                let x = 0;
                let i = 3;
                while (i > 0) {
                    let x = x + 1;
                    let i = i - 1;
                }
                return x;
            }
        }
    ''')))

    vm.execute([
        'call Main.fn 0',
    ])

    assert vm.stack == [3]


def test_unary_op(vm):
    c = Compiler()
    vm.load(c.compile(io.StringIO('''
        class Main {
            function in neg(int x) {
                return -x;
            }
        }
    ''')))

    vm.execute([
        'push constant 10',
        'call Main.neg 1',
    ])

    assert vm.stack == [-10]


def test_array_access(vm):
    c = Compiler()
    vm.load(c.compile(io.StringIO('''
        class Main {
            function int two(String s) {
                return 2;
            }
            function in fn() {
                var Array a, b;
                let a = Array.new(2);
                let b = Array.new(1);
                let a[0] = two("some msg");
                let a[1] = 2 + 2;
                let b[0] = a[0] + a[1];
                return b[0];
            }
        }
    ''')))

    vm.execute([
        'call Main.fn 0',
    ])

    assert vm.stack == [6]


def test_string_const(vm):
    c = Compiler()
    vm.load(c.compile(io.StringIO('''
        class Main {
            function char fn() {
                var String s;
                let s = "qwerty";
                return s.charAt(1);
            }
        }
    ''')))

    vm.execute([
        'call Main.fn 0',
    ])

    assert vm.stack == [ord('w')]


def test_parenthesized_expression(vm):
    c = Compiler()
    vm.load(c.compile(io.StringIO('''
        class Main {
            function in triple(int x) {
                return (x + (x + x));
            }
        }
    ''')))

    vm.execute([
        'push constant 10',
        'call Main.triple 1',
    ])

    assert vm.stack == [30]
