import os

from jack_tokenizer import Tokenizer
from jack_analyzer import Analyzer
from tree import Visitor
import utils

def write_tokens(tokens, path):
    def write(f, token_type, value):
        f.write(f'<{token_type}> {value} </{token_type}>\n')

    with open(path, 'wt') as f:
        f.write(f'<tokens>\n')
        for token in tokens:
            if token.type == 'EOF':
                pass
            elif token.type == 'int_const':
                write(f, 'integerConstant', token.value)
            elif token.type == 'string_const':
                write(f, 'stringConstant', token.value[1:-1])
            elif token.type == 'symbol':
                write(f, token.type, utils.xml_symbol(token.value))
            else:
                write(f, token.type, token.value)
            yield token
        f.write(f'</tokens>\n')


class XMLgenerator(Visitor):
    def __init__(self, fobj):
        self.fobj = fobj
        self._depth = 0

    def visit_start(self, node, children):
        list(children)

    def _visit(self, node, name, value, children):
        indent = ' ' * self._depth * 4
        self._depth += 1

        name = name.split('_')
        name = [name[0]] + [t.capitalize() for t in name[1:]]
        name = ''.join(name)

        if not node.children and value is not None:
            self.fobj.write(f'{indent}<{name}> {value} </{name}>\n')
        else:
            self.fobj.write(f'{indent}<{name}>\n')
            list(children)
            self.fobj.write(f'{indent}</{name}>\n')

        self._depth -= 1

    def visit_class_dec(self, node, children):
        self._visit(node, 'class', None, children)

    def visit_int_const(self, node, children):
        self._visit(node, 'integerConstant', node.value, None)

    def visit_string_const(self, node, children):
        assert node.value[0] == node.value[-1] == '"'
        self._visit(node, 'stringConstant', node.value[1:-1], None)

    def visit_symbol(self, node, children):
        self._visit(node, node.name, utils.xml_symbol(node.value), None)

    def defatul_visit(self, node, children):
        self._visit(node, node.name, node.value, children)


class Parser:
    def parse(self, input_file):
        tokenizer_ouput = os.path.splitext(input_file)[0] + 'T.xml'
        analyzer_ouput = os.path.splitext(input_file)[0] + '.xml'

        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize(input_file)

        tokens = write_tokens(tokens, tokenizer_ouput)

        analyzer = Analyzer()
        tree = analyzer.start(tokens)

        with open(analyzer_ouput, 'w') as f:
            visitor = XMLgenerator(f)
            visitor.visit(tree)
