from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from utils import runtime_error

def repl():
    interpreter = Interpreter()
    
    print("Welcome to the Scripty REPL!")
    print("Type 'exit' to quit the REPL.")
    
    while True:
        try:
            # Read
            user_input = input(">>> ")
            
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            # Evaluate
            lexer = Lexer(user_input)
            tokens = lexer.tokenize()
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            result_type, result_value = interpreter.interpret(ast)
            
            # Print
            if result_type == 'TYPE_NUMBER':
                print(result_value)
            elif result_type == 'TYPE_STRING':
                print(f'"{result_value}"')
            elif result_type == 'TYPE_BOOL':
                print(str(result_value).lower())
            else:
                print(f"Unknown type: {result_type}")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    repl()