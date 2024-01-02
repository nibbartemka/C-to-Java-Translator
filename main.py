from Lexer import Lexer
from Parser import Parser
from CodeGenerator import CodeGenerator
from Exceptions import *
from SemanticAnalyzer import SemanticAnalyzer
from OptimizeCode import OptimizeCode
  
INPUT_PATH = "file.txt"
LEXER_OUTPUT_PATH = "lexer_output.txt"
PARSER_OUTPUT_PATH = "parser_output.txt"
SEMANTIC_ANALYZER_OUTPUT_PATH = "semantic_output.txt"
GENERATED_CODE_PATH = "generated_code.txt"
OPTIMIZED_OUTPUT_PATH = "optimized_output.txt"
ENCODING = "utf-8"


with (
  open(INPUT_PATH, "r", encoding=ENCODING) as in_file,
  open(LEXER_OUTPUT_PATH, "w", encoding=ENCODING) as lexer_file
):
  lexer = Lexer(in_file)
  lexer.print_all_tokens(file=lexer_file)


with (
  open(INPUT_PATH, "r", encoding=ENCODING) as in_file,
  open(PARSER_OUTPUT_PATH, "w", encoding=ENCODING) as parser_file
):
  lexer = Lexer(in_file)
  parser = Parser(lexer)
  syntax_tree = parser.parse()
  print(syntax_tree, file=parser_file)


with (
  open(INPUT_PATH, "r", encoding=ENCODING) as in_file,
  open(SEMANTIC_ANALYZER_OUTPUT_PATH, "w", encoding=ENCODING) as semantic_file
):
  lexer = Lexer(in_file)
  parser = Parser(lexer)
  tree = parser.parse()
  semantic = SemanticAnalyzer()
  scope = semantic.analyze(tree)
  scope.print(file=semantic_file)


with (
  open(INPUT_PATH, "r", encoding=ENCODING) as in_file,
  open(GENERATED_CODE_PATH, "w", encoding=ENCODING) as generate_file
):
  lexer = Lexer(in_file)
  parser = Parser(lexer)
  tree = parser.parse()
  code_generation = CodeGenerator(tree)
  print(code_generation, file=generate_file)


with (
  open(OPTIMIZED_OUTPUT_PATH, "w", encoding=ENCODING) as optimize_file
):
  optimized_code = OptimizeCode(scope, tree, optimize_file)
  optimized_code.print()

