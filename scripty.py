import sys
from tokens import *
from lexer import *
from parser import *
from utils import *
from interpreter import *

if __name__ == "__main__":
    if(len(sys.argv) < 2):
        raise SystemExit("Usage: python {} <file_path>".format(sys.argv[0]))
    
    file_path = sys.argv[1]

    with open(file_path, 'r') as file:
        source = file.read()
        # print(f"Source code:\n{source}")

        print(f"{Colors.GREEN}LEXER:{Colors.WHITE}")
        tokens = Lexer(source).tokenize()
        for token in tokens:
            print(token)

        print(f"{Colors.GREEN}Parsed AST:{Colors.WHITE}")
        ast = Parser(tokens).parse()
        print_pretty_ast(str(ast))

        interpreter = Interpreter()
        interpreter.interpret_ast(ast)