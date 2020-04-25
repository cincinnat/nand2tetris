import collections
import itertools
import os

from jack_tokenizer import Tokenizer
from jack_analyzer import Analyzer, statements
from tree import Visitor

binary_ops = {
    '+': 'add',
    '-': 'sub',
    '*': 'call Math.multiply 2',
    '/': 'call Math.divide 2',
    '&': 'and',
    '|': 'or',
    '<': 'lt',
    '>': 'gt',
    '=': 'eq',
}

unary_ops = {
    '-': 'neg',
    '~': 'not',
}


# TODO: empty visitor decorator
# TODO: class-wide `chained` generator instead fo `generator=True`


class SymbolTable:
    Variable = collections.namedtuple('Variable', ['kind', 'type', 'name', 'no'])

    def __init__(self):
        self._data = dict()

    def clear(self):
        self._data.clear()

    def add(self, kind, typename, name):
        assert name not in self
        self._data[name] = self.Variable(
            kind, typename, name, self.count(kind))

    def count(self, kind):
        return sum(v.kind == kind for v in self._data.values())

    def __contains__(self, name):
        return name in self._data

    def __getitem__(self, name):
        return self._data[name]

    def __len__(self):
        return len(self._data)


class CodeGenerator(Visitor):
    def __init__(self):
        super().__init__(generator=True)

        self._class_name = None
        self._global = SymbolTable()
        self._local = SymbolTable()

        self._function_kind = None
        self._return_type = None
        self._function_name = None

    def visit_start(self, node, children):
        assert not self._global
        yield from children
        self._global.clear()

    def visit_class_dec(self, node, children):
        self._keyword('class', children)
        assert self._class_name is None
        self._class_name = self._identifier(children)

        yield f'// {self._class_name}'
        yield from children
        yield f'// ~{self._class_name}'

        self._class_name = None

    def visit_class_var_dec(self, node, children):
        kind = self._keyword(['static', 'field'], children)
        typename = self._identifier_or_keyword(children)

        for node_name, varname in children:
            assert node_name == 'identifier'
            self._global.add(kind, typename, varname)
        yield from itertools.chain.from_iterable(children)

    def visit_subroutine_dec(self, node, children):
        assert self._class_name is not None
        assert not self._local
        assert self._function_kind is None
        assert self._return_type is None
        assert self._function_name is None

        kind = self._keyword(['function', 'method', 'constructor'], children)
        self._function_kind = kind
        self._return_type = self._identifier_or_keyword(children)
        self._function_name = self._identifier(children)

        yield from children

        self._local.clear()
        self._function_kind = None
        self._return_type = None
        self._function_name = None

    def visit_parameter_list(self, node, children):
        if self._function_kind == 'method':
            self._local.add('argument', self._class_name, 'this')
        for node_name, typename in children:
            assert node_name in ['keyword', 'identifier']
            varname = self._identifier(children)
            self._local.add('argument', typename, varname)
        yield from children

    def visit_var_dec(self, node, children):
        self._keyword('var', children)
        typename = self._identifier_or_keyword(children)
        for node_name, varname in children:
            assert node_name == 'identifier'
            self._local.add('local', typename, varname)
        yield from children

    def visit_subroutine_body_statements(self, node, children):
        n_fields = self._global.count('field')
        n_locals = self._local.count('local')

        yield f'// {self._function_kind}'
        yield f'function {self._class_name}.{self._function_name} {n_locals}'
        if self._function_kind == 'constructor':
            yield f'push constant {max(1, n_fields)}  // sizeof({self._class_name})'
            yield f'call Memory.alloc 1'
            yield f'pop pointer 0'
        elif self._function_kind == 'method':
            yield f'push argument 0  // this'
            yield f'pop pointer 0'

        yield from children

    def visit_symbol(self, node, children):
        if node.value == '=' and 'assignment' in node.parent.name:
            pass
        elif node.value in binary_ops or node.value in unary_ops:
            yield 'symbol', node.value

    def visit_keyword(self, node, children):
        if node.value not in statements + ['else']:
            yield 'keyword', node.value

    def visit_identifier(self, node, children):
        yield 'identifier', node.value

    def default_visit(self, node, children):
        yield from children

    def _get_var(self, name):
        if name in self._local:
            return self._local[name]
        return self._global[name]

    def _get_segment(self, var):
        if var.kind == 'field':
            return 'this'
        return var.kind

    def visit_let_statement(self, node, children):
        yield f'// let'
        yield from children
        yield f'// ~let'

    def visit_assignment(self, node, children):
        dest = self._identifier(children)
        var = self._get_var(dest)
        yield from children
        yield f'pop {self._get_segment(var)} {var.no}  // {var.name}'

    def visit_array_assignment(self, node, children):
        dest = self._identifier(children)
        var = self._get_var(dest)
        yield f'push {self._get_segment(var)} {var.no}  // {var.name}'
        yield from children
        yield 'pop temp 0'
        yield 'pop pointer 1'
        yield 'push temp 0'
        yield 'pop that 0'

    def visit_index_expression(self, node, children):
        yield from children
        yield 'add  // *arr + index'

    def visit_do_statement(self, node, children):
        yield f'// do'
        yield from children
        yield f'pop temp 0  // ignore returned value'
        yield f'// ~do'

    def visit_subroutine_call(self, node, children):
        nargs = 0

        if self._this_method_call(node):
            # do <fn>(...)
            class_or_var_name = self._class_name
            method = self._identifier(children)
        else:
            # do <class_or_var_name>.<fn>(...)
            class_or_var_name = self._identifier(children)
            method = self._identifier(children)

        try:
            var = self._get_var(class_or_var_name)
            var_type = var.type
            yield f'push {self._get_segment(var)} {var.no}  // *{class_or_var_name}'
            nargs += 1
        except KeyError:
            # class_or_var_name is a class name
            var_type = class_or_var_name
            if self._get_function_type(node, method) == 'method':
                yield f'push pointer 0'
                nargs += 1

        yield from children
        nargs += self._count_call_args(node)
        yield f'call {var_type}.{method} {nargs}'

    def _get_function_type(self, node, method):
        class FuncVisitor(Visitor):
            def visit_subroutine_dec(self, node, children):
                if node.children[2].value == method:
                    return node.children[0].value
                return None

            def default_visit(self, node, children):
                value = filter(bool, children)
                return next(value, None)

        root = node
        while root.parent is not None:
            root = root.parent
        return FuncVisitor().visit(root)

    def _this_method_call(self, node):
        tokens = 0
        for child in node.children:
            if child.name == 'expression_list':
                break
            if child.name == 'identifier':
                tokens += 1

        assert tokens in [1, 2]  # class_or_var_name.method or just method
        return tokens == 1

    def _count_call_args(self, node):
        expression_list = next(filter(
            lambda c: c.name == 'expression_list', node.children))
        if expression_list.children:
            return 1 + sum(c.value == ',' for c in expression_list.children)
        return 0

    def visit_array_access(self, node, children):
        arr = self._identifier(children)
        var = self._get_var(arr)
        segment = self._get_segment(var)
        yield f'push {segment} {var.no}  // *{var.name}'
        yield from children
        yield f'add  // *{var.name}[expr]'
        yield f'pop pointer 1'
        yield f'push that 0'

    def visit_if_statement(self, node, children):
        yield f'// if-{id(node)}'
        yield from children
        yield f'label end-if-{id(node)}'

    def visit_if_condition(self, node, children):
        yield from children
        yield f'if-goto if-{id(node.parent)}'
        yield f'goto else-{id(node.parent)}'

    def visit_if_body(self, node, children):
        yield f'label if-{id(node.parent)}'
        yield from children
        yield f'goto end-if-{id(node.parent)}'

    def visit_else_body(self, node, children):
        yield f'label else-{id(node.parent)}'
        yield from children

    def visit_while_statement(self, node, children):
        yield f'// while-{id(node)}'
        yield from children

    def visit_while_condition(self, node, children):
        yield f'label while-condition-{id(node.parent)}'
        yield from children
        yield f'if-goto while-begin-{id(node.parent)}'
        yield f'goto while-end-{id(node.parent)}'

    def visit_while_body(self, node, children):
        yield f'label while-begin-{id(node.parent)}'
        yield from children
        yield f'goto while-condition-{id(node.parent)}'
        yield f'label while-end-{id(node.parent)}'

    def visit_term(self, node, children):
        if len(node.children) > 1:
            yield from children
        elif node.children[0].value == 'this':
            yield 'push pointer 0  // this'
        elif node.children[0].value == 'null':
            yield 'push constant 0  // null'
        elif node.children[0].value == 'true':
            yield 'push constant 1'
            yield 'neg'
        elif node.children[0].value == 'false':
            yield 'push constant 0'
        elif node.children[0].name == 'int_const':
            yield f'push constant {abs(node.children[0].value)}'
            if node.children[0].value < 0:
                yield 'neg'
        elif node.children[0].name == 'string_const':
            yield f'push constant {len(node.children[0].value[1:-1])}'
            yield f'call String.new 1'
            for ch in node.children[0].value[1:-1]:  # without the surrounding quotes
                yield f'push constant {ord(ch)}'
                yield f'call String.appendChar 2'
        elif node.children[0].name == 'identifier':
            var = self._get_var(node.children[0].value)
            yield f'push {self._get_segment(var)} {var.no}  // {var.name}'
        else:
            # if, do, while statements, etc.
            yield from children

    def visit_binary_op(self, node, children):
        op = self._symbol(children)
        yield from children
        yield binary_ops[op]

    def visit_unary_op(self, node, children):
        op = self._symbol(children)
        yield from children
        yield unary_ops[op]

    def visit_return_statement(self, node, children):
        expression = list(children)
        yield '// return'
        if expression:
            assert self._return_type != 'void'
            yield from expression
            yield 'return'
        else:
            assert self._return_type == 'void'
            yield 'push constant 0'
            yield 'return'

    def _symbol(self, children):
        name, value = next(children)
        assert name == 'symbol'
        return value

    def _keyword(self, values, children):
        if isinstance(values, str):
            values = [values]

        name, value = next(children)
        assert name == 'keyword'
        assert value in values
        return value

    def _identifier(self, children):
        name, value = next(children)
        assert name == 'identifier'
        return value

    def _identifier_or_keyword(self, children):
        name, value = next(children)
        assert name in ['keyword', 'identifier']
        return value


class Compiler:
    def compile(self, path, output_file=None):
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize(path)

        analyzer = Analyzer()
        tree = analyzer.start(tokens)

        cg = CodeGenerator()
        code = cg.visit(tree)
        if output_file is not None:
            with open(output_file, 'wt') as f:
                for cmd in code:
                    f.write('%s\n' % cmd)
        else:
            return code
