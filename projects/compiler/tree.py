import itertools

class Node:
    def __init__(self, parent, name, value):
        self.parent = parent
        self.name = name
        self.value = value
        self.children = []

        if parent is not None:
            parent.children.append(self)

    def remove(self, child):
        self.children = [c for c in self.children if c != child]

    def print(self):
        def print_node(depth, node):
            print('-' * depth * 4, node.name, node.value)
            for child in node.children:
                print_node(depth + 1, child)
        print_node(0, self)

    def depth(self):
        if self.parent is None:
            return 0
        return 1 + self.parent.depth()


class Visitor:
    def __init__(self, generator=False):
        self._generator = generator

    def visit(self, root):
        handler = getattr(self, 'visit_' + root.name, self.default_visit)
        # print(' ' * root.depth() * 4, root.name, root.value)

        children = (self.visit(child) for child in root.children)
        if self._generator:
            children = itertools.chain.from_iterable(children)
        return handler(root, children)

    def default_visit(self, node, children):
        list(children)
        return node
