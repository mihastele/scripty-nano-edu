from utils import *
from model import *
from tokens import *
from state import *
import codecs

###############################################################################
# Constants for different runtime value types
###############################################################################
TYPE_NUMBER = 'TYPE_NUMBER'  # Default to 64-bit float
TYPE_STRING = 'TYPE_STRING'  # String managed by the host language
TYPE_BOOL = 'TYPE_BOOL'  # true | false


class Interpreter:
    def interpret(self, node, env):
        if isinstance(node, Integer):
            return (TYPE_NUMBER, float(node.value))

        elif isinstance(node, Float):
            return (TYPE_NUMBER, float(node.value))

        elif isinstance(node, String):
            return (TYPE_STRING, str(node.value))

        elif isinstance(node, Bool):
            return (TYPE_BOOL, node.value)

        elif isinstance(node, Grouping):
            return self.interpret(node.value, env)
        
        elif isinstance(node, Identifier):
            value = env.get_var(node.name)
            if value is None:
                runtime_error(f'Undefined variable {node.name!r}.', node.line)
            if value[1] is None:
                runtime_error(f"Uninitialized variable {node.name!r}.", node.line)
            return value

        elif isinstance(node, Assignment):
            # left := right
            # Eval right
            righttype, rightval = self.interpret(node.right, env)
            # varval = env.get_var(node.left.name)
            env.set_var(node.left.name, (righttype, rightval))


        elif isinstance(node, BinOp):
            lefttype, leftval = self.interpret(node.left, env)
            righttype, rightval = self.interpret(node.right, env)
            if node.op.token_type == TOK_PLUS:
                if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
                    return (TYPE_NUMBER, leftval + rightval)
                elif lefttype == TYPE_STRING or righttype == TYPE_STRING:
                    return (TYPE_STRING, stringify(leftval) + stringify(rightval))
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
            operandtype, operandval = self.interpret(node.operand, env)
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
            lefttype, leftval = self.interpret(node.left, env)
            if node.op.token_type == TOK_OR:
                if leftval:
                    return (lefttype, leftval)
            elif node.op.token_type == TOK_AND:
                if not leftval:
                    return (lefttype, leftval)
            return self.interpret(node.right, env)
        
        elif isinstance(node, Stmts):
            # eval them in sequence
            for stmt in node.stmts:
                self.interpret(stmt, env)

        elif isinstance(node, PrintStmt):
            exprtype, exprval = self.interpret(node.value, env)
            val = stringify(exprval)
            print(codecs.escape_decode(bytes(str(val), 'utf-8'))[0].decode('utf-8'), end=node.end)

        elif isinstance(node, IfStmt):
            testtype, testval = self.interpret(node.test, env)
            if testtype != TYPE_BOOL:
                runtime_error(f'Expected boolean value, got {testtype}.', node.test.line)
            if testval:
                self.interpret(node.then_stmts, env.new_env())
            else:
                if node.else_stmts:
                    self.interpret(node.else_stmts, env.new_env())
        
        elif isinstance(node, WhileStmt):
            new_env = env.new_env()
            while True:
                testtype, testval = self.interpret(node.test, new_env)
                if testtype!= TYPE_BOOL:
                    runtime_error(f'Expected boolean value, got {testtype}.', node.test.line)
                if not testval:
                    break
                self.interpret(node.body_stmts, new_env)

        elif isinstance(node, ForStmt):
            varname = node.ident.name
            ltype, i = self.interpret(node.start, env)
            endtype, end = self.interpret(node.end, env)
            block_new_env = env.new_env()
            if i < end:
                if node.step is None:
                    step = 1
                else:
                    step_type, step = self.interpret(node.step, env)
                while i <= end:
                    newval = (TYPE_NUMBER, i)
                    block_new_env.set_var(varname, newval)
                    self.interpret(node.body_stmts, block_new_env)
                    i += step
            else:
                if node.step is None:
                    step = -1
                else:
                    step_type, step = self.interpret(node.step, env)
                while i >= end:
                    newval = (TYPE_NUMBER, i)
                    block_new_env.set_var(varname, newval)
                    self.interpret(node.body_stmts, block_new_env)
                    i += step

        elif isinstance(node, FuncDecl):
            env.set_func(node.name, (node, env))
        elif isinstance(node, FuncCall):
            # Make sure the function exists
            func = env.get_func(node.name)
            if not func:
                runtime_error(f'Function {node.name} not declared.', node.line)

            # fetch the fucntion declaration
            func_decl = func[0]
            func_env = func[1]

            # Does the number of args match the expected number of params?
            if len(node.args) != len(func_decl.params):
                runtime_error(f'Function {func_decl.name} expects {len(func_decl.params)} arguments, but got {len(node.args)}.',
                                node.line)
            # We need to eval all the args
            args = []
            for arg in node.args:
                # argtype, argval = self.interpret(arg, env)
                # args.append((argtype, argval))
                args.append(self.interpret(arg, env))
            # Proper env
            new_func_env = func_env.new_env()
            # We must create local variables in the new child environment of the function for the parameters and bind the args to them
            for param, argval in zip(func_decl.params, args):
                print(f'Binding {param.name} to {argval}')  # Debugging purpose only, remove later
                new_func_env.set_var(param.name, argval)
            # ask to interpret the body statements of the function declaration
            self.interpret(func_decl.body_stmts, new_func_env)
        elif isinstance(node, FuncCallStmt):
            self.interpret(node.expr, env)

    def interpret_ast(self, node):
        # Entrypoint with global environment
        env = Environment()
        self.interpret(node, env)