from Token import *
from Exceptions import LexerException
import sys

class Lexer:
  def __init__(self, file):
      self.file = file
      self.lineno = 1
      self.pos  = 1
      self.state = None
      self.char = None

  def __getnextchar(self):
      self.char = self.file.read(1)
      self.pos += 1
      if self.char == '\n':
        self.lineno += 1
        self.pos = 1

  def getnexttoken(self):
    match self.state:

      case TokenInfo.G:
        self.__getnextchar()
        if self.char == '=':
          self.state = None
          self.__getnextchar()
          return Token(TokenInfo.GE, ">=", self.lineno, self.pos)
        else:
          self.state = None
          return Token(TokenInfo.G, ">", self.lineno, self.pos)

      case TokenInfo.ASSIGN:
        self.__getnextchar()
        if self.char == '=':
          self.state = None
          self.__getnextchar()
          return Token(TokenInfo.EQ, "==", self.lineno, self.pos)
        else:
          self.state = None
          return Token(TokenInfo.ASSIGN, "=", self.lineno, self.pos)

      case TokenInfo.L:
        self.__getnextchar()
        if self.char == '=':
          self.state = None
          self.__getnextchar()
          return Token(TokenInfo.LE, "<=", self.lineno, self.pos)
        else:
          self.state = None
          return Token(TokenInfo.L, "<", self.lineno, self.pos)

      case TokenInfo.INT_LITERAL:
        int_literal = ""
        while self.char.isdigit():
          int_literal += self.char
          self.__getnextchar()
        if self.char == '.':
          self.state = TokenInfo.FLOAT_LITERAL
          float_literal = int_literal + '.'
          self.__getnextchar()
          while self.char.isdigit():
            float_literal += self.char
            self.__getnextchar()
        if self.char.isalpha() or self.char == '_':
          raise LexerException(f"Wrong identifier in {self.lineno} line, {self.pos} pos")
        if self.state == TokenInfo.INT_LITERAL:
          self.state = None
          return Token(TokenInfo.INT_LITERAL, int_literal, self.lineno, self.pos-1)
        if self.state == TokenInfo.FLOAT_LITERAL:
          self.state = None
          return Token(TokenInfo.FLOAT_LITERAL, float_literal, self.lineno, self.pos-1)

      case TokenInfo.ID:
        id = self.char
        self.__getnextchar()
        while self.char.isalpha() or self.char.isdigit() or self.char == '_':
          id += self.char
          self.__getnextchar()
        self.state = None
        if id in TokenInfo.keywords():
          return Token(TokenInfo.keywords()[id], id, self.lineno, self.pos-1)
        else:
          return Token(TokenInfo.ID, id, self.lineno, self.pos-1)

      case TokenInfo.PLUS:
        self.__getnextchar()
        self.state = None
        if self.char == "=":
          self.__getnextchar()
          return Token(TokenInfo.PLUS_ASSIGN, "+=", self.lineno, self.pos)
        else:
          return Token(TokenInfo.PLUS, "+", self.lineno, self.pos)

      case TokenInfo.MINUS:
        self.__getnextchar()
        self.state = None
        if self.char == "=":
          self.__getnextchar()
          return Token(TokenInfo.MINUS_ASSIGN, "-=", self.lineno, self.pos)
        else:
          return Token(TokenInfo.MINUS, "-", self.lineno, self.pos)

      case TokenInfo.ASTERISK:
        self.__getnextchar()
        self.state = None
        if self.char == "=":
          self.__getnextchar()
          return Token(TokenInfo.ASTERISK_ASSIGN, "*=", self.lineno, self.pos)
        else:
          return Token(TokenInfo.ASTERISK, "*", self.lineno, self.pos)

      case TokenInfo.SLASH:
        self.__getnextchar()
        self.state = None
        if self.char == "=":
          self.__getnextchar()
          return Token(TokenInfo.SLASH_ASSIGN, "/=", self.lineno, self.pos)
        elif self.char == "/":
          self.state = None
          while self.char != "\n":
            self.__getnextchar()
          self.__getnextchar()
          return self.getnexttoken()
        elif self.char == "*":
          self.state = None
          comment_ended = False
          while not comment_ended and self.char != "":
            self.__getnextchar()
            if self.char == "*":
              self.__getnextchar()
              if self.char == "/":
                comment_ended = True
          self.__getnextchar()
          return self.getnexttoken()
          
        else:
          return Token(TokenInfo.SLASH, "/", self.lineno, self.pos)

      case TokenInfo.PERCENT:
        self.__getnextchar()
        self.state = None
        if self.char == "=":
          self.__getnextchar()
          return Token(TokenInfo.PERCENT_ASSIGN, "%=", self.lineno, self.pos)
        else:
          return Token(TokenInfo.PERCENT, "%", self.lineno, self.pos)

      case None:
        if self.char is None:
          self.__getnextchar()
          return self.getnexttoken()
        elif self.char in ["\n", " ", "\t"]:
          self.__getnextchar()
          return self.getnexttoken()
        elif self.char == '':
          return Token(TokenInfo.EOF, "", self.lineno, self.pos)
        elif self.char == '+':
          self.state = TokenInfo.PLUS
          return self.getnexttoken()
        elif self.char == '-':
          self.state = TokenInfo.MINUS
          return self.getnexttoken()
        elif self.char == '*':
          self.state = TokenInfo.ASTERISK
          return self.getnexttoken()
        elif self.char == '%':
          self.__getnextchar()
          return self.getnexttoken()
        elif self.char == '(':
          self.__getnextchar()
          return Token(TokenInfo.LBR, "(", self.lineno, self.pos)
        elif self.char == ')':
          self.__getnextchar()
          return Token(TokenInfo.RBR, ")", self.lineno, self.pos)
        elif self.char == '{':
          self.__getnextchar()
          return Token(TokenInfo.LCBR, "{", self.lineno, self.pos)
        elif self.char == '}':
          self.__getnextchar()
          return Token(TokenInfo.RCBR, "}", self.lineno, self.pos)
        elif self.char == '[':
          self.__getnextchar()
          return Token(TokenInfo.LSBR, "[", self.lineno, self.pos)
        elif self.char == ']':
          self.__getnextchar()
          return Token(TokenInfo.RSBR, "]", self.lineno, self.pos)
        elif self.char == ';':
          self.__getnextchar()
          return Token(TokenInfo.SEMI, ";", self.lineno, self.pos)
        elif self.char == ',':
          self.__getnextchar()
          return Token(TokenInfo.COMMA, ",", self.lineno, self.pos)
        elif self.char == '.':
          self.__getnextchar()
          return Token(TokenInfo.DOT, ".", self.lineno, self.pos)
        elif self.char == '!':
          self.__getnextchar()
          if self.char == '=':
            self.__getnextchar()
            return Token(TokenInfo.NEQ, "!=", self.lineno, self.pos)
          else:
            raise LexerException(f"Expected '=' in {self.lineno} line, {self.pos} pos")
        elif self.char == '/':
          self.state = TokenInfo.SLASH
          return self.getnexttoken()
        elif self.char == '=':
          self.state = TokenInfo.ASSIGN
          return self.getnexttoken()
        elif self.char == '<':
          self.state = TokenInfo.L
          return self.getnexttoken()
        elif self.char == '>':
          self.state = TokenInfo.G
          return self.getnexttoken()
        elif self.char.isalpha() or self.char == '_':
          self.state = TokenInfo.ID
          return self.getnexttoken()
        elif self.char.isdigit():
          self.state = TokenInfo.INT_LITERAL
          return self.getnexttoken()
        
  def print_all_tokens(self, file=sys.stdout):
    token = self.getnexttoken()
    while token.token != TokenInfo.EOF:
      print(token, file=file)
      token = self.getnexttoken()
    print(token, file=file)