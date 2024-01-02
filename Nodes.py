from __future__ import annotations
from Token import *
from abc import ABC, abstractmethod

class Node:
    def __get_class_name(self):
        c = str(self.__class__)
        pos_1 = c.find('.')+1
        pos_2 = c.find("'", pos_1)
        return f"{c[pos_1:pos_2]}"

    def __repr__(self, level=0):
        attrs = self.__dict__
        res = f"{self.__get_class_name()}\n"
        for attr_name in attrs:
            if attrs[attr_name] is None:
                continue
            res += '|   ' * level
            res += "|+-"
            match attrs[attr_name]:
                case Token():
                    res += f"{attr_name}: {attrs[attr_name]}\n"
                case Node():
                    res += f"{attr_name}: {attrs[attr_name].__repr__(level+1)}"
                case list() as elements:
                    res += f"{attr_name}:\n"
                    for el in elements:
                        res += '|   ' * (level + 1)
                        res += "|+-"
                        res += el.__repr__(level+2)
        return res

    @abstractmethod
    def _generate_text(self, exclude_nodes=None):
        pass

    def get_children(self) -> list[Node]:
        children = []
        for attr in self.__dict__.values():
            if isinstance(attr, list):
                for el in attr:
                    if isinstance(el, Node):
                        children.append(el)
            elif isinstance(attr, Node):
                children.append(attr)
        return children

class NodeProgram(Node):
    def __init__(self, children):
        self.children = children
    def _generate_text(self, exclude_nodes=None):
        if exclude_nodes:
            generated_text = [child._generate_text(exclude_nodes) + ";" for child in self.children if child not in exclude_nodes]
        else:
            generated_text = [child._generate_text() + ";" for child in self.children]
        return "\n".join(generated_text)

class NodeBlock(NodeProgram): pass

class NodeElseBlock(NodeBlock): pass

class NodeDeclaration(Node):
    def __init__(self, _type: NodeType, id: NodeVar, value=None):
        self.type = _type
        self.id = id
        self.value = value
    def _generate_text(self, exclude_nodes=None):
        assign_part = ""
        if self.value:
            assign_part = " = " + self.value._generate_text()
        return f"{self.type._generate_text()} {self.id._generate_text()}" + assign_part

class NodeAssigning(Node):
    def __init__(self, left_side: NodeVar, right_side):
        self.left_side = left_side
        self.right_side = right_side
    def _generate_text(self, exclude_nodes=None):
        return " = ".join([self.left_side._generate_text(), self.right_side._generate_text()])

class NodeIfConstruction(Node):
    def __init__(self, condition, block, else_block):
        self.condition = condition
        self.block = block
        self.else_block = else_block
    def _generate_text(self, exclude_nodes=None):
        else_str = f'else {{\n{self.else_block._generate_text(exclude_nodes)}\n}}' if len(self.else_block.children) > 0 else ""
        return f'if ({self.condition._generate_text(exclude_nodes)}){{\n{self.block._generate_text(exclude_nodes)}\n}}{else_str}'

