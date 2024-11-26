import sys
def print_pretty_ast(ast_text):
    i = 0
    newline = False
    for ch in str(ast_text):
        if ch == '(':
            if not newline:
                print(end='')
            print(ch)
            i += 2
            newline = True
        elif ch == ')':
            if not newline:
                print()
            i -= 2
            newline = True
            print('  ' * i + ch)
        else:
            if newline:
                print('  ' * i, end='')
            print(ch, end='')
            newline = False

def stringify(val):
    if isinstance(val, bool) and val:
        return 'true'
    elif isinstance(val, bool):
        return 'false'
    elif isinstance(val, float) and val.is_integer():
        return str(int(val))
    else:
        return str(val)

def lexing_error(message, lineno):
    print(f"{Colors.RED}Error at line {lineno}: {message}{Colors.WHITE}")
    sys.exit(1)

def parse_error(message, lineno):
    print(f"{Colors.RED}Error at line {lineno}: {message}{Colors.WHITE}")
    sys.exit(1)

def runtime_error(message, lineno):
    print(f"{Colors.RED}Error at line {lineno}: {message}{Colors.WHITE}")
    sys.exit(1)

class Colors:
    WHITE = '\033[0m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'