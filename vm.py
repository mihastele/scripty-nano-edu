# The VM itself consists of a single stack.
#
# Instructions to push and pop from the stack:
#
#      ('PUSH', value)       # Push a value to the stack
#      ('POP',)              # Pop a value from the stack
#
# Stack values are tagged with their type using a tuple:
#
#      (TYPE_NUMBER, 4.0)
#      (TYPE_NUMBER, 15.6)
#      (TYPE_NUMBER, -3.141592)
#      (TYPE_STRING, 'This is a string')
#      (TYPE_BOOL, true)
#
# Instructions to add, subtract, multiply, divide, and compare values from the top of the stack
#
#      ('ADD',)              # Addition
#      ('SUB',)              # Subtraction
#      ('MUL',)              # Multiplication
#      ('DIV',)              # Division
#      ('OR',)               # Bitwise OR
#      ('AND',)              # Bitwise AND
#      ('XOR',)              # Bitwise XOR
#      ('NEG',)              # Negate
#      ('EXP',)              # Exponent
#      ('MOD',)              # Modulo
#      ('EQ',)               # Compare ==
#      ('NE',)               # Compare !=
#      ('GT',)               # Compare >
#      ('GE',)               # Compare >=
#      ('LT',)               # Compare <
#      ('LE',)               # Compare <=
#
# An example of the instruction stream for computing 7 + 2 * 3
#
#      ('PUSH', (TYPE_NUMBER, 7))
#      ('PUSH', (TYPE_NUMBER, 2))
#      ('PUSH', (TYPE_NUMBER, 3))
#      ('MUL',)
#      ('ADD',)
#
# Instructions to load and store variables
#
#      ('LOAD', name)        # Push a global variable name from memory to the stack
#      ('STORE, name)        # Save top of the stack into global variable by name
#      ('LOAD_LOCAL', name)  # Push a local variable name from memory to the stack
#      ('STORE_LOCAL, name)  # Save top of the stack to local variable by name
#
# Instructions to manage control-flow (if-else, while, etc.)
#
#      ('LABEL', name)       # Declares a label
#      ('JMP', name)         # Unconditionally jump to label name
#      ('JMPZ', name)        # Jump to label name if top of stack is zero (or false)
#      ('JSR', name)         # Jump to subroutine/function and keep track of the returning PC
#      ('RTS',)              # Return from subroutine/function
from interpreter import TYPE_NUMBER
from definitions import *
from utils import *
import codecs


