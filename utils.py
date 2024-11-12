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

                