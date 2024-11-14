from model import *
from tokens import *

class Interpreter:
    def __init__(self):
        pass

    def interpret(self, node):
        if isinstance(node, Integer):
            return float(node.value)
        elif isinstance(node, Float):
            return float(node.value)
        elif isinstance(node, Grouping):
            return self.interpret(node.value)
        elif isinstance(node, BinOp):
            lVal = self.interpret(node.left)
            rVal = self.interpret(node.right)
            if node.op.token_type == TOK_PLUS:
                return lVal + rVal
            elif node.op.token_type == TOK_MINUS:
                return lVal - rVal
            elif node.op.token_type == TOK_STAR:
                return lVal * rVal
            elif node.op.token_type == TOK_SLASH:
                return lVal / rVal
        elif isinstance(node, UnOp):
            operand = self.interpret(node.operand)
            if node.op.token_type == TOK_PLUS:
                return +operand
            elif node.op.token_type == TOK_MINUS:
                return -operand
            elif node.op.token_type == TOK_NOT:
                return not operand