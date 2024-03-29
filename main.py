from lexical_analyzer import LexicalAnalyzer
from syntax_analyzer import SyntaxAnalyzer, print_tree
from semantic_analyzer import SemanticAnalyzer
from tabulate import tabulate
from colorama import Fore

def if_error(content):
    if content[1] == 'Error':
        return (Fore.RED + str(content[0]) + Fore.RESET,
                Fore.RED + content[1] + Fore.RESET,
                Fore.RED + content[2] + Fore.RESET)
    return content

if __name__ == '__main__':
    with open('text_for_semantic.txt', 'r', encoding='utf-8') as file:
        text = file.read()
    
    # for lexical analyzer
    result = LexicalAnalyzer.analyze(text)
    # headers = ['ID', 'Token', 'Value']        
    # print(tabulate(list(map(if_error, result)), headers=headers))

    # for syntax analyzer
    result = SyntaxAnalyzer.analyze(result)
    # print_tree(result)

    # for semantic analyzer
    result = SemanticAnalyzer.analyze(result)
    errors = '\n'.join(result)
    errors = f'{Fore.RED}{errors}{Fore.RESET}'
    print(errors)
