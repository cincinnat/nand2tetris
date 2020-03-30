
class Compiler:
    _n_virtual_registers = 16

    _destinations = {
        None: 0b000,
        'A':  0b100,
        'D':  0b010,
        'M':  0b001,
    }

    _jumps = {
        None:  0b000,
        'JGT': 0b001,
        'JEQ': 0b010,
        'JLT': 0b100,
        'JMP': 0b111,
    }

    # replace M with A when a=1
    _ops = {
        #        123456
        '0':   0b101010,
        '1':   0b111111,
        '-1':  0b111010,
        'D':   0b001100,
        'A':   0b110000,
        '!D':  0b001101,
        '!A':  0b110001,
        '-D':  0b001111,
        '-A':  0b110011,
        'D+1': 0b011111,
        'A+1': 0b110111,
        'D-1': 0b001110,
        'A-1': 0b110010,
        'D+A': 0b000010,
        'D-A': 0b010011,
        'A-D': 0b000111,
        'D&A': 0b000000,
        'D|A': 0b010101,
    }


    def __init__(self):
        self._vars = {
            'SP': 0,
            'LCL': 1,
            'ARG': 2,
            'THIS': 3,
            'THAT': 4,
            **{'R%d' % i: i for i in range(self._n_virtual_registers)},
            'SCREEN': 16384,
            'KBD': 24576,
        }


    def compile(self, prog, output=None):
        prog = list(prog)
        self._count_instructions(prog)
        self._resolve_labels(prog)
        self._resolve_vars(prog)
        codes = self._compile(prog)

        if output:
            self._save_to(codes, output)
        return codes


    def _save_to(self, codes, path):
        with open(path, 'wt') as f:
            for code in codes:
                f.write(f'{code:016b}\n')


    def _count_instructions(self, prog):
        no = 0
        for comm in prog:
            if comm.itype != 'label':
                comm.no = no
                no += 1


    def _resolve_labels(self, prog):
        next_instruction = 0
        for comm in prog:
            if comm.itype == 'label':
                self._vars[comm.name] = next_instruction
            else:
                next_instruction += 1


    def _resolve_vars(self, prog):
        next_addr = self._n_virtual_registers
        for comm in prog:
            if comm.itype != 'A':
                continue

            try:
                addr = int(comm.address)
            except ValueError:
                if comm.address not in self._vars:
                    self._vars[comm.address] = next_addr
                    next_addr += 1
                addr = self._vars[comm.address]

            comm.address = addr


    def _compile(self, prog):
        instructions = []
        for comm in prog:
            if comm.itype == 'label':
                continue

            if comm.itype == 'A':
                instructions.append(self._compile_a_instruction(comm))
            elif comm.itype == 'C':
                instructions.append(self._compile_c_instruction(comm))
            else:
                RuntimeError('Invalid instruction: lineno: %s' % comm.lineno)

        return instructions


    def _compile_a_instruction(self, comm):
        return comm.address


    def _compile_c_instruction(self, comm):
        dest = self._compile_dest(comm)
        jmp = self._compile_jmp(comm)
        comp = self._compile_comp(comm)

        instruction = 0b111 << 13
        instruction |= dest << 3
        instruction |= comp << 6
        instruction |= jmp
        return instruction


    def _compile_dest(self, comm):
        dest = comm.dest or ''
        if len(dest) != len(set(dest)):
            raise RuntimeError('Invalid dest: lineno: %s' % comm.lineno)

        res = 0
        for reg in dest:
            res |= self._destinations[reg]
        return res


    def _compile_comp(self, comm):
        op = comm.comp[0]
        left = comm.comp[1]
        right = comm.comp[-1]
        arg = left

        if op == 'const':
            op = arg
        elif op == 'val':
            op = arg
        elif op == '!':
            op = f'!{arg}'
        elif op == 'neg':
            op = f'-{arg}'
        elif op == 'inc':
            op = f'{arg}+1'
        elif op == 'dec':
            op = f'{arg}-1'
        elif op == '+':
            op = f'{left}+{right}'
        elif op == '-':
            op = f'{left}-{right}'
        elif op == '&':
            op = f'{left}&{right}'
        elif op == '|':
            op = f'{left}|{right}'
        else:
            raise RuntimeError('Unknown op: lineno: %s' % comm.lineno)

        try:
            if 'M' in op:
                a = 1
                cs = self._ops[op.replace('M', 'A')]
            else:
                a = 0
                cs = self._ops[op]

        except KeyError:
            raise RuntimeError('Invalid comp: lineno: %s' % comm.lineno)

        return (a << 6) | cs


    def _compile_jmp(self, comm):
        if comm.jmp == 'JLE':
            return self._jumps['JLT'] | self._jumps['JEQ']
        if comm.jmp == 'JGE':
            return self._jumps['JGT'] | self._jumps['JEQ']
        if comm.jmp == 'JNE':
            return ~self._jumps['JEQ'] & 0b111
        try:
            return self._jumps[comm.jmp]
        except KeyError:
            raise RuntimeError('Invalid jmp: lineno: %s' % comm.lineno)
