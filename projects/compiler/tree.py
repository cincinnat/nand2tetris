
class Node:
    def __init__(self, parent, name, value):
        self.parent = parent
        self.name = name
        self.value = value
        self.children = []

        if parent is not None:
            parent.children.append(self)

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


def visit(root, visitor):
    return visitor(root, (visit(child, visitor) for child in root.children))


class Visitor:
    def visit(self, root):
        handler = getattr(self, 'visit_' + root.name, self.defatul_visit)
        handler(root, (self.visit(child) for child in root.children))

    def defatul_visit(self, node, children):
        list(children)
        return node
