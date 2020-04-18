import string


symbols = set('{}()[].,;+-*/&|<>=~')

keywords = {'class', 'constructor', 'function', 'method',
    'field', 'static', 'var', 'int', 'char', 'boolean', 'void',
    'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else',
    'while', 'return'}


class Token:
    def __init__(self, lineno, tokentype, value):
        self.lineno = lineno
        self.type = tokentype
        self.value = value

    def __str__(self):
        return str(self.value)


class TokenizerError(RuntimeError):
    pass


class Tokenizer:
    def tokenize(self, fobj_or_path):
        if isinstance(fobj_or_path, str):
            with open(fobj_or_path) as f:
                yield from self._tokenize(f)
        else:
            yield from self._tokenize(fobj_or_path)


    def _tokenize(self, fobj):
        token = []

        def make_token(lineno):
            t = self._make_token(lineno, ''.join(token))
            token.clear()
            return t

        def ignore_token():
            token.clear()

        last_lieno = None
        for lineno, ch in self._read(fobj):
            #
            # comments
            #
            if ch == '/' and not token:  # maybe comment
                token.append(ch)

            # single line comment (aka //)
            elif ch == '/' and token == ['/']:
                token.append(ch)
            elif token[:2] == ['/', '/']:
                if ch == '\n':
                    ignore_token()
                else:
                    token.append(ch)

            # multiline comment
            elif ch == '*' and token == ['/']:
                token.append(ch)
            elif token[:2] == ['/', '*']:
                token.append(ch)
                if token[-2:] == ['*', '/']:
                    ignore_token()

            #
            # string constant
            #
            elif ch == '"':
                if not token:
                    token.append(ch)
                elif token[0] == '"':
                    token.append(ch)
                    yield make_token(lineno)
                else:
                    # an identifier followed by '"',
                    # let the analyser handle this
                    yield make_token(lineno)
                    token.append(ch)

            elif token and token[0] == '"':
                token.append(ch)
                if ch == '\n':
                    # this will raise an error
                    yield make_token(lineno)

            #
            # other
            #
            elif ch in string.whitespace:
                if token:
                    yield make_token(lineno)

            elif ch in symbols:
                if token:
                    yield make_token(lineno)
                token.append(ch)
                yield make_token(lineno)

            else:
                token.append(ch)

            last_lieno = lineno

        if token:
            yield make_token(last_lieno)
        yield make_token(None)


    def _make_token(self, lineno, token):
        if lineno is None:
            assert not token
            return Token(None, 'EOF', 'EOF')
        assert token

        if len(token) == 1 and token[0] in symbols:
            return Token(lineno, 'symbol', token)

        if token[0] in string.digits:
            try:
                return Token(lineno, 'int_const', int(token))
            except ValueError:
                raise TokenizerError('not an integer: lineno %s' % lineno)

        if token[0] == '"' or token[-1] == '"':
            if token[0] != token[-1] or len(token) == 1:
                raise TokenizerError('malformed string: lineno %s' % lineno)
            return Token(lineno, 'string_const', token)

        if token in keywords:
            return Token(lineno, 'keyword', token)

        return Token(lineno, 'identifier', token)


    def _read(self, fobj):
        for lineno, line in enumerate(fobj, start=1):
            for ch in line:
                yield lineno, ch
