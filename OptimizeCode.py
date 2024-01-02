from SemanticAnalyzer import Scope
from CodeGenerator import CodeGenerator
from Nodes import *
from sys import stdout

class OptimizeCode:
    def __init__(self, global_scope: Scope, tree: Node, out_file=stdout):
        self.global_scope = global_scope
        self.tree = tree
        self.out_file = out_file
        self.unnessessary_nodes = []

        self.optimize(tree)

    def print(self):
        generation = CodeGenerator(self.tree, self.unnessessary_nodes)
        print(generation, file=self.out_file)

    def optimize(self, node: Node) -> None:
        match node:
            case NodeDeclaration():
                id = node.id.id.value
                if not self.global_scope.is_var_using(id):
                    self.unnessessary_nodes.append(node)
            case NodeAssigning():
                id = node.left_side.id.value
                if not self.global_scope.is_var_using(id):
                    self.unnessessary_nodes.append(node)
            case NodeIfConstruction():
                if not node.block.children:
                    self.unnessessary_nodes.append(node)
                else:
                    self.optimize(node.block)
                    rmv_flag = True
                    for child in node.block.children:
                        if child not in self.unnessessary_nodes:
                            rmv_flag = False
                    if rmv_flag:
                        self.unnessessary_nodes.append(node)

                    if not node.else_block.children:
                        self.unnessessary_nodes.append(node.else_block)
                    else:
                        self.optimize(node.else_block)
                        rmv_flag = True
                        for child in node.else_block.children:
                            if child not in self.unnessessary_nodes:
                                rmv_flag = False
                        if rmv_flag:
                            self.unnessessary_nodes.append(node.else_block)

            case NodeWhileConstruction():
                if not node.block.children:
                    self.unnessessary_nodes.append(node)
                else:
                    self.optimize(node.block)
                    rmv_flag = True
                    for child in node.block.children:
                        if child not in self.unnessessary_nodes:
                            rmv_flag = False
                    if rmv_flag:
                        self.unnessessary_nodes.append(node)
            case NodeForConstruction():
                if not node.block.children:
                    self.unnessessary_nodes.append(node)
                else:
                    self.optimize(node.block)
                    rmv_flag = True
                    for child in node.block.children:
                        if child not in self.unnessessary_nodes:
                            rmv_flag = False
                    if rmv_flag:
                        self.unnessessary_nodes.append(node)

        for child in node.get_children():
            if isinstance(node, NodeDeclaration) or isinstance(node, NodeAssigning):
                continue
            self.optimize(child)