class VM:
    def __init__(self):
        self.stack = []
        self.labels = {}
        self.globals = {}  # Global variables
        self.pc = 0
        self.sp = 0  # Stack pointer
        self.is_running = False

    def create_label_table(self, instructions):
        self.labels = {}
        pc = 0
        for instruction in instructions:
            opcode, *args = instruction
            if opcode == 'LABEL':
                self.labels.update({args[0]: pc})
            pc += 1

    def run(self, instructions):
        self.is_running = True

        # generate a dict with label names and their corresponding PC positions
        self.create_label_table(instructions)

        # VM kernel
        while self.is_running:
            opcode, *args = instructions[self.pc]
            self.pc += 1
            # PC does not always increment by 1 in real processor scenarios
            # print(opcode, args)
            getattr(self, opcode)(*args)  # --> invoke the method that matched the opcode name

    def LABEL(self, name):
        pass

    def JMP(self, label):
        self.pc = self.labels[label]

    def JMPZ(self, label):
        # if self.POP() == (TYPE_NUMBER, 0):
        valT, val = self.POP()
        if val == 0 or val == False:
            self.pc = self.labels[label]

    def STORE_GLOBAL(self, name):
        self.globals[name] = self.POP()

    def LOAD_GLOBAL(self, name):
        self.PUSH(self.globals[name])

    def PUSH(self, value):
        self.stack.append(value)
        self.sp = self.sp + 1

    def POP(self):
        self.sp = self.sp - 1
        return self.stack.pop()

    def ADD(self):
        righttype, rightval = self.POP()
        lefttype, leftval = self.POP()
        if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
            self.PUSH((TYPE_NUMBER, leftval + rightval))
        elif lefttype == TYPE_STRING and righttype == TYPE_STRING:
            self.PUSH((TYPE_STRING, stringify(leftval) + stringify(rightval)))
        else:
            vm_error(f'Error on ADD between {lefttype} and {righttype}.', self.pc - 1)

    def SUB(self):
        righttype, rightval = self.POP()
        lefttype, leftval = self.POP()
        if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
            self.PUSH((TYPE_NUMBER, leftval - rightval))
        else:
            vm_error(f'Error on SUB between {lefttype} and {righttype}.', self.pc - 1)

    def MUL(self):
        righttype, rightval = self.POP()
        lefttype, leftval = self.POP()
        if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
            self.PUSH((TYPE_NUMBER, leftval * rightval))
        else:
            vm_error(f'Error on MUL between {lefttype} and {righttype}.', self.pc - 1)

    def DIV(self):
        righttype, rightval = self.POP()
        lefttype, leftval = self.POP()
        if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
            self.PUSH((TYPE_NUMBER, leftval / rightval))
        else:
            vm_error(f'Error on DIV between {lefttype} and {righttype}.', self.pc - 1)

    def EXP(self):
        righttype, rightval = self.POP()
        lefttype, leftval = self.POP()
        if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
            self.PUSH((TYPE_NUMBER, leftval ** rightval))
        else:
            vm_error(f'Error on EXP between {lefttype} and {righttype}', self.pc - 1)

    def MOD(self):
        righttype, rightval = self.POP()
        lefttype, leftval = self.POP()
        if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
            self.PUSH((TYPE_NUMBER, leftval % rightval))
        else:
            vm_error(f'Error on MOD between {lefttype} and {righttype}', self.pc - 1)

    def AND(self):
        righttype, rightval = self.POP()
        lefttype, leftval = self.POP()
        if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
            self.PUSH((TYPE_NUMBER, leftval & rightval))
        elif lefttype == TYPE_BOOL and righttype == TYPE_BOOL:
            self.PUSH((TYPE_BOOL, leftval & rightval))
        else:
            vm_error(f'Error on AND between {lefttype} and {righttype}', self.pc - 1)

    def OR(self):
        righttype, rightval = self.POP()
        lefttype, leftval = self.POP()
        if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
            self.PUSH((TYPE_NUMBER, leftval | rightval))
        elif lefttype == TYPE_BOOL and righttype == TYPE_BOOL:
            self.PUSH((TYPE_BOOL, leftval | rightval))
        else:
            vm_error(f'Error on OR between {lefttype} and {righttype}', self.pc - 1)

    def XOR(self):
        righttype, rightval = self.POP()
        lefttype, leftval = self.POP()
        if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
            self.PUSH((TYPE_NUMBER, leftval ^ rightval))
        elif lefttype == TYPE_BOOL and righttype == TYPE_BOOL:
            self.PUSH((TYPE_BOOL, leftval ^ rightval))
        else:
            vm_error(f'Error on XOR between {lefttype} and {righttype}', self.pc - 1)

    def NEG(self):
        operandtype, operand = self.POP()
        if operandtype == TYPE_NUMBER:
            self.PUSH((TYPE_NUMBER, -operand))
        else:
            vm_error(f'Error on NEG between {operandtype}', self.pc - 1)

    def LT(self):
        righttype, rightval = self.POP()
        lefttype, leftval = self.POP()
        if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
            self.PUSH((TYPE_BOOL, leftval < rightval))
        elif lefttype == TYPE_STRING and righttype == TYPE_STRING:
            self.PUSH((TYPE_BOOL, leftval < rightval))
        else:
            vm_error(f'Error on LT between {lefttype} and {righttype}', self.pc - 1)

    def GT(self):
        righttype, rightval = self.POP()
        lefttype, leftval = self.POP()
        if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
            self.PUSH((TYPE_BOOL, leftval > rightval))
        elif lefttype == TYPE_STRING and righttype == TYPE_STRING:
            self.PUSH((TYPE_BOOL, leftval > rightval))
        else:
            vm_error(f'Error on GT between {lefttype} and {righttype}', self.pc - 1)

    def LE(self):
        righttype, rightval = self.POP()
        lefttype, leftval = self.POP()
        if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
            self.PUSH((TYPE_BOOL, leftval <= rightval))
        elif lefttype == TYPE_STRING and righttype == TYPE_STRING:
            self.PUSH((TYPE_BOOL, leftval <= rightval))
        else:
            vm_error(f'Error on LE between {lefttype} and {righttype}', self.pc - 1)

    def GE(self):
        righttype, rightval = self.POP()
        lefttype, leftval = self.POP()
        if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
            self.PUSH((TYPE_BOOL, leftval >= rightval))
        elif lefttype == TYPE_STRING and righttype == TYPE_STRING:
            self.PUSH((TYPE_BOOL, leftval >= rightval))
        else:
            vm_error(f'Error on GE between {lefttype} and {righttype}', self.pc - 1)

    def EQ(self):
        righttype, rightval = self.POP()
        lefttype, leftval = self.POP()
        if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
            self.PUSH((TYPE_BOOL, leftval == rightval))
        elif lefttype == TYPE_STRING and righttype == TYPE_STRING:
            self.PUSH((TYPE_BOOL, leftval == rightval))
        elif lefttype == TYPE_BOOL and righttype == TYPE_BOOL:
            self.PUSH((TYPE_BOOL, leftval == rightval))
        else:
            vm_error(f'Error on EQ between {lefttype} and {righttype}', self.pc - 1)

    def NE(self):
        righttype, rightval = self.POP()
        lefttype, leftval = self.POP()
        if lefttype == TYPE_NUMBER and righttype == TYPE_NUMBER:
            self.PUSH((TYPE_BOOL, leftval != rightval))
        elif lefttype == TYPE_STRING and righttype == TYPE_STRING:
            self.PUSH((TYPE_BOOL, leftval != rightval))
        elif lefttype == TYPE_BOOL and righttype == TYPE_BOOL:
            self.PUSH((TYPE_BOOL, leftval != rightval))
        else:
            vm_error(f'Error on NE between {lefttype} and {righttype}', self.pc - 1)

    def PRINT(self):
        valtype, val = self.POP()
        print(codecs.escape_decode(bytes(stringify(val), "utf-8"))[0].decode("utf-8"), end='')

    def PRINTLN(self):
        valtype, val = self.POP()
        print(codecs.escape_decode(bytes(stringify(val), "utf-8"))[0].decode("utf-8"), end='\n')

    def HALT(self):
        self.is_running = False
