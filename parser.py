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
            return self.func_stmt()
        else:
            pass


    
    def stmts(self):
        stmts = []
        while self.curr < len(self.tokens):
            stmt = self.stmt()
            print(f"Parsed {stmt}")  # for debugging purposes, print the parsed statement
            stmts.append(stmt)
        return Stmts(stmts, line=self.previous_token().line)
    
    def program(self):
        stmts = self.stmts()
        # print("HIII")
        return stmts
    
    def parse(self):
        ast = self.program()
        return ast
