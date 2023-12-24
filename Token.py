from enum import Enum

class TokenInfo(Enum):
  EOF             = "EOF"
  ID              = "ID"
  INT_LITERAL     = "INT-LITERAL"
  FLOAT_LITERAL   = "FLOAT-LITERAL"
  ASSIGN          = "ASSIGN '='"
  L               = "L '<'"
  G               = "G '>'"
  EQ              = "EQ '=='"
  PLUS            = "PLUS '+'"
  MINUS           = "MINUS '-'"
  ASTERISK        = "ASTERISK '*'"
  SLASH           = "SLASH '/'"
  PERCENT         = "PERCENT '%'"
  LBR             = "LBR '('"
  RBR             = "RBR ')'"
  LCBR            = "LCBR '{'"
  RCBR            = "RCBR '}'"
  LSBR            = "LSBR '['"
  RSBR            = "RSBR ']'"
  LE              = "LE '<='"
  GE              = "GE '>='"
  COMMA           = "COMMA ','"
  WHILE           = "WHILE"
  BREAK           = "BREAK"
  CONTINUE        = "CONTINUE"
  IF              = "IF"
  PLUS_ASSIGN     = "PLUS-ASSIGN '+='"
  MINUS_ASSIGN    = "MINUS-ASSIGN '-='"
  ASTERISK_ASSIGN = "ASTERISK_ASSIGN '*='"
  SLASH_ASSIGN    = "SLASH_ASSIGN '/='"
  PERCENT_ASSIGN  = "PERCENT_ASSIGN '%='"
  SEMI            = ";"
  ELSE = "ELSE"
  OR = "OR"
  AND = "AND"
  NOT = "NOT"
  FOR = "FOR"
  NEQ = "NEQ"
  DOT = "DOT"

  @staticmethod
  def keywords():
    return {
      'while'     : TokenInfo.WHILE,
      'break'     : TokenInfo.BREAK,
      'continue'  : TokenInfo.CONTINUE,
      'if'        : TokenInfo.IF,
      'else'      : TokenInfo.ELSE,
      'or'        : TokenInfo.OR,
      'and'       : TokenInfo.AND,
      'not'       : TokenInfo.NOT,
      'for'       : TokenInfo.FOR,
    }
  

class Token:
  def __init__(self, token, value, lineno, pos):
    self.token = token
    self.value = value
    self.lineno = lineno
    self.pos = pos
  def __repr__(self):
    return f'<{self.token.value}, {self.value}, ({self.lineno}, {self.pos})>'
  def __str__(self):
    return f'<{self.token.value}, {self.value}>'