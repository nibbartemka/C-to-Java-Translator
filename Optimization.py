from SemanticAnalyzer import Scope
import sys

class Optimization:
    def __init__(self, global_scope: Scope, in_file, out_file=sys.stdout):
        self.global_scope = global_scope
        self.in_file = in_file.read()
        self.out_file = out_file
        self.del_line_num = None
    
    def optimize(self, scope: Scope, del_line_num: set) -> None:
        del_line_num.update({value.name.lineno for value in iter(scope.variable_table.values()) if not value.is_using})

        for child in scope.children:
            self.optimize(child, del_line_num)

        self.del_line_num = del_line_num


    def print(self):
        self.del_line_num.discard(0)

        lines = self.in_file.split("\n")
        lines_iter = (line for i, line in enumerate(lines) if i + 1 not in self.del_line_num)
        
        print("\n".join(lines_iter), file=self.out_file)





