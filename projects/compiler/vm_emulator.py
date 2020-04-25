import collections

class Frame:
    def __init__(self, pc, stack_size, memory):
        self.pc = pc
        self.stack_size = stack_size
        self.segments = dict(
            argument = memory['argument'],
            local = memory['local'],
            this = memory['this'],
            that = memory['that'],
        )


class VMEmulator:
    def __init__(self):
        self.memory = collections.defaultdict(list)
        self.stack = []
        self.heap = []
        self.program = None
        self.program_size = None
        self.pc = 0

        self.caller_frame = []

    def _parse(self, prog):
        def parse(cmd):
            cmd = cmd.split('//')[0].strip()
            if cmd:
                return cmd.split()
            return None
        cmd = filter(bool, map(parse, prog))
        return list(map(tuple, cmd))

    def load(self, program):
        program = list(program)
        print()
        for i, cmd in enumerate(program):
            print('>>>', i+1, cmd)
        self.program = self._parse(program)
        self.program_size = len(self.program)

    def execute(self, commands):
        assert self.program

        self.stack.clear()
        self.memory.clear()
        self.memory['static'] = collections.defaultdict(int)
        self.memory['pointer'] = [0, 0]
        self.memory['this'] = [0]
        self.memory['that'] = [0]
        self.memory['temp'] = [0] * 8
        self.program = self.program[:self.program_size]
        self.program.extend(self._parse(commands))
        self.pc = self.program_size

        total_commands = 0
        while self.pc < len(self.program):
            self._execute(self.program[self.pc])
            total_commands += 1
            assert total_commands < 100

    def _execute(self, cmd):
        print('#', self.pc, cmd)

        def handle_numbers(string):
            try:
                return int(string)
            except ValueError:
                return string
        cmd = tuple(map(handle_numbers, cmd))

        instruction = cmd[0].replace('-', '_')
        handler = getattr(self, f'_{instruction}')

        prev_pc = self.pc
        handler(*cmd[1:])
        if self.pc == prev_pc:
            self.pc += 1

    def _push(self, segment, index):
        if segment in ['this', 'that']:
            value = self.heap[self.memory[segment][0] + index]
        elif segment == 'pointer':
            target = ['this', 'that'][index]
            value = self.memory[target][0]
        elif segment == 'constant':
            value = index
        else:
            value = self.memory[segment][index]

        self.stack.append(value)

    def _pop(self, segment, index):
        value = self.stack.pop()

        if segment in ['this', 'that']:
            self.heap[self.memory[segment][0] + index] = value
        elif segment == 'pointer':
            target = ['this', 'that'][index]
            self.memory[target][0] = value
        else:
            self.memory[segment][index] = value

    def _call(self, function, nargs):
        def convert_builtin(function):
            return '_builtin_' + function.lower().replace('.', '_')
        if hasattr(self, convert_builtin(function)):
            getattr(self, convert_builtin(function))()
            return

        self.caller_frame.append(Frame(self.pc, len(self.stack), self.memory))

        self.memory['argument'] = list(reversed([
            self.stack.pop() for i in range(nargs)]))
        self.memory['local'] = []
        self.memory['this'] = [0]
        self.memory['that'] = [0]
        self.pc = self.__find('function', function)

    def __find(self, *args):
        for i, cmd in enumerate(self.program):
            if cmd[:len(args)] == args:
                return i
        assert False, args

    def _return(self):
        frame = self.caller_frame.pop()
        for segment, data in frame.segments.items():
            self.memory[segment] = data
        self.pc = frame.pc + 1

    def _function(self, name, nlocals):
        self.memory['local'] = [0] * nlocals

    def _label(self, name):
        # do nothing
        pass

    def _goto(self, label):
        self.pc = self.__find('label', label)

    def _if_goto(self, label):
        if self.stack.pop():
            self._goto(label)

    def _builtin_memory_alloc(self):
        nbytes = self.stack.pop()
        assert nbytes > 0
        address = len(self.heap)
        self.heap.extend([0] * nbytes)
        self.stack.append(address)

    def _builtin_string_new(self):
        size = self.stack.pop() + 2
        address = len(self.heap)
        self.heap.extend([0] * size)
        self.heap[address] = size
        self.heap[address + 1] = 0
        self.stack.append(address)

    def _builtin_string_appendchar(self):
        ch = self.stack.pop()
        address = self.stack.pop()
        capacity = self.heap[address]
        size = self.heap[address + 1]
        assert size < capacity
        self.heap[address + 2 + size] = ch
        self.heap[address + 1] = size + 1
        self.stack.append(address)

    def _builtin_string_charat(self):
        idx = self.stack.pop()
        address = self.stack.pop()
        size = self.heap[address + 1]
        assert idx < size
        self.stack.append(self.heap[address + 2 + idx])

    def _builtin_array_new(self):
        size = self.stack.pop()
        assert size > 0
        address = len(self.heap)
        self.heap.extend([0] * size)
        self.stack.append(address)

    def _add(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a + b)

    def _eq(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a == b)

    def _lt(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a < b)

    def _gt(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a > b)

    def _sub(self):
        b = self.stack.pop()
        a = self.stack.pop()
        self.stack.append(a - b)

    def _neg(self):
        a = self.stack.pop()
        self.stack.append(-a)
