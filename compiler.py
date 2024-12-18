from definitions import *
from model import *
from tokens import *
from utils import *


SYM_VAR = 'SYM_VAR'
SYM_FUNC = 'SYM_FUNC'

class Symbol:
    def __init__(self, name, symtype=SYM_VAR, depth=0):
        self.name = name
        self.depth = depth
        self.symtype = symtype


class Compiler:
    def __init__(self):
        self.code = []
        self.locals = []
        self.globals = []
        # functions will be symbols with names
        self.functions = []
        self.scope_depth = 0
        self.label_counter = 0

    def make_label(self):
        self.label_counter += 1
        return f'LBL{self.label_counter}'

    def emit(self, instruction):
        self.code.append(instruction)

    def get_func_symbol(self, name):
        for symbol in reversed(self.functions):
            if symbol.name == name:
                return symbol
        return None

    def get_var_symbol(self, name):
        for index, symbol in reversed(list(enumerate(self.locals))):
            if symbol.name == name:
                return (symbol, index)
        for index, symbol in reversed(list(enumerate(self.globals))):
            if symbol.name == name:
                return (symbol, index)
        return None

    def begin_block(self):
        self.scope_depth += 1

    def end_block(self):
        self.scope_depth -= 1
        # Loop and remove all the locals that are "deeper" than the current scope depth
        i = len(self.locals) - 1
        while len(self.locals) > 0 and self.locals[i].depth > self.scope_depth:
            self.emit(('POP',))
            self.locals.pop()
            i -= 1

    def compile(self, node):
        if isinstance(node, Integer):
            value = (TYPE_NUMBER, float(node.value))
            self.emit(('PUSH', value))

        elif isinstance(node, Float):
            value = (TYPE_NUMBER, float(node.value))
            self.emit(('PUSH', value))

        elif isinstance(node, Bool):
            value = (TYPE_BOOL, True if node.value == True or node.value == 'true' else False)
            self.emit(('PUSH', value))

        elif isinstance(node, String):
            value = (TYPE_STRING, stringify(node.value))
            self.emit(('PUSH', value))

        elif isinstance(node, BinOp):
            self.compile(node.left)
            self.compile(node.right)
            if node.op.token_type == TOK_PLUS:
                self.emit(('ADD',))
            elif node.op.token_type == TOK_MINUS:
                self.emit(('SUB',))
            elif node.op.token_type == TOK_STAR:
                self.emit(('MUL',))
            elif node.op.token_type == TOK_SLASH:
                self.emit(('DIV',))
            elif node.op.token_type == TOK_CARET:
                self.emit(('EXP',))
            elif node.op.token_type == TOK_MOD:
                self.emit(('MOD',))
            elif node.op.token_type == TOK_LT:
                self.emit(('LT',))
            elif node.op.token_type == TOK_GT:
                self.emit(('GT',))
            elif node.op.token_type == TOK_LE:
                self.emit(('LE',))
            elif node.op.token_type == TOK_GE:
                self.emit(('GE',))
            elif node.op.token_type == TOK_EQEQ:
                self.emit(('EQ',))
            elif node.op.token_type == TOK_NE:
                self.emit(('NE',))

        elif isinstance(node, UnOp):
            self.compile(node.operand)
            if node.op.token_type == TOK_MINUS:
                self.emit(('NEG',))
            elif node.op.token_type == TOK_NOT:
                self.emit(('PUSH', (TYPE_BOOL, True)))
                self.emit(('XOR',))

        elif isinstance(node, LogicalOp):
            self.compile(node.left)
            self.compile(node.right)
            if node.op.token_type == TOK_AND:
                self.emit(('AND',))
            elif node.op.token_type == TOK_OR:
                self.emit(('OR',))

        elif isinstance(node, Grouping):
            self.compile(node.value)

        elif isinstance(node, PrintStmt):
            self.compile(node.value)
            if node.end == '':
                self.emit(('PRINT',))
            else:
                self.emit(('PRINTLN',))

        elif isinstance(node, IfStmt):
            self.compile(node.test)
            then_label = self.make_label()
            else_label = self.make_label()
            exit_label = self.make_label()
            self.emit(
                ('JMPZ', else_label))  # Branch directly to else_label if top of stack is EQUAL to ZERO (a.k.a. False)
            self.emit(('LABEL', then_label))
            self.begin_block()
            self.compile(node.then_stmts)
            self.end_block()
            self.emit(('JMP', exit_label))
            self.emit(('LABEL', else_label))
            if node.else_stmts:
                self.begin_block()
                self.compile(node.else_stmts)
                self.end_block()
            self.emit(('LABEL', exit_label))

        elif isinstance(node, WhileStmt):
            test_label = self.make_label()
            body_label = self.make_label()
            exit_label = self.make_label()
            self.emit(('LABEL', test_label))
            self.compile(node.test)
            self.emit(
                ('JMPZ', exit_label))  # Branch directly to exit_label if top of stack is EQUAL to ZERO (a.k.a. False)
            self.emit(('LABEL', body_label))
            self.begin_block()
            self.compile(node.body_stmts)
            self.end_block()
            self.emit(('JMP', test_label))
            self.emit(('LABEL', exit_label))

        elif isinstance(node, Stmts):
            for stmt in node.stmts:
                self.compile(stmt)

        elif isinstance(node, Assignment):
            self.compile(node.right)
            symbol = self.get_var_symbol(node.left.name)
            if not symbol:
                new_symbol = Symbol(node.left.name, SYM_VAR, self.scope_depth)
                if self.scope_depth == 0:
                    self.globals.append(new_symbol)
                    new_global_slot = len(self.globals) - 1
                    self.emit(('STORE_GLOBAL', new_global_slot))
                else:
                    self.locals.append(new_symbol)
                    # visual helper SET_SLOT, it does nothing in VM
                    self.emit(('SET_SLOT', str(len(self.locals) - 1) + f" ({new_symbol.name})"))
            else:
                sym, slot = symbol
                if sym.depth == 0:
                    self.emit(('STORE_GLOBAL', slot))
                else:
                    self.emit(('STORE_LOCAL', slot))

        elif isinstance(node, Identifier):
            symbol = self.get_var_symbol(node.name)
            if not symbol:
                compile_error(f'Variable {node.name} is not defined.', node.line)
            else:
                sym, slot = symbol
                if sym.depth == 0:
                    self.emit(('LOAD_GLOBAL', slot))
                else:
                    self.emit(('LOAD_LOCAL', slot))

        elif isinstance(node, FuncDecl):
            var = self.get_var_symbol(node.name)
            func = self.get_func_symbol(node.name)
            if func:
                compile_error(f'Function {node.name} is already defined.', node.line)
            if var:
                compile_error(f'Variable {node.name} shadows function.', node.line)
            new_func = Symbol(node.name, SYM_FUNC, self.scope_depth)
            self.functions.append(new_func)

            end_label = self.make_label()
            self.emit(('JMP', end_label))
            self.emit(('LABEL', new_func.name))
            self.begin_block()
            self.compile(node.body_stmts)
            self.end_block()
            self.emit(('RTS',))
            self.emit(('LABEL', end_label))


        elif isinstance(node, FuncCall):
            pass

        elif isinstance(node, FuncCallStmt):
            self.compile(node.expr)


    def print_code(self):
        i = 0
        for instruction in self.code:
            if instruction[0] == 'LABEL':
                print(f"{i:08} {Colors.RED}{instruction[1]}:{Colors.WHITE}")
                i += 1
                continue
            if instruction[0] == 'PUSH':
                print(
                    f"{i:08}     {Colors.GREEN}{instruction[0]} {Colors.CYAN}{stringify(instruction[1][1])}{Colors.WHITE}")
                i += 1
                continue
            if len(instruction) == 1:
                print(f"{i:08}     {Colors.BLUE}{instruction[0]}{Colors.WHITE}")
            elif len(instruction) == 2:
                print(f"{i:08}     {Colors.GREEN}{instruction[0]} {Colors.CYAN}{instruction[1]}{Colors.WHITE}")
            i += 1

    def generate_code(self, node):
        self.emit(('LABEL', 'START'))
        self.compile(node)
        self.emit(('HALT',))
        return self.code
