import keywords as kw


class Parser:
    def parse(self, code):
        for lineno, line in enumerate(code.splitlines()):
            line = line.rstrip()
            line = line.split('//', 1)[0]
            line = line.lstrip()
            if not line:
                continue

            command = line.split()
            if command[0] in kw.memory_access_commands:
                try:
                    action, segment, value = command
                    value = int(value)
                    if segment not in kw.memory_segments:
                        raise RuntimeError('Invalid memory segment: lineno %s' % lineno)
                    if action == 'pop' and segment == 'constant':
                        raise RuntimeError('Can not pop to constant: lineno %s' % lineno)

                    max_int16 = (1 << 15) - 1
                    if not 0 <= value <= max_int16:
                        raise RuntimeError('Expected non-negative int16: lineno %s' % lineno)

                    command = [action, segment, value]
                except ValueError:
                    raise RuntimeError('Invalid command: lineno: %s' % lineno)

            elif command[0] in kw.arithmetic_commands:
                if len(command) != 1:
                    raise RuntimeError('Invalid command: lineno: %s' % lineno)

            else:
                raise RuntimeError('Invalid command: lineno: %s' % lineno)

            yield [lineno] + command


    def parse_file(self, path):
        with open(path) as f:
            yield from self.parse(f.read())
