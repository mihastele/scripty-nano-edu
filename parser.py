from model import *
from tokens import *
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.curr = 0
        # parser with one lookahead

        # <primary>  ::=  <integer> | <float> | '(' <expr> ')'
    def primary(self):
        if self.match(TOK_INTEGER): return Integer(int(self.previous_token().lexeme))
        if self.match(TOK_FLOAT): return Float(float(self.previous_token().lexeme))
        if self.match(TOK_LPAREN):
            expr = self.expr()
        if (not self.match(TOK_RPAREN)):
            raise SyntaxError(f'Error: ")" expected.')
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