class NodeWhileConstruction(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block
    def _generate_text(self, exclude_nodes=None):
        return f'while ({self.condition._generate_text(exclude_nodes)}){{\n{self.block._generate_text(exclude_nodes)}\n}}'

class NodeForConstruction(Node):
    def __init__(self, init, condition, step, block):
        self.init = init
        self.condition = condition
        self.step = step
        self.block = block
    def _generate_text(self, exclude_nodes=None):
        return f"for ({self.init._generate_text()}; {self.condition._generate_text()}; {self.step._generate_text()}) {{\n{self.block._generate_text(exclude_nodes)}\n}}"

class NodeLiteral(Node):
    def __init__(self, value):
        self.value = value
    def _generate_text(self, exclude_nodes=None):
        return f'{self.value.value}'

class NodeIntLiteral(NodeLiteral): pass

class NodeFloatLiteral(NodeLiteral): pass

class NodeVar(Node):
    def __init__(self, id: Token):
        self.id = id
    def _generate_text(self, exclude_nodes=None):
        return f'{self.id.value}'

class NodeChainedVar(Node):
    def __init__(self, ids: list[NodeVar]) -> None:
        self.ids = ids
    def _generate_text(self, exclude_nodes=None):
        s = ".".join([id.id.value for id in self.ids])
        if s == "Console.WriteLine":
            s = "System.out.println"
        elif s == "Console.Write":
            s = "System.out.print"
        return s

class NodeType(Node):
    pass

class NodeAtomType(NodeType):
    def __init__(self, id: Token):
        self.id = id
    def _generate_text(self, exclude_nodes=None):
        s = f'{self.id.value}'
        if s == "bool":
            s = "boolean"
        return s

class NodeComplexType(NodeType):
    def __init__(self, id, size):
        self.id = id
        self.size = size
    def _generate_text(self, exclude_nodes=None):
        atom_type = {self.id}
        if atom_type == "bool":
            atom_type = "boolean"
        return f'{atom_type}({self.size})'

class NodeUnaryOperator(Node):
    def __init__(self, operand):
        self.operand = operand
    def _generate_text(self, exclude_nodes=None):
        return f'{self.operand._generate_text()}'

class NodeUnaryMinus(NodeUnaryOperator): pass
class NodeNot(NodeUnaryOperator): pass

class NodeBreak(Node): 
    def _generate_text(self, exclude_nodes=None):
        return "break"

class NodeContinue(Node): 
    def _generate_text(self, exclude_nodes=None):
        return "continue"

class NodeBinaryOperator(Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def _generate_text(self, exclude_nodes=None):
        pass

class NodeL(NodeBinaryOperator):
    def _generate_text(self, exclude_nodes=None):
        return f'({self.left._generate_text()} < {self.right._generate_text()})'
class NodeG(NodeBinaryOperator):
   def _generate_text(self, exclude_nodes=None):
        return f'({self.left._generate_text()} > {self.right._generate_text()})'
class NodeLE(NodeBinaryOperator):
   def _generate_text(self, exclude_nodes=None):
        return f'({self.left._generate_text()} <= {self.right._generate_text()})'
class NodeGE(NodeBinaryOperator):
   def _generate_text(self, exclude_nodes=None):
        return f'({self.left._generate_text()} >= {self.right._generate_text()})'
class NodeEQ(NodeBinaryOperator):
   def _generate_text(self, exclude_nodes=None):
        return f'({self.left._generate_text()} == {self.right._generate_text()})'
class NodeNEQ(NodeBinaryOperator): 
   def _generate_text(self, exclude_nodes=None):
        return f'({self.left._generate_text()} != {self.right._generate_text()})'
class NodeOr(NodeBinaryOperator):
   def _generate_text(self, exclude_nodes=None):
        return f'({self.left._generate_text()} || {self.right._generate_text()})'
class NodeAnd(NodeBinaryOperator):
   def _generate_text(self, exclude_nodes=None):
        return f'({self.left._generate_text()} && {self.right._generate_text()})'

class NodePlus(NodeBinaryOperator):
   def _generate_text(self, exclude_nodes=None):
        return f'({self.left._generate_text()} + {self.right._generate_text()})'
class NodeMinus(NodeBinaryOperator):
   def _generate_text(self, exclude_nodes=None):
        return f'({self.left._generate_text()} - {self.right._generate_text()})'
class NodeDivision(NodeBinaryOperator): 
   def _generate_text(self, exclude_nodes=None):
        return f'({self.left._generate_text()} / {self.right._generate_text()})'
class NodeMultiply(NodeBinaryOperator): 
   def _generate_text(self, exclude_nodes=None):
        return f'({self.left._generate_text()} * {self.right._generate_text()})'
class NodeMod(NodeBinaryOperator):
   def _generate_text(self, exclude_nodes=None):
        return f'({self.left._generate_text()} % {self.right._generate_text()})'


class NodeFormalParams(Node):
    def __init__(self, types: list[NodeType], ids: list[NodeVar]) -> None:
        self.types = types
        self.ids = ids
    def _generate_text(self, exclude_nodes=None):
        params_strs = []
        for type, id in zip(self.types, self.ids):
            s = f"{type._generate_text()} {id._generate_text()}"
            params_strs.append(s)
        return ", ".join(params_strs)

class NodeActualParams(Node):
    def __init__(self, values: list[Node]) -> None:
        self.values = values
    def _generate_text(self, exclude_nodes=None):
        return ", ".join([value._generate_text() for value in self.values])

class NodeCall(Node):
    def __init__(self, callable: NodeVar, params: NodeActualParams) -> None:
        self.callable = callable
        self.params = params
    def _generate_text(self, exclude_nodes=None):
        return f"{self.callable._generate_text()}({self.params._generate_text()})"

class NodeFunction(Node):
    def __init__(self, name: NodeVar, params: NodeFormalParams, return_type: NodeType, block) -> None:
        self.name = name
        self.params = params
        self.return_type = return_type
        self.block = block
    def _generate_text(self, exclude_nodes=None):
        return f"{self.return_type._generate_text()} {self.name._generate_text()}({self.params._generate_text()}) {{\n{self.block._generate_text()}\n}}"
    