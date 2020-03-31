import os

import keywords as kw


class _Ops:
    def __init__(self, filename, resolve_contants=False):
        self.filename = filename
        self.resolve_contants = resolve_contants
        self.__idx = 0

    def __strip(self, text):
        lines = filter(bool, map(str.strip, text.split('\n')))

        def resolve_contants(command):
            if command.startswith('@'):
                val = command[1:]
                val = kw.constants.get(val, val)
                return f'@{val}'
            return command
        if self.resolve_contants:
            lines = map(resolve_contants)

        def enumerate_labels(command):
            if command.startswith('@__'):  # @__XXX__
                assert command.endswith('__'), command
                return f'{command}.{self.__idx}'
            if command.startswith('('):    # (__XXX__)
                assert command.endswith('__)'), command
                return f'({command[1:-1]}.{self.__idx})'
            return command
        lines = map(enumerate_labels, lines)

        return '\n'.join(lines)

    def __move_to_stack_top(self):
        return f'''
            @SP
            A=M-1
        '''

    def __dec_stack_size(self):
        return f'''
            @SP
            M=M-1
        '''

    def __dec_stack_size_and_move_on_top(self):
        return f'''
            @SP
            M=M-1
            A=M-1
        '''

    def __inc_stack_size_and_move_on_top(self):
        return f'''
            @SP
            M=M+1
            A=M-1
        '''

    def __call__(self, op, *args):
        self.__idx += 1
        op = getattr(self, f'_{op}')
        return op(*args)

    def _add(self):
        return self.__strip(f'''
            // add
            {self.__move_to_stack_top()}
            D=M
            A=A-1
            M=D+M
            {self.__dec_stack_size()}
        ''')

    def _sub(self):
        return self.__strip(f'''
            // sub
            {self.__move_to_stack_top()}
            D=M
            A=A-1
            M=M-D
            {self.__dec_stack_size()}
        ''')

    def _neg(self):
        return self.__strip(f'''
            // neg
            {self.__move_to_stack_top()}
            M=-M
        ''')

    def _eq(self):
        return self.__strip(f'''
            // eq
            {self.__move_to_stack_top()}
            D=M
            A=A-1
            D=D-M
            @__EQ_TRUE__
            D; JEQ
            D=0
            @__EQ_END__
            0; JMP
            (__EQ_TRUE__)
            D=-1
            (__EQ_END__)
            {self.__dec_stack_size_and_move_on_top()}
            M=D
        ''')

    def __cmp_ne(self, prefix, lt=True):
        return f'''
            {self.__move_to_stack_top()}
            D=M
            @__{prefix}_NEG_Y__
            D; JLT

            // y >= 0
            {self.__move_to_stack_top()}
            A=A-1
            D=M
            @__{prefix}_CHECK_DIFF__
            D; JGE

            // x < 0 & y >= 0
            @__{prefix}_{"TRUE" if lt else "FALSE"}__
            0; JMP
            
            (__{prefix}_FALSE__)
            D=0
            @__{prefix}_END__
            0; JMP

            (__{prefix}_NEG_Y__)
            // y < 0
            {self.__move_to_stack_top()}
            A=A-1
            D=M
            @__{prefix}_CHECK_DIFF__
            D; JLT

            // x >= 0 & y < 0
            @__{prefix}_{"FALSE" if lt else "TRUE"}__
            0; JMP

            (__{prefix}_TRUE__)
            D=-1
            @__{prefix}_END__
            0; JMP

            (__{prefix}_CHECK_DIFF__)
            // D=x; (x < 0 & y < 0) | (x >= 0 | y >= 0)
            {self.__move_to_stack_top()}
            D=D-M
            @__{prefix}_TRUE__
            D; {"JLT" if lt else "JGT"}
            @__{prefix}_FALSE__
            0; JMP

            (__{prefix}_END__)
            {self.__dec_stack_size_and_move_on_top()}
            M=D
        '''

    def _gt(self):
        return self.__strip(f'''
            // gt
            {self.__cmp_ne("GT", lt=False)}
        ''')

    def _lt(self):
        return self.__strip(f'''
            // lt
            {self.__cmp_ne("LT", lt=True)}
        ''')

    def _and(self):
        return self.__strip(f'''
            // and
            {self.__move_to_stack_top()}
            D=M
            A=A-1
            M=D&M
            {self.__dec_stack_size()}
        ''')

    def _or(self):
        return self.__strip(f'''
            // or
            {self.__move_to_stack_top()}
            D=M
            A=A-1
            M=D|M
            {self.__dec_stack_size()}
        ''')

    def _not(self):
        return self.__strip(f'''
            // not
            {self.__move_to_stack_top()}
            M=!M
        ''')

    def _push(self, segment, value):
        if segment == 'static':
            read_value = f'''
                @{self.filename}.{value}
                D=M
            '''
        elif segment == 'constant':
            read_value = f'''
                @{value}
                D=A
            '''
        elif segment in kw.segment_pointers:
            read_value = f'''
                @{value}
                D=A
                @{kw.segment_pointers[segment]}
                A=D+M
                D=M
            '''
        elif segment in kw.special_segmnets:
            read_value = f'''
                @{value}
                D=A
                @{kw.special_segmnets[segment]}
                A=A+D
                D=M
            '''
        else:
            raise NotImplementedError(f'push {segment}')

        return self.__strip(f'''
            // push
            {read_value}
            {self.__inc_stack_size_and_move_on_top()}
            M=D
        ''')

    def _pop(self, segment, value):
        assert segment != 'constant'

        if segment == 'static':
            return f'''
                {self.__move_to_stack_top()}
                D=M
                {self.__dec_stack_size()}
                @{self.filename}.{value}
                M=D
            '''

        if segment in kw.segment_pointers:
            compute_address = f'''
                @{kw.segment_pointers[segment]}
                D=M
                @{value}
                D=D+A
            '''
        elif segment in kw.special_segmnets:
            compute_address = f'''
                @{value}
                D=A
                @{kw.special_segmnets[segment]}
                A=D+A
                D=A
            '''
        else:
            raise NotImplementedError(f'pop {segment}')

        assert segment in {**kw.segment_pointers, **kw.special_segmnets}
        return f'''
            {compute_address}
            @R13
            M=D
            {self.__move_to_stack_top()}
            D=M
            {self.__dec_stack_size()}
            @R13
            A=M
            M=D
        '''


class CodeGenerator:
    def translate(self, commands, output, dry_run=False):
        filename = os.path.splitext(os.path.basename(output))[0]
        code_blocks = self._traslate(filename, commands)
        code = '\n'.join(code_blocks)

        if not dry_run:
            with open(output, 'wt') as f:
                f.write(code)
        return code

    def _traslate(self, filename, commands):
        ops = _Ops(filename)
        # [(lineno, command...)]
        for command in commands:
            yield ops(*command[1:])
