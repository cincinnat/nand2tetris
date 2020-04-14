import re

import keywords as kw


class _Ops:
    def __init__(self, filename=None):
        self.filename = filename
        self.function_name = None
        self.__idx = 0

    def __format(self, text):
        lines = filter(bool, map(str.strip, text.split('\n')))

        def enumerate_labels(command):
            # @__XXX__ [// comment]
            if re.match(r'@__[^\s]+__(\s*//.*)?', command):
                return re.sub(r'@__([^s]+)__', fr'@__\1.{self.__idx}__', command)
            # (__XXX__) [// comment]
            if re.match(r'\(__[^\s]+__\)(\s*//.*)?', command):
                return re.sub(r'\(__([^s]+)__\)', fr'(__\1.{self.__idx}__)', command)
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
        op = getattr(self, f'_{op}'.replace('-', '_'))
        return self.__format(op(*args))

    def init_program(self):
        code = f'''
            @256
            D=A
            @SP
            M=D
            {self("call", "Sys.init", 0)}
        '''
        return self.__format(code)

    def _add(self):
        return f'''
            // add
            {self.__move_to_stack_top()}
            D=M
            A=A-1
            M=D+M
            {self.__dec_stack_size()}
        '''

    def _sub(self):
        return f'''
            // sub
            {self.__move_to_stack_top()}
            D=M
            A=A-1
            M=M-D
            {self.__dec_stack_size()}
        '''

    def _neg(self):
        return f'''
            // neg
            {self.__move_to_stack_top()}
            M=-M
        '''

    def _eq(self):
        return f'''
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
        '''

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
        return f'''
            // gt
            {self.__cmp_ne("GT", lt=False)}
        '''

    def _lt(self):
        return f'''
            // lt
            {self.__cmp_ne("LT", lt=True)}
        '''

    def _and(self):
        return f'''
            // and
            {self.__move_to_stack_top()}
            D=M
            A=A-1
            M=D&M
            {self.__dec_stack_size()}
        '''

    def _or(self):
        return f'''
            // or
            {self.__move_to_stack_top()}
            D=M
            A=A-1
            M=D|M
            {self.__dec_stack_size()}
        '''

    def _not(self):
        return f'''
            // not
            {self.__move_to_stack_top()}
            M=!M
        '''

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

        return f'''
            // push
            {read_value}
            {self.__inc_stack_size_and_move_on_top()}
            M=D
        '''

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

    def __label_name(self, name):
        label_name = [self.filename, self.function_name, name]
        label_name = filter(bool, label_name)
        return '$'.join(label_name)

    def _label(self, name):
        return f'''
            ({self.__label_name(name)})
        '''

    def _goto(self, label):
        return f'''
            // goto {label}
            @{self.__label_name(label)}
            0; JMP
        '''

    def _if_goto(self, label):
        return f'''
            // if-goto {label}
            {self.__move_to_stack_top()}
            D=M
            {self.__dec_stack_size()}
            @{self.__label_name(label)}
            D; JNE
        '''

    def _function(self, name, local_size):
        return f'''
            // function {name} {local_size}
            ({name})

            // initialize the local segment with 0s
            @{local_size}
            D=A
            @R13
            M=D

            (__FN_ZERO_LOCAL__)  // while D > 0
            @__FN_START__
            D; JEQ  // D = R13
            {self.__inc_stack_size_and_move_on_top()}
            M=0
            @R13
            M=M-1
            D=M
            @__FN_ZERO_LOCAL__
            0; JMP

            (__FN_START__)
        '''

    def _return(self):
        def restore(ptr):
            return f'''
                // *{ptr} = *(--LCL)
                @LCL
                M=M-1
                A=M
                D=M
                @{ptr}
                M=D
            '''

        return f'''
            // return
            @5
            D=A
            @LCL
            A=M-D
            D=M
            @R13      // 1. set R13 = return address (= *(LCL-5))
            M=D

            {self.__move_to_stack_top()}
            D=M
            @ARG
            A=M
            M=D      // 2. set ARG[0] = return value

            @ARG
            D=M+1
            @SP
            M=D      // 3. set SP = ARG + 1

            // 4. set THAT = *(LCL - 1)
            {restore("THAT")}
            // 5. set THIS = *(LCL - 2)
            {restore("THIS")}
            // 6. set ARG = *(LCL - 3)
            {restore("ARG")}
            // 7. set LCL = *(LCL - 3)
            {restore("LCL")}

            @R13
            A=M      // 8. goto return address
            0; JMP
        '''

    def _call(self, function, n_args):
        i = self.__idx
        self.__idx += 1

        def push(ptr):
            return f'''
                @{ptr}
                D=M
                {self.__inc_stack_size_and_move_on_top()}
                M=D
            '''

        return f'''
            // call {function} {n_args}
            @{function}$ret.{i}
            D=A
            {self.__inc_stack_size_and_move_on_top()}
            M=D      // 1. push return address

            // 2. push LCL
            {push("LCL")}
            // 3. push ARG
            {push("ARG")}
            // 4. push THIS
            {push("THIS")}
            // 5. push THAT
            {push("THAT")}

            @SP
            D=M
            @{n_args}
            D=D-A
            @5
            D=D-A
            @ARG
            M=D      // 6. ARG = SP - n_args - 5

            @SP
            D=M
            @LCL
            M=D      // 7. LCL = SP

            @{function}
            0; JMP   // 8. goto function
            ({function}$ret.{i})
        '''


class CodeGenerator:
    def __init__(self):
        self.__ops = _Ops()

    def translate(self, filename, commands):
        code_blocks = self.itranslate(filename, commands)
        code = '\n'.join(code_blocks)
        return code

    def itranslate(self, filename, commands):
        # commands = [(lineno, *command)]

        self.__ops.filename = filename
        commands = self.__detect_functions(commands)
        for function_name, command in commands:
            self.__ops.function_name = function_name
            yield self.__ops(*command[1:])

    def __detect_functions(self, commands):
        command_buffer = []
        def command_iterator(commands):
            for command in commands:
                yield command
                while command_buffer:
                    yield command_buffer.pop()
            while True:
                if command_buffer:
                    while command_buffer:
                        yield command_buffer.pop()
                else:
                    yield None

        def find_body_size(command_list):
            for i, command in enumerate(reversed(command_list)):
                # (lineno, return)
                if command[1] == 'return':
                    return len(command_list) - i
            return len(command_list)

        def get_function_body(it):
            body = []
            for command in it:
                if command is None:
                    break
                if command[1] == 'function':
                    command_buffer.append(command)
                    break
                body.append(command)

            i = find_body_size(body)
            command_buffer.extend(body[i:])
            return body[:i]

        it = command_iterator(commands)
        for command in it:
            if command is None:
                break
            assert len(command) > 1, command
            if command[1] == 'function':
                # (lineno, function, <name>, <nargs>)
                function_name = command[2]
                body = get_function_body(it)

                yield function_name, command
                for item in body:
                    yield function_name, item
            else:
                yield None, command

    def gen_initializer(self):
        return self.__ops.init_program()
