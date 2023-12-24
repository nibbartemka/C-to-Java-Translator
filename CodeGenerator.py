class CodeGenerator:
  def __init__(self, node):
    self.node = node
  def __str__(self):
    return f'{self.node._generate_text()}'