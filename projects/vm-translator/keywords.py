memory_segments = {
        'argument',
        'local',
        'static',
        'constant',
        'this',
        'that',
        'pointer',
        'temp',
    }

segment_pointers = {
        'argument': 'ARG',
        'local': 'LCL',
        'this': 'THIS',
        'that': 'THAT',
    }

special_segmnets = {
        'pointer': 'R3',
        'temp': 'R5',
    }

constants = {
        'SP': 0,
        'LCL': 1,
        'ARG': 2,
        'THIS': 3,
        'THAT': 4,
        **{'R%d' % i: i for i in range(16)},
        'SCREEN': 16384,
        'KBD': 24576,
    }

arithmetic_commands = {
        'add',
        'sub',
        'neg',
        'eq',
        'gt',
        'lt',
        'and',
        'or',
        'not',
    }


memory_access_commands = {
        'push',
        'pop',
    }

commands = {
    *arithmetic_commands,
    *memory_access_commands,
}
