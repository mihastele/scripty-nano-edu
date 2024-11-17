from utils import *
from model import *
from tokens import *
import codecs

###############################################################################
# Constants for different runtime value types
###############################################################################
TYPE_NUMBER = 'TYPE_NUMBER'  # Default to 64-bit float
TYPE_STRING = 'TYPE_STRING'  # String managed by the host language
TYPE_BOOL = 'TYPE_BOOL'  # true | false


class Interpreter:
    def interpret(self, node):
        if isinstance(node, Integer):
            return (TYPE_NUMBER, float(node.value))

        elif isinstance(node, Float):
            return (TYPE_NUMBER, float(node.value))

        elif isinstance(node, String):
            return (TYPE_STRING, str(node.value))

        elif isinstance(node, Bool):
            return (TYPE_BOOL, node.value)

        elif isinstance(node, Grouping):
            return self.interpret(node.value)

        elif isinstance(node, BinOp):
            lefttype, leftval = self.interpret(node.left)
            righttype, rightval = self.interpret(node.right)
            if node.op.token_type == TOK_PLUS:
                if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
                    return (TYPE_NUMBER, leftval + rightval)
                elif lefttype == TYPE_STRING or righttype == TYPE_STRING:
                    return (TYPE_STRING, str(leftval) + str(rightval))
                else:
                    runtime_error(f'Unsupported operator {node.op.lexeme!r} between {lefttype} and {righttype}.',
                                node.op.line)

            elif node.op.token_type == TOK_MINUS:
                if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
                    return (TYPE_NUMBER, leftval - rightval)
                else:
                    runtime_error(f'Unsupported operator {node.op.lexeme!r} between {lefttype} and {righttype}.',
                                node.op.line)

            elif node.op.token_type == TOK_STAR:
                if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
                    return (TYPE_NUMBER, leftval * rightval)
                else:
                    runtime_error(f'Unsupported operator {node.op.lexeme!r} between {lefttype} and {righttype}.',
                                node.op.line)

            elif node.op.token_type == TOK_SLASH:
                if rightval == 0:
                    runtime_error(f'Division by zero.', node.line)
                if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
                    return (TYPE_NUMBER, leftval / rightval)
                else:
                    runtime_error(f'Unsupported operator {node.op.lexeme!r} between {lefttype} and {righttype}.',
                                node.op.line)

            elif node.op.token_type == TOK_MOD:
                if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
                    return (TYPE_NUMBER, leftval % rightval)
                else:
                    runtime_error(f'Unsupported operator {node.op.lexeme!r} between {lefttype} and {righttype}.',
                                node.op.line)

            elif node.op.token_type == TOK_CARET:
                if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
                    return (TYPE_NUMBER, leftval ** rightval)
                else:
                    runtime_error(f'Unsupported operator {node.op.lexeme!r} between {lefttype} and {righttype}.',
                                node.op.line)

            elif node.op.token_type == TOK_GT:
                if (lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER) or (
                        lefttype == TYPE_STRING and righttype == TYPE_STRING):
                    return (TYPE_BOOL, leftval > rightval)
                else:
                    runtime_error(f'Unsupported operator {node.op.lexeme!r} between {lefttype} and {righttype}.',
                                node.op.line)

            elif node.op.token_type == TOK_GE:
                if (lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER) or (
                        lefttype == TYPE_STRING and righttype == TYPE_STRING):
                    return (TYPE_BOOL, leftval >= rightval)
                else:
                    runtime_error(f'Unsupported operator {node.op.lexeme!r} between {lefttype} and {righttype}.',
                                node.op.line)

            elif node.op.token_type == TOK_LT:
                if (lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER) or (
                        lefttype == TYPE_STRING and righttype == TYPE_STRING):
                    return (TYPE_BOOL, leftval < rightval)
                else:
                    runtime_error(f'Unsupported operator {node.op.lexeme!r} between {lefttype} and {righttype}.',
                                node.op.line)

            elif node.op.token_type == TOK_LE:
                if (lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER) or (
                        lefttype == TYPE_STRING and righttype == TYPE_STRING):
                    return (TYPE_BOOL, leftval <= rightval)
                else:
                    runtime_error(f'Unsupported operator {node.op.lexeme!r} between {lefttype} and {righttype}.',
                                node.op.line)

            elif node.op.token_type == TOK_EQEQ:
                if (lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER) or (
                        lefttype == TYPE_STRING and righttype == TYPE_STRING) or (
                        lefttype == TYPE_BOOL and righttype == TYPE_BOOL):
                    return (TYPE_BOOL, leftval == rightval)
                else:
                    runtime_error(f'Unsupported operator {node.op.lexeme!r} between {lefttype} and {righttype}.',
                                node.op.line)

            elif node.op.token_type == TOK_NE:
                if (lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER) or (
                        lefttype == TYPE_STRING and righttype == TYPE_STRING) or (
                        lefttype == TYPE_BOOL and righttype == TYPE_BOOL):
                    return (TYPE_BOOL, leftval != rightval)
                else:
                    runtime_error(f'Unsupported operator {node.op.lexeme!r} between {lefttype} and {righttype}.',
                                node.op.line)

        elif isinstance(node, UnOp):
            operandtype, operandval = self.interpret(node.operand)
            if node.op.token_type == TOK_MINUS:
                if operandtype == TYPE_NUMBER:
                    return (TYPE_NUMBER, -operandval)
                else:
                    runtime_error(f'Unsupported operator {node.op.lexeme!r} with {operandtype}.', node.op.line)

            if node.op.token_type == TOK_PLUS:
                if operandtype == TYPE_NUMBER:
                    return (TYPE_NUMBER, operandval)
                else:
                    runtime_error(f'Unsupported operator {node.op.lexeme!r} with {operandtype}.', node.op.line)

            elif node.op.token_type == TOK_NOT:
                if operandtype == TYPE_BOOL:
                    return (TYPE_BOOL, not operandval)
                else:
                    runtime_error(f'Unsupported operator {node.op.lexeme!r} with {operandtype}.', node.op.line)

        elif isinstance(node, LogicalOp):
            lefttype, leftval = self.interpret(node.left)
            if node.op.token_type == TOK_OR:
                if leftval:
                    return (lefttype, leftval)
            elif node.op.token_type == TOK_AND:
                if not leftval:
                    return (lefttype, leftval)
            return self.interpret(node.right)
        
        elif isinstance(node, Stmts):
            # eval them in sequence
            for stmt in node.stmts:
                self.interpret(stmt)

        elif isinstance(node, PrintStmt):
            exprtype, exprval = self.interpret(node.value)
            print(codecs.escape_decode(bytes(str(exprval), 'utf-8'))[0].decode('utf-8'), end=node.end)
