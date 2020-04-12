import keywords as kw


class Parser:
    def __parse_command(self, lineno, command):
        if command[0] in kw.memory_access_commands:
            action, segment, value = command
            value = int(value)
            if segment not in kw.memory_segments:
                raise RuntimeError('invalid memory segment')
            if action == 'pop' and segment == 'constant':
                raise RuntimeError('can not pop to the constant segment')

            max_int16 = (1 << 15) - 1
            if not 0 <= value <= max_int16:
                raise RuntimeError('expected non-negative int16')

            command = [action, segment, value]

        elif command[0] in kw.arithmetic_commands:
            assert len(command) == 1

        elif command[0] in kw.branching_commands:
            assert len(command) == 2

        elif command[0] in kw.function_commands:
            if command[0] == 'return':
                assert len(command) == 1
            else:
                assert len(command) == 3
                command[-1] = int(command[-1])

        else:
            raise RuntimeError('unknown command')

        return [lineno] + command


    def parse(self, code):
        for lineno, line in enumerate(code.splitlines()):
            line = line.rstrip()
            line = line.split('//', 1)[0]
            line = line.lstrip()
            if not line:
                continue

            command = line.split()
            try:
                yield self.__parse_command(lineno, command)
            except Exception as e:
                raise RuntimeError('lineno: %s: %s' % (lineno, e))


    def parse_file(self, path):
        with open(path) as f:
            yield from self.parse(f.read())
