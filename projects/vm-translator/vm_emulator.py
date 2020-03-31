import collections
import ctypes
import keywords as kw


class MaxStepsExceededError(RuntimeError):
    pass


class VMEmulator:
    stack_offset = 256

    def __init__(self, trace=False):
        self.trace = trace
        self.reset()

    def reset(self):
        self.pc = 0
        self.ram = collections.defaultdict(ctypes.c_int16)
        self.A = 0
        self.D = 0
        self.symbols = dict(**kw.constants)

        self.ram[self.symbols['SP']] = self.stack_offset

    @property
    def M(self):
        return self.ram[self.A]

    @M.setter
    def M(self, value):
        self.ram[self.A] = value

    def execute(self, prog, max_steps=1000):
        instructions = self._parse(prog)
        self._resolve_labels(instructions)
        self._resolve_variables(instructions)

        finished = False
        for _ in range(max_steps):
            if self.pc >= len(instructions):
                finished = True
                break
            self._execute_instruction(instructions[self.pc])

        if not finished:
            raise MaxStepsExceededError(max_steps)

        # clear temporary data
        #
        for i in range(13, 16):
            if i in self.ram:
                del self.ram[i]

    def _parse(self, prog):
        instructions = prog.split('\n')
        parsed = []
        for instruction in instructions:
            instruction = instruction.strip()
            instruction = instruction.split('//')[0]
            if instruction:
                parsed.append(instruction)
        return parsed

    def _resolve_labels(self, instructions):
        for i, instruction in enumerate(instructions):
            if instruction.startswith('('):
                self.symbols[instruction[1:-1]] = i

    def _resolve_variables(self, instructions):
        i = 16
        for instruction in instructions:
            if instruction.startswith('@'):
                name = instruction[1:]
                try:
                    int(name)
                except ValueError:
                    # not a number
                    if name not in self.symbols:
                        self.symbols[name] = i
                        i += 1

    def _execute_instruction(self, instruction):
        if instruction.startswith('@'):
            self._execute_a_instruction(instruction)
        elif instruction.startswith('('):
            # we are at a label, do nothing
            self.__print_label(self.pc, instruction)
            self.pc += 1
        else:
            self._execute_c_instruction(instruction)

    def _execute_a_instruction(self, instruction):
        address = instruction[1:]
        try:
            address = int(address)
        except ValueError:
            address = self.symbols[address]
        self.A = address
        self.__print_a_instruction(self.pc, instruction, address)
        self.pc += 1

    def _execute_c_instruction(self, instruction):
        if ';' in instruction:
            cmd, jmp = instruction.split(';')
            jmp = jmp.strip()
        else:
            cmd = instruction
            jmp = None

        cmd = cmd.replace('M', 'self.M')
        cmd = cmd.replace('A', 'self.A')
        cmd = cmd.replace('D', 'self.D')
        cmd = cmd.replace('!', '~')

        if '=' in cmd:
            dest, comp = cmd.split('=')
        else:
            comp = cmd
            dest = None

        value = eval(comp)
        self.__print_c_instruction(self.pc, instruction, dest, value, jmp)

        if dest:
            exec(f'{dest}={value}')
        if (jmp == 'JMP'
            or (value < 0 and jmp in {'JLT', 'JLE', 'JNE'})
            or (value > 0 and jmp in {'JGT', 'JGE', 'JNE'})
            or (value == 0 and jmp in {'JLE', 'JEQ', 'JGE'})
            ):
            self.pc = self.A
        else:
            self.pc += 1


    def __print_c_instruction(self, pc, instruction, dest, value, jmp):
        if self.trace:
            if dest:
                cmd = f'{dest.split(".")[1]}={value}'
            else:
                cmd = str(value)
            if jmp:
                cmd = f'{cmd}; {jmp}'
            print(f'#> {pc:02d}: {cmd} \t // {instruction}')


    def __print_a_instruction(self, pc, instruction, address):
        if self.trace:
            print(f'#> {pc:02d}: @{address} \t // {instruction}')


    def __print_label(self, pc, instruction):
        if self.trace:
            print(f'#> {pc:02d}: {instruction}')
