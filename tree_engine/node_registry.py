class NodeRegistry:
    def __init__(self):
        self.nodes = {}

    def register(self, node):
        self.nodes[node.name] = node

    def get(self, name):
        return self.nodes.get(name)
