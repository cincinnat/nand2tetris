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
