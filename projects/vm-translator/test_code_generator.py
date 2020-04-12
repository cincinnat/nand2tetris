import pytest

import keywords as kw
from vm_emulator import VMEmulator
from code_generator import CodeGenerator


@pytest.fixture
def vm():
    return VMEmulator(trace=True)


def test_push_constant(vm):
    g = CodeGenerator()
    code = g.translate([
            (0, 'push', 'constant', 1),
            (1, 'push', 'constant', 10),
            (2, 'push', 'constant', 100),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 3,
        vm.stack_offset + 0: 1,
        vm.stack_offset + 1: 10,
        vm.stack_offset + 2: 100,
    }


def test_push_static(vm):
    static_offset = vm.symbols['R15'] + 1
    vm.ram[static_offset + 0] = 33
    vm.ram[static_offset + 1] = 22

    g = CodeGenerator()
    code = g.translate([
            (0, 'push', 'static', 1),
            (1, 'push', 'static', 10),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 2,
        static_offset + 0: 33,
        static_offset + 1: 22,
        vm.stack_offset + 0: 33,
        vm.stack_offset + 1: 22,
    }


def test_push_local(vm):
    local_offset = 512
    vm.ram[vm.symbols['LCL']] = local_offset
    vm.ram[local_offset + 1] = 33
    vm.ram[local_offset + 10] = 22

    g = CodeGenerator()
    code = g.translate([
            (0, 'push', 'local', 1),
            (1, 'push', 'local', 10),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 2,
        vm.symbols['LCL']: local_offset,
        local_offset + 1: 33,
        local_offset + 10: 22,
        vm.stack_offset + 0: 33,
        vm.stack_offset + 1: 22,
    }


def test_push_argument(vm):
    argument_offset = 512
    vm.ram[vm.symbols['ARG']] = argument_offset
    vm.ram[argument_offset + 1] = 33
    vm.ram[argument_offset + 10] = 22

    g = CodeGenerator()
    code = g.translate([
            (0, 'push', 'argument', 1),
            (1, 'push', 'argument', 10),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 2,
        vm.symbols['ARG']: argument_offset,
        argument_offset + 1: 33,
        argument_offset + 10: 22,
        vm.stack_offset + 0: 33,
        vm.stack_offset + 1: 22,
    }


def test_push_this(vm):
    this_offset = 512
    vm.ram[vm.symbols['THIS']] = this_offset
    vm.ram[this_offset + 1] = 33
    vm.ram[this_offset + 10] = 22

    g = CodeGenerator()
    code = g.translate([
            (0, 'push', 'this', 1),
            (1, 'push', 'this', 10),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 2,
        vm.symbols['THIS']: this_offset,
        this_offset + 1: 33,
        this_offset + 10: 22,
        vm.stack_offset + 0: 33,
        vm.stack_offset + 1: 22,
    }


def test_push_that(vm):
    that_offset = 512
    vm.ram[vm.symbols['THAT']] = that_offset
    vm.ram[that_offset + 1] = 33
    vm.ram[that_offset + 10] = 22

    g = CodeGenerator()
    code = g.translate([
            (0, 'push', 'that', 1),
            (1, 'push', 'that', 10),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 2,
        vm.symbols['THAT']: that_offset,
        that_offset + 1: 33,
        that_offset + 10: 22,
        vm.stack_offset + 0: 33,
        vm.stack_offset + 1: 22,
    }


def test_push_pointer(vm):
    vm.ram[vm.symbols['R3']] = 33
    vm.ram[vm.symbols['R4']] = 22

    g = CodeGenerator()
    code = g.translate([
            (0, 'push', 'pointer', 0),
            (1, 'push', 'pointer', 1),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 2,
        vm.symbols['R3']: 33,
        vm.symbols['R4']: 22,
        vm.stack_offset + 0: 33,
        vm.stack_offset + 1: 22,
    }


def test_push_temp(vm):
    vm.ram[vm.symbols['R5'] + 1] = 33
    vm.ram[vm.symbols['R5'] + 3] = 22

    g = CodeGenerator()
    code = g.translate([
            (0, 'push', 'temp', 1),
            (1, 'push', 'temp', 3),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 2,
        vm.symbols['R5'] + 1: 33,
        vm.symbols['R5'] + 3: 22,
        vm.stack_offset + 0: 33,
        vm.stack_offset + 1: 22,
    }


def test_pop_static(vm):
    static_offset = vm.symbols['R15'] + 1
    vm.ram[vm.stack_offset + 0] = 33
    vm.ram[vm.stack_offset + 1] = 22
    vm.ram[vm.symbols['SP']] += 2

    g = CodeGenerator()
    code = g.translate([
            (0, 'pop', 'static', 1),
            (1, 'pop', 'static', 10),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset,
        static_offset + 0: 22,
        static_offset + 1: 33,
        vm.stack_offset + 0: 33,
        vm.stack_offset + 1: 22,
    }


def test_pop_local(vm):
    local_offset = 512
    vm.ram[vm.symbols['LCL']] = local_offset
    vm.ram[vm.stack_offset + 0] = 33
    vm.ram[vm.stack_offset + 1] = 22
    vm.ram[vm.symbols['SP']] += 2

    g = CodeGenerator()
    code = g.translate([
            (0, 'pop', 'local', 1),
            (1, 'pop', 'local', 10),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset,
        vm.symbols['LCL']: local_offset,
        local_offset + 1: 22,
        local_offset + 10: 33,
        vm.stack_offset + 0: 33,
        vm.stack_offset + 1: 22,
    }


def test_pop_argument(vm):
    argument_offset = 512
    vm.ram[vm.symbols['ARG']] = argument_offset
    vm.ram[vm.stack_offset + 0] = 33
    vm.ram[vm.stack_offset + 1] = 22
    vm.ram[vm.symbols['SP']] += 2

    g = CodeGenerator()
    code = g.translate([
            (0, 'pop', 'argument', 1),
            (1, 'pop', 'argument', 10),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset,
        vm.symbols['ARG']: argument_offset,
        argument_offset + 1: 22,
        argument_offset + 10: 33,
        vm.stack_offset + 0: 33,
        vm.stack_offset + 1: 22,
    }


def test_pop_this(vm):
    this_offset = 512
    vm.ram[vm.symbols['THIS']] = this_offset
    vm.ram[vm.stack_offset + 0] = 33
    vm.ram[vm.stack_offset + 1] = 22
    vm.ram[vm.symbols['SP']] += 2

    g = CodeGenerator()
    code = g.translate([
            (0, 'pop', 'this', 1),
            (1, 'pop', 'this', 10),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset,
        vm.symbols['THIS']: this_offset,
        this_offset + 1: 22,
        this_offset + 10: 33,
        vm.stack_offset + 0: 33,
        vm.stack_offset + 1: 22,
    }


def test_pop_that(vm):
    that_offset = 512
    vm.ram[vm.symbols['THAT']] = that_offset
    vm.ram[vm.stack_offset + 0] = 33
    vm.ram[vm.stack_offset + 1] = 22
    vm.ram[vm.symbols['SP']] += 2

    g = CodeGenerator()
    code = g.translate([
            (0, 'pop', 'that', 1),
            (1, 'pop', 'that', 10),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset,
        vm.symbols['THAT']: that_offset,
        that_offset + 1: 22,
        that_offset + 10: 33,
        vm.stack_offset + 0: 33,
        vm.stack_offset + 1: 22,
    }


def test_pop_pointer(vm):
    pointer_offset = vm.symbols[kw.special_segmnets['pointer']]
    vm.ram[vm.stack_offset + 0] = 33
    vm.ram[vm.stack_offset + 1] = 22
    vm.ram[vm.symbols['SP']] += 2

    g = CodeGenerator()
    code = g.translate([
            (0, 'pop', 'pointer', 0),
            (1, 'pop', 'pointer', 1),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset,
        pointer_offset + 0: 22,
        pointer_offset + 1: 33,
        vm.stack_offset + 0: 33,
        vm.stack_offset + 1: 22,
    }


def test_pop_temp(vm):
    temp_offset = vm.symbols[kw.special_segmnets['temp']]
    vm.ram[vm.stack_offset + 0] = 33
    vm.ram[vm.stack_offset + 1] = 22
    vm.ram[vm.symbols['SP']] += 2

    g = CodeGenerator()
    code = g.translate([
            (0, 'pop', 'temp', 1),
            (1, 'pop', 'temp', 3),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset,
        temp_offset + 1: 22,
        temp_offset + 3: 33,
        vm.stack_offset + 0: 33,
        vm.stack_offset + 1: 22,
    }


def test_add(vm):
    vm.ram[vm.stack_offset + 0] = 22
    vm.ram[vm.stack_offset + 1] = 33
    vm.ram[vm.symbols['SP']] += 2

    g = CodeGenerator()
    code = g.translate([
            (0, 'add'),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 1,
        vm.stack_offset + 0: 22+33,
        vm.stack_offset + 1: 33,
    }


def test_sub(vm):
    vm.ram[vm.stack_offset + 0] = 22
    vm.ram[vm.stack_offset + 1] = 33
    vm.ram[vm.symbols['SP']] += 2

    g = CodeGenerator()
    code = g.translate([
            (0, 'sub'),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 1,
        vm.stack_offset + 0: 22-33,
        vm.stack_offset + 1: 33,
    }


def test_neg(vm):
    vm.ram[vm.stack_offset + 0] = 22
    vm.ram[vm.symbols['SP']] += 1

    g = CodeGenerator()
    code = g.translate([
            (0, 'neg'),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 1,
        vm.stack_offset + 0: -22,
    }


def test_and(vm):
    vm.ram[vm.stack_offset + 0] = 22
    vm.ram[vm.stack_offset + 1] = 21
    vm.ram[vm.symbols['SP']] += 2

    g = CodeGenerator()
    code = g.translate([
            (0, 'and'),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 1,
        vm.stack_offset + 0: 22&21,
        vm.stack_offset + 1: 21,
    }


def test_or(vm):
    vm.ram[vm.stack_offset + 0] = 22
    vm.ram[vm.stack_offset + 1] = 21
    vm.ram[vm.symbols['SP']] += 2

    g = CodeGenerator()
    code = g.translate([
            (0, 'or'),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 1,
        vm.stack_offset + 0: 22|21,
        vm.stack_offset + 1: 21,
    }


def test_not(vm):
    vm.ram[vm.stack_offset + 0] = 22
    vm.ram[vm.symbols['SP']] += 1

    g = CodeGenerator()
    code = g.translate([
            (0, 'not'),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 1,
        vm.stack_offset + 0: ~22,
    }


@pytest.mark.parametrize("a,b,expected", [
        (-1, -2, -1),
        (-2, -1, 0),
        (-1, -1, 0),
        (-1, 0, 0),
        (0, -1, -1),
        (0, 0, 0),
        (0, 1, 0),
        (1, 0, -1),
        (2, 1, -1),
        (1, 2, 0),
        (1, 1, 0),
        (-1, 1, 0),
        (1, -1, -1),
    ])
def test_gt(vm, a, b, expected):
    vm.ram[vm.stack_offset + 0] = a
    vm.ram[vm.stack_offset + 1] = b
    vm.ram[vm.symbols['SP']] += 2

    g = CodeGenerator()
    code = g.translate([
            (0, 'gt'),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 1,
        vm.stack_offset + 0: expected,
        vm.stack_offset + 1: b,
    }



@pytest.mark.parametrize("a,b,expected", [
        (-1, -2, 0),
        (-2, -1, -1),
        (-1, -1, 0),
        (-1, 0, -1),
        (0, -1, 0),
        (0, 0, 0),
        (0, 1, -1),
        (1, 0, 0),
        (2, 1, 0),
        (1, 2, -1),
        (1, 1, 0),
        (-1, 1, -1),
        (1, -1, 0),
    ])
def test_lt(vm, a, b, expected):
    vm.ram[vm.stack_offset + 0] = a
    vm.ram[vm.stack_offset + 1] = b
    vm.ram[vm.symbols['SP']] += 2

    g = CodeGenerator()
    code = g.translate([
            (0, 'lt'),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 1,
        vm.stack_offset + 0: expected,
        vm.stack_offset + 1: b,
    }

@pytest.mark.parametrize("a,b,expected", [
        (-1, -2, 0),
        (-1, -1, -1),
        (0, 0, -1),
        (-1, 1, 0),
        (1, 1, -1),
        (2, 1, 0),
    ])
def test_eq(vm, a, b, expected):
    vm.ram[vm.stack_offset + 0] = a
    vm.ram[vm.stack_offset + 1] = b
    vm.ram[vm.symbols['SP']] += 2

    g = CodeGenerator()
    code = g.translate([
            (0, 'eq'),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, max_steps=100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 1,
        vm.stack_offset + 0: expected,
        vm.stack_offset + 1: b,
    }


def test_label(vm):
    g = CodeGenerator()
    code = g.translate([
            (0, 'label', 'name1'),
            (1, 'label', 'name2'),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, 100)

    assert vm.symbols['<output>$name1'] == 0
    assert vm.symbols['<output>$name2'] == 1


def test_goto(vm):
    g = CodeGenerator()
    code = g.translate([
            (0, 'push', 'constant', 10),
            (1, 'goto', 'end'),
            (2, 'push', 'constant', 20),
            (3, 'label', 'end'),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, 100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset + 1,
        vm.stack_offset + 0: 10,
    }


def test_if_goto(vm):
    g = CodeGenerator()
    code = g.translate([
            (0, 'push', 'constant', 0),
            (1, 'if-goto', 'end'),
            (2, 'push', 'constant', 10),
            (1, 'if-goto', 'end'),
            (2, 'push', 'constant', 20),
            (1, 'if-goto', 'end'),
            (3, 'label', 'end'),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, 100)

    assert vm.ram == {
        vm.symbols['SP']: vm.stack_offset,
        vm.stack_offset + 0: 10,
    }


def test_label_within_function(vm):
    g = CodeGenerator()
    code = g.translate([
            (0, 'call', 'fn', 0),
            (1, 'goto', 'end'),
            (2, 'function', 'fn', 0),
            (5, 'push', 'constant', 0),
            (3, 'goto', 'end'),
            (4, 'label', 'label1'),
            (6, 'return'),
            (4, 'label', 'end'),
            (6, 'return'),
            (7, 'label', 'end'),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, 500)

    assert '<input>$end' in vm.symbols
    assert '<input>$fn$label1' in vm.symbols
    assert '<input>$fn$end' in vm.symbols


def test_function_statement(vm):
    local_segment_size = 2
    initial_sp = 512
    vm.ram[vm.symbols['SP']] = initial_sp
    vm.ram[vm.symbols['LCL']] = vm.ram[vm.symbols['SP']]

    g = CodeGenerator()
    code = g.translate([
            (0, 'function', 'fn', local_segment_size),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, 100)

    assert vm.symbols['fn'] == 0
    assert vm.ram == {
        vm.symbols['SP']: initial_sp + local_segment_size,
        vm.symbols['LCL']: initial_sp,
        initial_sp + 0: 0,
        initial_sp + 1: 0,
    }


def test_return_statement(vm):
    n_args = 3
    frame_offset = 512
    current_sp = frame_offset + 100
    arg1 = 111
    arg2 = 222
    arg3 = 333
    caller_arg = 254
    caller_lcl = caller_arg + 5
    caller_this = 1234
    caller_that = 2345
    return_addr = 6000
    return_value = 42

    vm.ram[frame_offset + 0] = arg1
    vm.ram[frame_offset + 1] = arg2
    vm.ram[frame_offset + 2] = arg3
    vm.ram[frame_offset + 3] = return_addr
    vm.ram[frame_offset + 4] = caller_lcl
    vm.ram[frame_offset + 5] = caller_arg
    vm.ram[frame_offset + 6] = caller_this
    vm.ram[frame_offset + 7] = caller_that
    vm.ram[current_sp - 1] = return_value

    vm.ram[vm.symbols['LCL']] = frame_offset + n_args + 5
    vm.ram[vm.symbols['ARG']] = frame_offset
    vm.ram[vm.symbols['THIS']] = 5555
    vm.ram[vm.symbols['THAT']] = 6666
    vm.ram[vm.symbols['SP']] = current_sp

    g = CodeGenerator()
    g.translate([
            (0, 'function', 'fn', 0),
        ],
        output='<output>',
        dry_run=True,
    )
    code = g.translate([
            (0, 'return'),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, 100)

    assert vm.ram == {
        vm.symbols['SP']: frame_offset + 1,
        vm.symbols['LCL']: caller_lcl,
        vm.symbols['ARG']: caller_arg,
        vm.symbols['THIS']: caller_this,
        vm.symbols['THAT']: caller_that,

        frame_offset + 0: return_value,
        frame_offset + 1: arg2,
        frame_offset + 2: arg3,
        frame_offset + 3: return_addr,
        frame_offset + 4: caller_lcl,
        frame_offset + 5: caller_arg,
        frame_offset + 6: caller_this,
        frame_offset + 7: caller_that,
        current_sp - 1: return_value,
    }


def test_call_statement(vm):
    caller_arg = 254
    caller_lcl = caller_arg + 5
    caller_this = 1234
    caller_that = 2345
    caller_sp = 512

    n_args = 3
    arg1 = 111
    arg2 = 222
    arg3 = 333

    vm.symbols['fn'] = 8192
    vm.ram[vm.symbols['SP']] = caller_sp
    vm.ram[vm.symbols['LCL']] = caller_lcl
    vm.ram[vm.symbols['ARG']] = caller_arg
    vm.ram[vm.symbols['THIS']] = caller_this
    vm.ram[vm.symbols['THAT']] = caller_that

    vm.ram[caller_sp - 3] = arg1
    vm.ram[caller_sp - 2] = arg2
    vm.ram[caller_sp - 1] = arg3

    g = CodeGenerator()
    code = g.translate([
            (0, 'call', 'fn', n_args),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, 100)

    assert vm.ram == {
        vm.symbols['SP']: caller_sp + 5,
        vm.symbols['LCL']: caller_sp + 5,
        vm.symbols['ARG']: caller_sp - n_args,
        vm.symbols['THIS']: caller_this,
        vm.symbols['THAT']: caller_that,

        caller_sp - 3: arg1,
        caller_sp - 2: arg2,
        caller_sp - 1: arg3,
        caller_sp + 0: vm.symbols['fn$ret.1'],
        caller_sp + 1: caller_lcl,
        caller_sp + 2: caller_arg,
        caller_sp + 3: caller_this,
        caller_sp + 4: caller_that,
    }


def test_function_calls(vm):
    g = CodeGenerator()
    code = g.translate([
            (0,  'call', 'main', 0),
            (1,  'goto', 'end'),

            (2,  'function', 'main', 0),
            (3,  'push', 'constant', 10),
            (4,  'push', 'constant', 20),
            (5,  'call', 'double-sum', 2),
            (6,  'return'),

            (7,  'function', 'double-sum', 1),
            (8,  'push', 'argument', 0),
            (9,  'push', 'argument', 1),
            (10, 'add'),
            (11, 'pop', 'local', 0),
            (12, 'push', 'local', 0),
            (13, 'push', 'local', 0),
            (14, 'add'),
            (15, 'return'),

            (16, 'label', 'end'),
        ],
        output='<output>',
        dry_run=True,
    )
    vm.execute(code, 500)

    assert vm.ram[vm.symbols['SP']] == vm.stack_offset + 1
    assert vm.ram[vm.stack_offset] == 2 * (10 + 20)


def test_program(vm):
    raise NotImplementedError()
