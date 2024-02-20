from lexical_analyzer import LexicalAnalyzer
from tabulate import tabulate
from colorama import Fore

def if_error(content):
    if content[1] == 'Error':
        return (Fore.RED + str(content[0]) + Fore.RESET,
                Fore.RED + content[1] + Fore.RESET,
                Fore.RED + content[2] + Fore.RESET)
    return content

if __name__ == '__main__':
    with open('text.txt', 'r') as file:
        text = file.read()
    
    result = LexicalAnalyzer.analyze(text)

    headers = ['ID', 'Token', 'Value']        
    print(tabulate(list(map(if_error, result)), headers=headers))
