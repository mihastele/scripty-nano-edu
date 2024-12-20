from utils import *
from tokens import *
from model import *


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.curr = 0

    def advance(self):
        token = self.tokens[self.curr]
        self.curr = self.curr + 1
        return token

    def peek(self):
        return self.tokens[self.curr]

    def is_next(self, expected_type):
        if self.curr >= len(self.tokens):
            return False
        return self.peek().token_type == expected_type

    def expect(self, expected_type):
        if self.curr >= len(self.tokens):
            parse_error(f'Found {self.previous_token().lexeme!r} at the end of parsing', self.previous_token().line)
        elif self.peek().token_type == expected_type:
            token = self.advance()
            return token
        else:
            parse_error(f'Expected {expected_type!r}, found {self.peek().lexeme!r}.', self.peek().line)

    def previous_token(self):
        return self.tokens[self.curr - 1]

    def match(self, expected_type):
        if self.curr >= len(self.tokens):
            return False
        if self.peek().token_type != expected_type:
            return False
        self.curr = self.curr + 1  # If it is a match, we return True and also comsume that token
        return True

    # <primary>  ::=  <integer>
    #              |  <float>
    #              |  <bool>
    #              |  <string>
    #              |  <identifier>
    #              | '(' <expr> ')'
    def primary(self):
        if self.match(TOK_INTEGER):
            return Integer(int(self.previous_token().lexeme), line=self.previous_token().line)
        elif self.match(TOK_FLOAT):
            return Float(float(self.previous_token().lexeme), line=self.previous_token().line)
        elif self.match(TOK_TRUE):
            return Bool(True, line=self.previous_token().line)
        elif self.match(TOK_FALSE):
            return Bool(False, line=self.previous_token().line)
        elif self.match(TOK_STRING):
            return String(str(self.previous_token().lexeme[1:-1]),
                        line=self.previous_token().line)  # Remove the quotes at the beginning and at the end of the lexeme
        elif self.match(TOK_LPAREN):
            expr = self.expr()
            if (not self.match(TOK_RPAREN)):
                parse_error(f'Error: ")" expected.', self.previous_token().line)
            else:
                return Grouping(expr, line=self.previous_token().line)
        else:
            identifier = self.expect(TOK_IDENTIFIER)
            if self.match(TOK_LPAREN):
                args = self.args()
                self.expect(TOK_RPAREN)
                return FuncCall(identifier.lexeme, args, line=self.previous_token().line)
            else:
                return Identifier(identifier.lexeme, line=self.previous_token().line)

    # <unary>  ::=  ('+'|'-'|'~') <unary>  |  <primary>
    def unary(self):
        if self.match(TOK_NOT) or self.match(TOK_MINUS) or self.match(TOK_PLUS):
            op = self.previous_token()
            operand = self.unary()
            return UnOp(op, operand, line=op.line)
        return self.primary()

    # <exponent> ::= <unary> ( "^" <unary> )*
    def exponent(self):
        expr = self.unary()
        while self.match(TOK_CARET):
            op = self.previous_token()
            right = self.exponent()
            expr = BinOp(op, expr, right, line=op.line)
        return expr

    # <modulo> ::= <exponent> ( "%" <exponent> )*
    def modulo(self):
        expr = self.exponent()
        while self.match(TOK_MOD):
            op = self.previous_token()
            right = self.exponent()
            expr = BinOp(op, expr, right, line=op.line)
        return expr

    # <multiplication>  ::=  <modulo> ( ('*'|'/') <modulo> )*
    def multiplication(self):
        expr = self.modulo()
        while self.match(TOK_STAR) or self.match(TOK_SLASH):
            op = self.previous_token()
            right = self.modulo()
            expr = BinOp(op, expr, right, op.line)
        return expr

    # <addition>  ::=  <multiplication> ( ('+'|'-') <multiplication> )*
    def addition(self):
        expr = self.multiplication()
        while self.match(TOK_PLUS) or self.match(TOK_MINUS):
            op = self.previous_token()
            right = self.multiplication()
            expr = BinOp(op, expr, right, line=op.line)
        return expr

    # <comparison> ::= <addition> (( ">" | ">=" | "<" | "<=" ) <addition>)*
    def comparison(self):
        expr = self.addition()
        while self.match(TOK_GT) or self.match(TOK_GE) or self.match(TOK_LT) or self.match(TOK_LE):
            op = self.previous_token()
            right = self.addition()
            expr = BinOp(op, expr, right, line=op.line)
        return expr

    # <equality>  ::=  <comparison> ( ( "~=" | "==" ) <comparison> )*
    def equality(self):
        expr = self.comparison()
        while self.match(TOK_NE) or self.match(TOK_EQEQ):
            op = self.previous_token()
            right = self.comparison()
            expr = BinOp(op, expr, right, line=op.line)
        return expr

    # <logical_and> ::= <equality> ( "and" <equality> )*
    def logical_and(self):
        expr = self.equality()
        while self.match(TOK_AND):
            op = self.previous_token()
            right = self.equality()
            expr = LogicalOp(op, expr, right, line=op.line)
        return expr

    # <logical_or> ::= <logical_and> ( "or" <logical_and> )*
    def logical_or(self):
        expr = self.logical_and()
        while self.match(TOK_OR):
            op = self.previous_token()
            right = self.logical_and()
            expr = LogicalOp(op, expr, right, line=op.line)
        return expr

    def expr(self):
        return self.logical_or()
    
    # <print_stmt> ::= "print" <expr>
    def print_stmt(self, end):
        if self.match(TOK_PRINT) or self.match(TOK_PRINTLN):
            val = self.expr()
            # prev token because of match
            return PrintStmt(val, end, line=self.previous_token().line)
        
    def if_stmt(self):
        self.expect(TOK_IF)
        test = self.expr()
        self.expect(TOK_THEN)
        then_stmts = self.stmts()
        if self.is_next(TOK_ELSE):
            self.advance() # Consume the else token
            else_stmts = self.stmts()
        else:
            else_stmts = None
        self.expect(TOK_END)
        return IfStmt(test, then_stmts, else_stmts, line=self.previous_token().line)

    def while_stmt(self):
        self.expect(TOK_WHILE)
        test = self.expr()
        self.expect(TOK_DO)
        body = self.stmts()
        self.expect(TOK_END)
        return WhileStmt(test, body, line=self.previous_token().line)
    
    def for_stmt(self):
        self.expect(TOK_FOR)
        Identifier = self.primary()
        self.expect(TOK_ASSIGN)
        start = self.expr()
        self.expect(TOK_COMMA)
        end = self.expr()
        if(self.match(TOK_COMMA)):
            # Using match which consumes, in case of is_next # self.advance() # Consume the comma token
            step = self.expr()
        else:
            step = None
        self.expect(TOK_DO)  # Consume the do token. This should be the start of the block for the for loop's body.
        body_stmts = self.stmts()
        self.expect(TOK_END)  # Consume the end token. This should be the end of the for loop's body.
        return ForStmt(Identifier, start, end, step, body_stmts, line=self.previous_token().line)
    
    # <params>  ::=  <identifier> ("," <identifier> )*
    def params(self):
        params = []
        param_count = 0
        while not self.is_next(TOK_RPAREN):
            param_count += 1
            if param_count > 255:
                raise parse_error('Error: Maximum number of parameters exceeded.', self.previous_token().line)
            name = self.expect(TOK_IDENTIFIER)
            params.append(Param(name.lexeme, line=self.previous_token().line))
            if not self.is_next(TOK_RPAREN):
                self.expect(TOK_COMMA)
        return params

    def args(self):
        args = []
        while not self.is_next(TOK_RPAREN):
            arg = self.expr()
            args.append(arg)
            if not self.is_next(TOK_RPAREN):
                self.expect(TOK_COMMA)
        return args

  # <func_decl>  ::=  "func" <name> "(" <params>? ")" <body_stmts> "end"
    def func_decl(self):
        self.expect(TOK_FUNC)
        name = self.expect(TOK_IDENTIFIER)
        self.expect(TOK_LPAREN)
        params = self.params()
        self.expect(TOK_RPAREN)
        body_stmts = self.stmts()
        self.expect(TOK_END)
        return FuncDecl(name.lexeme, params, body_stmts, line=self.previous_token().line)

    # <local_assign> ::= local <assign>
    def local_assign(self):
        self.expect(TOK_LOCAL)
        left = self.expr()
        self.expect(TOK_ASSIGN)
        right = self.expr()
        return LocalAssignment(left, right, line=self.previous_token().line)

    def ret_stmt(self):
        self.expect(TOK_RET)
        expr = self.expr() if not self.is_next(TOK_SEMICOLON) else None
        return RetStmt(expr, line=self.previous_token().line)

    def stmt(self):
        #predictive parsing
        if self.peek().token_type == TOK_PRINT:
            return self.print_stmt(end='')
        elif self.peek().token_type == TOK_PRINTLN:
            return self.print_stmt(end='\n')
        elif self.peek().token_type == TOK_IF:
            return self.if_stmt()
        elif self.peek().token_type == TOK_WHILE:
            return self.while_stmt()
        elif self.peek().token_type == TOK_FOR:
            return self.for_stmt()
        elif self.peek().token_type == TOK_FUNC:
            return self.func_decl()
        elif self.peek().token_type == TOK_RET:
            return self.ret_stmt()
        elif self.peek().token_type == TOK_LOCAL:
            return self.local_assign()
        else:
            left = self.expr()
            if self.match(TOK_ASSIGN):
                # handle assignment statement
                right = self.expr()
                return Assignment(left, right, line=left.line)
            else:
                # handle function call statement
                return FuncCallStmt(left)



    
    def stmts(self):
        stmts = []
        # loop all statements of the current block
        while self.curr < len(self.tokens) and not self.is_next(TOK_ELSE) and not self.is_next(TOK_END):
            stmt = self.stmt()
            # print(f"Parsed {stmt}")  # for debugging purposes, print the parsed statement
            stmts.append(stmt)
        return Stmts(stmts, line=self.previous_token().line)
    
    def program(self):
        stmts = self.stmts()
        # print("HIII")
        return stmts
    
    def parse(self):
        ast = self.program()
        return ast
