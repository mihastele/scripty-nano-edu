import sys
from tokens import *
from lexer import *
from parser import *
from utils import *
from interpreter import *
from compiler import *
from vm import *

VERBOSE = False

if __name__ == "__main__":
    if(len(sys.argv) < 2):
        raise SystemExit("Usage: python {} <file_path>".format(sys.argv[0]))
    
    file_path = sys.argv[1]

    with open(file_path, 'r') as file:
        source = file.read()
        # print(f"Source code:\n{source}")

        tokens = Lexer(source).tokenize()
        ast = Parser(tokens).parse()
        if VERBOSE:
            print(f"{Colors.GREEN}LEXER:{Colors.WHITE}")
            for token in tokens:
                print(token)
            print(f"{Colors.GREEN}Parsed AST:{Colors.WHITE}")
            print_pretty_ast(str(ast))

        # interpreter = Interpreter()
        # interpreter.interpret_ast(ast)


        if VERBOSE:
            print(f"{Colors.GREEN}*******************{Colors.WHITE}")
            print(f"{Colors.GREEN}Code generation:{Colors.WHITE}")
            print(f"{Colors.GREEN}*******************{Colors.WHITE}")

        compiler = Compiler()
        code = compiler.compile_code(ast)

        print(code)

        vm = VM()
        vm.run(code)