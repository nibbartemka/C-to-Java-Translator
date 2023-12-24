class LexerException(Exception):
  def __init__(self, text):
    super().__init__(f'Lexer Exception: {text}')

class ParserException(Exception):
  def __init__(self, text):
    super().__init__(f'Parser Exception: {text}')

class SemanticAnalyzerException(Exception):
  def __init__(self, text):
    super().__init__(f'Semantic Analyzer Exception: {text}')