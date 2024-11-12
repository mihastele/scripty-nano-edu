import sys
from tokens import *
from lexer import *
from parser import *

if __name__ == "__main__":
    if(len(sys.argv) < 2):
        raise SystemExit("Usage: python {} <file_path>".format(sys.argv[0]))
    
    file_path = sys.argv[1]

    with open(file_path, 'r') as file:
        source = file.read()
        # print(f"Source code:\n{source}")

        print("LEXER:")
        tokens = Lexer(source).tokenize()
        for token in tokens:
            print(token)

        print("Parsed AST:")
        ast = Parser(tokens).parse()
        print(ast)