from Nodes import *
from Token import *
from Exceptions import *

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token = self.lexer.getnexttoken()
        self.iteration_flag = False
        self.ignore_semi = False
        self.peek_tokens_queue = []

    def next_token(self):
        if self.peek_tokens_queue:
            self.token = self.peek_tokens_queue.pop(0)
        else:
            self.token = self.lexer.getnexttoken()

    def peek_next_token(self):
        """Посмотреть следующий токен, не переключаясь на него"""
        self.peek_tokens_queue.append(self.lexer.getnexttoken())
        return self.peek_tokens_queue[-1]      

    def require(self, expected_token):
        if self.token.token != expected_token:
            raise ParserException(f"Token expected {expected_token.name}! line {self.lexer.lineno}, pos {self.lexer.pos}")

    def require_get_and_next(self, expected_token):
        self.require(expected_token)
        token = self.token
        self.next_token()
        return token

    def block(self) -> Node:
        statements = []
        while self.token.token not in {TokenInfo.RCBR, TokenInfo.EOF}:
            statements.append(self.statement())
            if not self.ignore_semi:
                self.require_get_and_next(TokenInfo.SEMI)
            self.ignore_semi = False
        return NodeBlock(statements)

    def else_block(self) -> Node:
        statements = []
        while self.token.token not in {TokenInfo.RCBR, TokenInfo.EOF}:
            statements.append(self.statement())
            if not self.ignore_semi:
                self.require_get_and_next(TokenInfo.SEMI)
            self.ignore_semi = False
        return NodeElseBlock(statements)


    def expression(self) -> Node:
        return self.condition()

    def condition(self) -> Node:
        left = self.or_operand()
        op = self.token.token
        while op == TokenInfo.OR:
            self.next_token()
            left = NodeOr(left, self.or_operand())
            op = self.token.token
        return left

    def or_operand(self) -> Node:
        left = self.inversion()
        op = self.token.token
        while op == TokenInfo.AND:
            self.next_token()
            left = NodeAnd(left, self.inversion())
            op = self.token.token
        return left

    def inversion(self) -> Node:
        match self.token.token:
            case TokenInfo.NOT:
                self.next_token()
                return NodeNot(self.logical_operand())
            case _:
                return self.and_operand()

    def and_operand(self) -> Node:
        left = self.sum()
        op = self.token.token
        while op in {TokenInfo.L, TokenInfo.G, TokenInfo.LE, TokenInfo.GE, TokenInfo.EQ, TokenInfo.NEQ}:
            self.next_token()
            match op:
                case TokenInfo.L:
                    left = NodeL(left, self.sum())
                case TokenInfo.G:
                    left = NodeG(left, self.sum())
                case TokenInfo.LE:
                    left = NodeLE(left, self.sum())
                case TokenInfo.GE:
                    left = NodeGE(left, self.sum())
                case TokenInfo.EQ:
                    left = NodeEQ(left, self.sum())
                case TokenInfo.NEQ:
                    left = NodeNEQ(left, self.sum())
            op = self.token.token
        return left

    def sum(self) -> Node:
        left = self.term()
        op = self.token.token
        while op in {TokenInfo.PLUS, TokenInfo.MINUS}:
            self.next_token()
            match op:
                case TokenInfo.PLUS:
                    left = NodePlus(left, self.term())
                case Token.MINUS:
                    left = NodeMinus(left, self.term())
            op = self.token.token
        return left

    def term(self) -> Node:
        left = self.factor()
        op = self.token.token
        while op in {TokenInfo.ASTERISK, TokenInfo.SLASH, TokenInfo.PERCENT}:
            self.next_token()
            match op:
                case TokenInfo.ASTERISK:
                    left = NodeMultiply(left, self.factor())
                case TokenInfo.SLASH:
                    left = NodeDivision(left, self.factor())
                case TokenInfo.PERCENT:
                    left = NodeMod(left, self.factor())
            op = self.token.token
        return left

    def factor(self) -> Node:
        match self.token.token:
            case TokenInfo.MINUS:
                self.next_token()
                return NodeUnaryMinus(self.operand())
            case _:
                return self.operand()

    def operand(self) -> Node:
        first_token = self.token
        match self.token.token:
            case TokenInfo.INT_LITERAL:
                self.next_token()
                return NodeIntLiteral(first_token)
            case TokenInfo.FLOAT_LITERAL:
                self.next_token()
                return NodeFloatLiteral(first_token)
            case TokenInfo.ID:
                ids = [NodeVar(first_token)]
                self.next_token()
                while self.token.token == TokenInfo.DOT:
                    self.next_token()
                    ids.append(NodeVar(self.require_get_and_next(TokenInfo.ID)))
                if len(ids) == 1:
                    var = NodeVar(first_token)
                else:
                    var = NodeChainedVar(ids)
                if self.token.token == TokenInfo.LBR:
                    self.next_token()
                    params = self.actual_params()
                    self.require_get_and_next(TokenInfo.RBR)
                    return NodeCall(var, params)
                else:
                    return var
            case TokenInfo.LBR:
                self.next_token()
                expression = self.expression()
                self.require_get_and_next(TokenInfo.RBR)
                return expression
    

    def type(self) -> Node:
        id = self.token
        self.next_token()
        if self.token.token != TokenInfo.LSBR:
            return NodeAtomType(id)
        self.next_token()
        self.require(TokenInfo.INT_LITERAL)
        size = self.token
        self.next_token()
        self.require(TokenInfo.RSBR)
        self.next_token()
        return NodeComplexType(id, size)

    def declaration(self) -> Node:
        self.require(TokenInfo.ID)
        _type = self.type()
        self.require(TokenInfo.ID)
        id = self.token
        self.next_token()

        if self.token.token == TokenInfo.ASSIGN:
            self.next_token()
            return NodeDeclaration(_type, NodeVar(id), self.expression())
        return NodeDeclaration(_type, NodeVar(id))
    
    def if_stmt(self) -> NodeIfConstruction:
        self.next_token()
        condition = self.condition()
        self.require_get_and_next(TokenInfo.LCBR)
        block = self.block()
        self.require_get_and_next(TokenInfo.RCBR)
        self.ignore_semi = True
        if self.token.token != TokenInfo.ELSE:
            return NodeIfConstruction(condition, block, NodeElseBlock([]))
        self.next_token()
        self.require_get_and_next(TokenInfo.LCBR)
        else_block = self.else_block()
        self.require_get_and_next(TokenInfo.RCBR)
        self.ignore_semi = True
        return NodeIfConstruction(condition, block, else_block)

    def while_stmt(self) -> NodeWhileConstruction:
        self.next_token()
        self.iteration_flag = True
        condition = self.condition()
        self.require_get_and_next(TokenInfo.LCBR)
        block = self.block()
        self.require_get_and_next(TokenInfo.RCBR)
        self.iteration_flag = False
        self.ignore_semi = True
        return NodeWhileConstruction(condition, block)

    def for_stmt(self) -> NodeForConstruction:
        self.next_token()
        self.iteration_flag = True
        self.require_get_and_next(TokenInfo.LBR)
        init = self.statement()
        self.require_get_and_next(TokenInfo.SEMI)
        condition = self.condition()
        self.require_get_and_next(TokenInfo.SEMI)
        step = self.statement()
        self.require_get_and_next(TokenInfo.RBR)
        self.require_get_and_next(TokenInfo.LCBR)
        block = self.block()
        self.require_get_and_next(TokenInfo.RCBR)
        self.iteration_flag = False
        self.ignore_semi = True
        return NodeForConstruction(init, condition, step, block)

    def statement(self) -> Node:
        match self.token.token:
            case TokenInfo.ID:
                match self.peek_next_token().token:
                    case TokenInfo.ID:
                        if self.peek_next_token().token == TokenInfo.LBR:
                            return self.function()
                        else:
                            return self.declaration()
                    case TokenInfo.ASSIGN:
                        first_token = self.token
                        self.next_token()
                        self.next_token()
                        return NodeAssigning(NodeVar(first_token), self.expression())
                    case _:
                        return self.expression()

            case TokenInfo.IF:
                return self.if_stmt()

            case TokenInfo.WHILE:
                return self.while_stmt()
            
            case TokenInfo.FOR:
                return self.for_stmt()

            case TokenInfo.BREAK:
                self.next_token()
                if self.iteration_flag:
                  return NodeBreak()
                else:
                  raise ParserException(f'Invalid statement "break": line {self.lexer.lineno}, pos {self.lexer.pos}')
            
            case TokenInfo.CONTINUE:
                self.next_token()
                if self.iteration_flag:
                  return NodeContinue()
                else:
                  raise ParserException(f'Invalid statement "continue": line {self.lexer.lineno}, pos {self.lexer.pos}')
            
            case _:
                return self.expression()

    def function(self) -> NodeFunction:
        self.require(TokenInfo.ID)
        _type = self.type()
        id = self.require_get_and_next(TokenInfo.ID)
        self.require_get_and_next(TokenInfo.LBR)
        params = self.formal_params()
        self.require_get_and_next(TokenInfo.RBR)
        self.require_get_and_next(TokenInfo.LCBR)
        block = self.block()
        self.require_get_and_next(TokenInfo.RCBR)
        self.ignore_semi = True
        return NodeFunction(NodeVar(id), params, _type, block)

    def formal_params(self) -> NodeFormalParams:
        types = []
        ids = []
        while self.token.token != TokenInfo.RBR:
            type = self.type()
            id = self.require_get_and_next(TokenInfo.ID)
            if self.token.token == TokenInfo.COMMA:
                self.next_token()
            types.append(type)
            ids.append(NodeVar(id))
        return NodeFormalParams(types, ids)

    def actual_params(self) -> NodeActualParams:
        values = []
        while self.token.token != TokenInfo.RBR:
            value = self.expression()
            values.append(value)
        return NodeActualParams(values)

    def parse(self) -> Node:
        if self.token.token == TokenInfo.EOF:
            self.error("Пустой файл!")
        else:
            statements = []
            while self.token.token != TokenInfo.EOF:
                statements.append(self.statement())
                if not self.ignore_semi:
                    self.require_get_and_next(TokenInfo.SEMI)
                self.ignore_semi = False
            return NodeProgram(statements)