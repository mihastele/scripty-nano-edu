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
        self.pc = 0
        self.sp = 0  # Stack pointer
        self.is_running = False

    def run(self, instructions):
        self.is_running = True

        # VM kernel
        while self.is_running:
            opcode, *args = instructions[self.pc]
            self.pc += 1
            # PC does not always increment by 1 in real processor scenarios
            # print(opcode, args)
            getattr(self, opcode)(*args)  # --> invoke the method that matched the opcode name

    def LABEL(self, name):
        pass

    def PUSH(self, value):
        self.stack.append(value)
        self.sp += 1  # Stack Pointer usually decrements

    def POP(self):
        self.sp -= 1
        return self.stack.pop()

    def NEG(self):
        pass

    def ADD(self):
        # Be careful the order
        rightT, rightV = self.POP()
        leftT, leftV = self.POP()  # leftT is the type, leftV is the value
        if (leftT == TYPE_NUMBER and rightT == TYPE_NUMBER):
            self.PUSH((TYPE_NUMBER, leftV + rightV))
        else:
            vm_error(f'Unsupported operator + between {leftT} and {rightT}.', self.pc)
        # TODO: String concat!

    def SUB(self):
        # Be careful the order
        rightT, rightV = self.POP()
        leftT, leftV = self.POP()  # leftT is the type, leftV is the value
        if (leftT == TYPE_NUMBER and rightT == TYPE_NUMBER):
            self.PUSH((TYPE_NUMBER, leftV - rightV))
        else:
            vm_error(f'Unsupported operator - between {leftT} and {rightT}.', self.pc)

    def MUL(self):
        # Be careful the order
        rightT, rightV = self.POP()
        leftT, leftV = self.POP()  # leftT is the type, leftV is the value
        if (leftT == TYPE_NUMBER and rightT == TYPE_NUMBER):
            self.PUSH((TYPE_NUMBER, leftV * rightV))
        else:
            vm_error(f'Unsupported operator * between {leftT} and {rightT}.', self.pc)

    def DIV(self):
        # Be careful the order
        rightT, rightV = self.POP()
        leftT, leftV = self.POP()  # leftT is the type, leftV is the value
        if (leftT == TYPE_NUMBER and rightT == TYPE_NUMBER):
            self.PUSH((TYPE_NUMBER, leftV / rightV))
        else:
            vm_error(f'Unsupported operator DIV between {leftT} and {rightT}.', self.pc)

    def PRINT(self):
        valT, val = self.POP()
        print(codecs.escape_decode(bytes(str(val), 'utf-8'))[0].decode('utf-8'), end='')

    def PRINTLN(self):
        valT, val = self.POP()
        print(codecs.escape_decode(bytes(str(val), 'utf-8'))[0].decode('utf-8'), end='\n')

    def HALT(self):
        self.is_running = False
