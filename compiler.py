from model import *
from tokens import *
from utils import *


TYPE_NUMBER = 'TYPE_NUMBER'  # Default to 64-bit float
TYPE_STRING = 'TYPE_STRING'  # String managed by the host language
TYPE_BOOL = 'TYPE_BOOL'  # true | false

class Compiler:
  def __init__(self):
    self.code = []

  def emit(self, instruction):
    self.code.append(instruction)

  # generate byte code
  def compile(self, node):
    if isinstance(node, Integer):
      value = (TYPE_NUMBER, float(node.value))
      self.emit(('PUSH', value))
    if isinstance(node, Float):
      value = (TYPE_NUMBER, float(node.value))
      self.emit(('PUSH', value))
    if isinstance(node, BinOp):
      self.compile(node.left)
      self.compile(node.right)
      if node.op.token_type == TOK_PLUS:
        self.emit(('ADD',))
    if isinstance(node, PrintStmt):
      self.compile(node.value)
      if node.end == '':
        self.emit(('PRINT',))
      else:
        self.emit(('PRINTLN',))
    if isinstance(node, Stmts):
      for stmt in node.stmts:
        self.compile(stmt)

  def compile_code(self, root_node):
    self.compile(root_node)
    return self.code
