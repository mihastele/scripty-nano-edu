from model import *
from tokens import *
from utils import *
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.curr = 0
        # parser with one lookahead
    
    
    def advance(self):
        token = self.peek()
        self.curr += 1
        return token
    
    def peek(self):
        if self.curr < len(self.tokens):
            return self.tokens[self.curr]
        return None

    
    def is_next(self, expected_type):
        if self.curr >= len(self.tokens):
            return False
        return self.peek().token_type == expected_type

    def expect(self, expected_type):
        if self.curr >= len(self.tokens):
            parse_error(f"Found {self.previous_token.lexeme!r} at the end of parsing.", self.previous_token.line)
        elif self.peek().token_type == expected_type:
            token = self.advance()
            return token
        else:
            raise parse_error(f"Expected {expected_type!r}, found {self.previous_token().lexeme!r}.", self.peek().line)

    def match(self, expected_type):
        if self.curr >= len(self.tokens):
            return False
        if self.peek().token_type != expected_type:
            return False
        self.advance()
        return True

    def previous_token(self):
        if self.curr > 0:
            return self.tokens[self.curr - 1]
        return None


        # <primary>  ::=  <integer> | <float> | '(' <expr> ')'
    def primary(self):
        if self.match(TOK_INTEGER): return Integer(int(self.previous_token().lexeme))
        if self.match(TOK_FLOAT): return Float(float(self.previous_token().lexeme))
        if self.match(TOK_LPAREN):
            expr = self.expr()
            if (not self.match(TOK_RPAREN)):
                parse_error(f'Error: ")" expected.', self.peek().line)
            else:
                return Grouping(expr)

    # <unary>  ::=  ('+'|'-'|'~') <unary>  |  <primary>
    def unary(self):
        if self.match(TOK_NOT) or self.match(TOK_MINUS) or self.match(TOK_PLUS):
            op = self.previous_token()
            operand = self.unary()
            return UnOp(op, operand)
        return self.primary()

    # <factor>  ::=  <unary>
    def factor(self):
        return self.unary()

    # <term>  ::=  <factor> ( ('*'|'/') <factor> )*
    def term(self):
        expr = self.factor()
        while self.match(TOK_STAR) or self.match(TOK_SLASH):
            op = self.previous_token()
            right = self.factor()
            # print(f"Binary operation: {op.lexeme}")
            expr = BinOp(op, expr, right)
        return expr

    # <expr>  ::=  <term> ( ('+'|'-') <term> )*
    def expr(self):
        expr = self.term()
        while self.match(TOK_PLUS) or self.match(TOK_MINUS):
            op = self.previous_token()
            right = self.term()
            expr = BinOp(op, expr, right)
        return expr

    def parse(self):
        ast = self.expr()
        return ast
