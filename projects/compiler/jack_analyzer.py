from tree import Node


class AnalyzerError(RuntimeError):
    pass


type_names = ['int', 'boolean', 'char']
statements = ['let', 'do', 'if', 'while', 'return']
constants = ['true', 'false', 'this', 'null']
unary_ops = list('-~')
binary_ops = list('+-*/&|<>=')


class Analyzer:
    def __init__(self):
        self._token = None
        self._tokens = None

        self._tree = None
        self._cur = None

    class _node:
        def __init__(self, terminal=False, inline=False):
            self.inline = inline
            self.terminal = terminal

        def _create_node(self, analyzer, name):
            analyzer._cur = Node(analyzer._cur, name,
                analyzer._token.value if self.terminal else None)
            if analyzer._tree is None:
                analyzer._tree = analyzer._cur

        def __call__(self, fn):
            def wrapper(analyzer, *args, **kwargs):
                if not self.inline:
                    tmp = analyzer._cur
                    self._create_node(analyzer, fn.__name__)
                res = fn(analyzer, *args, **kwargs)
                if not self.inline:
                    analyzer._cur = tmp
                return res

            return wrapper

    @_node()
    def start(self, tokens, entry_point=None):
        self._tokens = tokens
        self._token = next(self._tokens)

        if entry_point is None:
            self.class_dec()
        else:
            entry_point()

        if self._token.value != 'EOF':
            raise AnalyzerError('expect EOF')
        # exhaust the generator
        assert next(tokens, None) is None

        tree = self._tree
        self._cur = None
        self._tree = None
        return tree

    @_node()
    def class_dec(self):
        self._expect('class')
        self.class_name()
        self._expect('{')
        self.class_var_decs()
        self.subroutine_decs()
        self._expect('}')

    @_node(inline=True)
    def class_name(self):
        self.identifier()

    @_node(terminal=True)
    def identifier(self):
        assert self._token.type == 'identifier'
        self._next()

    @_node(inline=True)
    def class_var_decs(self):
        while self._token.value in {'static', 'field'}:
            self.class_var_dec()

    @_node()
    def class_var_dec(self):
        self._expect('static', 'field')
        self.type_name()
        self.var_names()
        self._expect(';')

    @_node(inline=True)
    def type_name(self):
        if not self._accept(*type_names):
            self.identifier()

    @_node(inline=True)
    def var_names(self):
        self.var_name()
        while self._accept(','):
            self.var_name()

    @_node(inline=True)
    def var_name(self):
        self.identifier()

    @_node(inline=True)
    def subroutine_decs(self):
        while self._token.value in {'constructor', 'function', 'method'}:
            self.subroutine_dec()

    @_node()
    def subroutine_dec(self):
        self._expect('constructor', 'function', 'method')
        if self._accept('void'):
            pass
        else:
            self.type_name()
        self.subroutine_name()
        self._expect('(')
        self.parameter_list()
        self._expect(')')
        self.subroutine_body()

    @_node()
    def parameter_list(self):
        def accept_parameter():
            if self._token.value in type_names:
                self.type_name()
                self.var_name()
            elif self._token.type == 'identifier':
                self.identifier()
                self.var_name()

        accept_parameter()
        while self._accept(','):
            accept_parameter()

    @_node()
    def subroutine_body(self):
        self._expect('{')
        self.var_decs()
        self.statements()
        self._expect('}')

    @_node(inline=True)
    def var_decs(self):
        while self._token.value == 'var':
            self.var_dec()

    @_node()
    def var_dec(self):
        self._expect('var')
        self.type_name()
        self.var_names()
        self._expect(';')

    @_node()
    def statements(self):
        while self._token.value in statements:
            self.statement()

    @_node(inline=True)
    def statement(self):
        if self._token.value == 'let':
            self.let_statement()
        elif self._token.value == 'do':
            self.do_statement()
        elif self._token.value == 'if':
            self.if_statement()
        elif self._token.value == 'while':
            self.while_statement()
        else:
            self.return_statement()

    @_node()
    def let_statement(self):
        self._expect('let')
        self.var_name()
        if self._accept('['):
            self.expression()
            self._expect(']')
        self._expect('=')
        self.expression()
        self._expect(';')

    @_node()
    def expression(self):
        self.term()
        while self._token.value in binary_ops:
            self.binary_op()
            self.term()


    @_node()
    def term(self):
        if self._token.type == 'int_const':
            self.int_const()
        elif self._token.type == 'string_const':
            self.string_const()
        elif self._token.value in constants:
            self.constant()
        elif self._token.type == 'identifier':
            self.identifier()
            if self._accept('.'):
                self.subroutine_call()
            elif self._accept('['):
                if not self._accept(']'):
                    self.expression()
                    self._expect(']')
        elif self._accept('('):
            self.expression()
            self._expect(')')
        else:
            self.unary_op()
            self.term()

    @_node(inline=True)
    def constant(self):
        self._expect(*constants)

    @_node(terminal=True)
    def int_const(self):
        self._next()

    @_node(terminal=True)
    def string_const(self):
        self._next()

    @_node(inline=True)
    def unary_op(self):
        self._expect(*unary_ops)

    @_node(inline=True)
    def binary_op(self):
        self._expect(*binary_ops)

    @_node()
    def do_statement(self):
        self._expect('do')
        self.subroutine_call()
        self._expect(';')

    @_node(inline=True)
    def subroutine_call(self):
        self.identifier()
        while self._accept('.'):
            self.identifier()
        self._expect('(')
        self.expression_list()
        self._expect(')')

    @_node()
    def expression_list(self):
        def is_term():
            ttype = self._token.type
            tvalue = self._token.value
            return (tvalue in constants
                or tvalue == '('
                or tvalue in unary_ops
                or ttype == 'int_const'
                or ttype == 'string_const'
                or ttype == 'identifier')

        if is_term():
            self.expression()
            while self._accept(','):
                self.expression()

    @_node()
    def if_statement(self):
        self._expect('if')
        self._expect('(')
        self.expression()
        self._expect(')')
        self._expect('{')
        self.statements()
        self._expect('}')
        if self._accept('else'):
            self._expect('{')
            self.statements()
            self._expect('}')

    @_node()
    def while_statement(self):
        self._expect('while')
        self._expect('(')
        self.expression()
        self._expect(')')
        self._expect('{')
        self.statements()
        self._expect('}')

    @_node()
    def return_statement(self):
        self._expect('return')
        if not self._accept(';'):
            self.expression()
            self._expect(';')

    @_node(inline=True)
    def subroutine_name(self):
        self.identifier()

    def _expect(self, *args):
        if self._token.value not in args:
            raise AnalyzerError('lineno: %s: expect %s'
                % (self._token.lineno, args))
        self._consume()

    def _accept(self, *args):
        if self._token.value in args:
            self._consume()
            return True
        return False

    def _consume(self):
        if self._token.type == 'keyword':
            self.keyword()
        else:
            assert self._token.type == 'symbol', self._token.type
            self.symbol()

    @_node(terminal=True)
    def keyword(self):
        assert self._token.type == 'keyword', self._token.type
        self._next()

    @_node(terminal=True)
    def symbol(self):
        assert self._token.type == 'symbol', self._token.type
        self._next()

    def _next(self):
        try:
            self._token = next(self._tokens)
        except StopIteration:
            raise AnalyzerError('unexpected end of file')
