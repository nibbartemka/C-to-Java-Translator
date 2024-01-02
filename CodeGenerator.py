class CodeGenerator:
  def __init__(self, node, exclude_nodes=None):
    self.node = node
    self.exclude_nodes = exclude_nodes
  def __str__(self):
    return f'{self.node._generate_text(self.exclude_nodes)}'