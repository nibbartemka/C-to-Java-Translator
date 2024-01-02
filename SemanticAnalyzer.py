from __future__ import annotations
from dataclasses import dataclass
from Exceptions import SemanticAnalyzerException
from Nodes import *
from collections import OrderedDict
import sys


builtin_ids = ["true", "false", "Console", "WriteLine", "Write"]


@dataclass
class Variable:
    name: str
    type: str
    value: ... = None
    is_using: bool = False


class Scope:
    parent: Scope
    children: list[Scope]
    scope_name: str
    variable_table: OrderedDict[str, Variable]  # name: variable


    def __init__(self, scope_name: str = "", parent: Scope = None) -> None:
        self.parent = parent
        self.children = []
        self.scope_name = scope_name
        self.variable_table = OrderedDict()
    
    def print(self, file=sys.stdout, level=0):
        offset = lambda l: "   " * l
        print(offset(level) + "Scope: " + self.scope_name, file=file)
        print(offset(level + 1) + "Variables:", file=file)
        for variable in self.variable_table.values():
            print(offset(level + 2) + f"{variable.type} {variable.name} {variable.is_using}", file=file)
        print(offset(level + 1) + "Children:", file=file)
        for child in self.children:
            child.print(file, level + 2)

    def add_variable(self, name: Token, type: NodeType | str, value=None) -> None:
        if name.value in self.variable_table:
            raise SemanticAnalyzerException(f"Переменная уже объявлена : line {name.lineno}, pos {name.pos}")
        if isinstance(type, NodeType):
            type_str = type._generate_text()
        else:
            type_str = type 
        self.variable_table[name.value] = Variable(name, type_str, value)
    

    def update_variable(self, name: Token, value) -> None:
        variable = self.find_variable(name.value)
        if variable is None:
            raise SemanticAnalyzerException(f"Обновление не объявленной переменной : line {name.lineno}, pos {name.pos}")
        variable.value = value


    def add_scope(self, scope_name: str = "") -> Scope:
        new_scope = Scope(scope_name, parent=self)
        self.children.append(new_scope)
        return new_scope


    def find_variable(self, name: str) -> Variable | None:
        """Ищет переменную в более глобальных областях видимости"""
        curr_scope = self
        while curr_scope != None:
            if name in curr_scope.variable_table:
                return Variable(name, curr_scope.variable_table[name], curr_scope.variable_table[name].value, curr_scope.variable_table[name].is_using)
            curr_scope = curr_scope.parent
        return None
    
    def find_scope(self, name: str) -> Scope | None:
        '''
            Ищем область видимости в которой есть наша переменная
        '''
        curr_scope = self
        while curr_scope != None:
            if name in curr_scope.variable_table:
                return curr_scope
            curr_scope = curr_scope.parent
        return None
    
    def has_variable(self, name: Token) -> bool:
        return self.find_variable(name.value) is not None

    def is_var_using(self, name: str) -> bool:
        var_ = self.find_variable(name)
        if not var_:
            return False
        else:
            return var_.is_using
    
    def change_is_using(self, name: Token) -> None:
        scope = self.find_scope(name.value)
        if scope is not None:
            scope.variable_table[name.value].is_using = True


class SemanticAnalyzer:
    last_declared_id: str = ""
    is_declaration: bool = False

    def analyze(self, syntax_tree_root: Node) -> Scope:
        global_scope = Scope(scope_name="global")
        for builtin_id in builtin_ids:
            global_scope.add_variable(Token(TokenInfo.ID, builtin_id, 0, 0), "")
        self.__analyze(syntax_tree_root, global_scope)
        return global_scope


    def __analyze(self, node: Node, scope: Scope):
        match node:
            case NodeDeclaration():
                self.last_declared_id = node.id.id.value
                self.is_declaration = True
                scope.add_variable(node.id.id, node.type, node.value)
            case NodeAssigning():
                self.is_declaration = False
                scope.update_variable(node.left_side.id, node.right_side)
            case NodeForConstruction():
                self.is_declaration = False
                scope = scope.add_scope("For")
            case NodeWhileConstruction():
                self.is_declaration = False
                scope = scope.add_scope("While")
            case NodeFunction():
                self.is_declaration = False
                scope.add_variable(node.name.id, "Function")
                scope = scope.add_scope("Function " + node.name.id.value)
                for id, type in zip(node.params.ids, node.params.types):
                    scope.add_variable(id.id, type)
            case NodeIfConstruction():
                self.is_declaration = False
                scope.add_scope("If")
            case NodeElseBlock():
                self.is_declaration = False
                scope.add_scope("Else")
            case NodeVar():
                if not scope.has_variable(node.id):
                    raise SemanticAnalyzerException(f"Обращение к не объявленной переменной : line {node.id.lineno}, pos {node.id.pos}")
                else:
                    if (self.last_declared_id != node.id.value and self.is_declaration) or\
                        (not self.is_declaration):
                        scope.change_is_using(node.id)
        for child in node.get_children():
            self.__analyze(child, scope)