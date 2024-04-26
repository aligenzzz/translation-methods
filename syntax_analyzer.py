from anytree import Node, RenderTree
from constants import TYPES, SPECIAL_SYMBOLS

LIB_CONNECTION = 'lib connection'
STRUCTURE_DEFINITION = 'structure definition'
FUNCTION_DEFINITION = 'function definition'
FUNCTION_PARAMETERS = 'parameters'
FUNCTION_CALLING = 'function calling'
FUNCTION_ARGUMENTS = 'arguments'
BLOCK_OF_CODE = 'block of code'
RETURN_STATEMENT = 'return'
STRING_STATEMENT = 'string'
CHAR_STATEMENT = 'char st.'
IF_ELSE_STATEMENT = 'if-else'
IF_STATEMENT = 'if'
ELSE_STATEMENT = 'else'
CONDITION_STATEMENT = 'condition'
VARIABLE_DECLARATION = 'variable declaration'
VARIABLE = 'variable'
ARRAY_DECLARATION = 'array'
ARRAY_SIZE = 'size'
ARRAY_ELEMENT = 'array element'
ARRAY_INDEX = 'index'
ASSIGNMENT = '='
DATASET = 'dataset'
MEMBER_ACCESS = 'member access'
LOOP_STATEMENT = 'loop'
SWITCH_STATEMENT = 'switch'
CASE_STATEMENT = 'case'
CASE_CONDITION = 'case condition'
CASE_CODE = 'case code'
DEFAULT_STATEMENT = 'default'
DEFAULT_CODE = 'default code'

OPERATORS_TWO = {
    '+', '-', '*', '/', '%', '&', '|', '^', '~',
    '==', '!=', '>', '<', '>=', '<=', '&&', '||', '<<', '>>', 
    '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^='
}
OPERATORS_ONE = {
    '++', '--'
}

IDENTIFIER_TOKEN = 'Identifier'
KEYWORD_TOKEN = 'Keyword'
OPERATOR_TOKEN = 'Operator'
LITERAL_TOKEN = 'Literal'
SEPARATOR_TOKEN = 'Separator'
SPECIAL_TOKEN = 'Special symbol'

class SyntaxAnalyzer:  
    @staticmethod
    def analyze(tokens):
        root = Node('program')
        current_node = root  
        n = len(tokens)      

        for id, token_type, token in tokens:
            id -= 1
            
            if token == '}' and current_node.name in OPERATORS_TWO and current_node.name.endswith('='):
                current_node = current_node.parent

            # lib connection
            if token in SPECIAL_SYMBOLS:
                node = Node(LIB_CONNECTION, parent=current_node)
                current_node = node
                Node(token, parent=current_node)
                continue
            if current_node.name == LIB_CONNECTION and token_type == IDENTIFIER_TOKEN:
                node = Node(token, parent=current_node)
                current_node = current_node.parent
                continue

            # structure definition
            if token == 'struct' and current_node.name != BLOCK_OF_CODE:
                node = Node(STRUCTURE_DEFINITION, parent=current_node)
                current_node = node
                continue     
            if token == '}' and current_node.parent.name == STRUCTURE_DEFINITION:
                current_node = current_node.parent
                continue
            if token == ';' and current_node.name == STRUCTURE_DEFINITION:
                current_node = current_node.parent
                continue
            
            # function definition
            if (id + 2) < n and token in TYPES and tokens[id + 1][1] == IDENTIFIER_TOKEN and tokens[id + 2][2] == '(':
                node = Node(FUNCTION_DEFINITION, parent=current_node)
                current_node = node
                Node(token, parent=current_node)
                continue
            if token == '(' and current_node.name == FUNCTION_DEFINITION:
                node = Node(FUNCTION_PARAMETERS, parent=current_node)
                current_node = node
                continue
            if token == ')' and current_node.name == FUNCTION_PARAMETERS:
                current_node = current_node.parent
                continue
            if token == '}' and current_node.parent.name == FUNCTION_DEFINITION:
                current_node = current_node.parent
                current_node = current_node.parent
                continue
            if token == '}' and current_node.name == BLOCK_OF_CODE and current_node.parent.name == FUNCTION_PARAMETERS: 
                current_node = current_node.parent
                current_node = current_node.parent
                current_node = current_node.parent
                continue
            
            # array declaration
            if (id + 2) < n and token in TYPES and tokens[id + 1][1] == IDENTIFIER_TOKEN and tokens[id + 2][2] == '[':
                node = Node(ARRAY_DECLARATION, parent=current_node)
                current_node = node
                Node(token, parent=current_node)
                continue
            if token == '[' and current_node.name == ARRAY_DECLARATION:
                node = Node(ARRAY_SIZE, parent=current_node)
                current_node = node
                continue
            if token == ']' and current_node.name == ARRAY_SIZE and tokens[id + 1][2] != '[':
                current_node = current_node.parent
                continue
            if token == ';' and current_node.name == ARRAY_DECLARATION:
                current_node = current_node.parent
                continue

            # variable declaration
            if (id + 2) < n and token == 'const' and tokens[id + 2][1] == IDENTIFIER_TOKEN:
                node = Node(VARIABLE_DECLARATION, parent=current_node)
                current_node = node
                Node(token, parent=current_node)
                continue
            if (id + 1) < n and token in TYPES and tokens[id + 1][1] == IDENTIFIER_TOKEN and current_node.name != VARIABLE_DECLARATION:
                node = Node(VARIABLE_DECLARATION, parent=current_node)
                current_node = node
                Node(token, parent=current_node)
                continue
            if (id + 1) < n and token_type == IDENTIFIER_TOKEN and tokens[id + 1][1] == IDENTIFIER_TOKEN:
                node = Node(VARIABLE_DECLARATION, parent=current_node)
                current_node = node
                Node(token, parent=current_node)
                continue
            if token == ';' and current_node.name == VARIABLE_DECLARATION:
                current_node = current_node.parent
                continue 
            if token in ',' and current_node.name == VARIABLE_DECLARATION and current_node.parent.name == FUNCTION_PARAMETERS:
                current_node = current_node.parent
                continue 
            if token in ')' and current_node.name == VARIABLE_DECLARATION and current_node.parent.name == FUNCTION_PARAMETERS:
                current_node = current_node.parent
                current_node = current_node.parent
                continue 
            if token == ',' and current_node.name == VARIABLE_DECLARATION:
                var_type = current_node.children[0].name
                current_node = current_node.parent
                node = Node(VARIABLE_DECLARATION, parent=current_node)
                current_node = node
                Node(var_type, parent=current_node)
                continue
            
            # assignment
            if token == '=' and current_node.name in (ARRAY_DECLARATION, VARIABLE_DECLARATION):
                temp_node = current_node
                current_node = current_node.parent
                node = Node(ASSIGNMENT, parent=current_node)
                temp_node.parent = node
                current_node = node
                continue 
            if token == '=':
                temp_node = current_node.children[-1]
                node = Node(ASSIGNMENT, parent=current_node)
                temp_node.parent = node
                current_node = node
                continue 
            if token in OPERATORS_TWO and token.endswith('='):
                temp_node = current_node.children[-1]
                node = Node(token, parent=current_node)
                temp_node.parent = node
                current_node = node
                continue 
            if token == ';' and current_node.name == ASSIGNMENT:
                current_node = current_node.parent
                continue 

            # other operators (two)
            if token in OPERATORS_TWO and current_node.name in (ARRAY_DECLARATION, VARIABLE_DECLARATION):
                temp_node = current_node
                current_node = current_node.parent
                node = Node(token, parent=current_node)
                temp_node.parent = node
                current_node = node
                continue 
            if token in OPERATORS_TWO and token_type == OPERATOR_TOKEN:
                temp_node = current_node.children[-1]
                node = Node(token, parent=current_node)
                temp_node.parent = node
                current_node = node
                continue 
            if current_node.name in OPERATORS_TWO and len(current_node.children) == 1 and \
               token_type == LITERAL_TOKEN and not current_node.name.endswith('='):
                Node(token, parent=current_node)
                current_node = current_node.parent
                continue 
            if current_node.name in OPERATORS_TWO and len(current_node.children) == 1 and \
               token_type == IDENTIFIER_TOKEN and not current_node.name.endswith('=') and tokens[id + 1][2] != '[':
                node = Node(VARIABLE, parent=current_node)
                Node(token, parent=node)
                current_node = current_node.parent
                continue
            if token == ';' and current_node.name in OPERATORS_TWO:
                current_node = current_node.parent
                continue 

            # other operators (one)
            if (id - 1) >= 0 and tokens[id - 1][1] in (LITERAL_TOKEN, IDENTIFIER_TOKEN) and token in OPERATORS_ONE:
                temp_node = current_node.children[-1]
                node = Node(token, parent=current_node)
                temp_node.parent = node
                continue 
            if token in OPERATORS_ONE and current_node.name not in OPERATORS_ONE:
                node = Node(token, parent=current_node)
                current_node = node
                continue
            if token_type in (LITERAL_TOKEN, IDENTIFIER_TOKEN) and current_node.name in OPERATORS_ONE:
                Node(token, parent=current_node)
                current_node = current_node.parent
                current_node = current_node.parent
                continue

            # dataset
            if token == '{' and current_node.name in (ASSIGNMENT, DATASET):
                node = Node(DATASET, parent=current_node)
                current_node = node
                continue
            if token == ',' and current_node.name == DATASET:
                continue
            if token == '}' and current_node.name == DATASET:
                current_node = current_node.parent
                continue
            
            # if-else / if / else statements
            if token == 'if':
                node = Node(IF_ELSE_STATEMENT, parent=current_node)
                current_node = node
                node = Node(IF_STATEMENT, parent=current_node)
                current_node = node
                continue
            if token == '(' and current_node.name == IF_STATEMENT:
                node = Node(CONDITION_STATEMENT, parent=current_node)
                current_node = node
                continue
            if token == '}' and current_node.parent.name == IF_STATEMENT:
                current_node = current_node.parent
                current_node = current_node.parent
                if (id + 1) < n and tokens[id + 1][2] != ELSE_STATEMENT:
                    current_node = current_node.parent
                continue
            if token == 'else':
                node = Node(ELSE_STATEMENT, parent=current_node)
                current_node = node
                continue
            if token == '}' and current_node.parent.name == ELSE_STATEMENT:
                current_node = current_node.parent
                current_node = current_node.parent
                current_node = current_node.parent
                continue

            # function calling
            if (id + 1) < n and token_type == IDENTIFIER_TOKEN and tokens[id + 1][2] == '(' and \
               current_node.name in (BLOCK_OF_CODE, CASE_CODE, DEFAULT_CODE, ASSIGNMENT, *OPERATORS_TWO):
                node = Node(FUNCTION_CALLING, parent=current_node)
                current_node = node
                Node(token, parent=current_node)
                continue
            if token == '(' and current_node.name == FUNCTION_CALLING:
                node = Node(FUNCTION_ARGUMENTS, parent=current_node)
                current_node = node
                continue
            if token == ')' and current_node.name == FUNCTION_ARGUMENTS:
                current_node = current_node.parent
                current_node = current_node.parent
                continue
            if token == ',' and current_node.name == FUNCTION_ARGUMENTS:
                continue
            
            # string statement
            if token == '"' and current_node.name != STRING_STATEMENT:
                node = Node(STRING_STATEMENT, parent=current_node)
                current_node = node
                continue
            if token == '"' and current_node.name == STRING_STATEMENT:
                current_node = current_node.parent
                continue

            # char statement
            if token == '\'' and current_node.name != CHAR_STATEMENT:
                node = Node(CHAR_STATEMENT, parent=current_node)
                current_node = node
                continue
            if token == '\'' and current_node.name == CHAR_STATEMENT:
                current_node = current_node.parent
                continue

            # member access
            if (id + 1) < n and token_type == IDENTIFIER_TOKEN and tokens[id + 1][2] == '.':
                node = Node(MEMBER_ACCESS, parent=current_node)
                current_node = node
                Node(token, parent=current_node)
                continue
            if (id - 1) >= 0 and token_type == IDENTIFIER_TOKEN and tokens[id - 1][2] == '.':
                node = Node(token, parent=current_node)
                current_node = current_node.parent
                continue

            # return statement
            if token == 'return':
                node = Node(RETURN_STATEMENT, parent=current_node)
                current_node = node
                continue
            if token == ';' and current_node.name == RETURN_STATEMENT:
                current_node = current_node.parent
                continue
            
            # loop statement
            if token == 'for' or token == 'while':
                node = Node(LOOP_STATEMENT, parent=current_node)
                current_node = node
                continue
            if token == '(' and current_node.name == LOOP_STATEMENT:
                node = Node(CONDITION_STATEMENT, parent=current_node)
                current_node = node
                continue
            if token == '}' and current_node.parent.name == LOOP_STATEMENT:
                current_node = current_node.parent
                current_node = current_node.parent
                continue
            if token == ')' and current_node.name in (*OPERATORS_TWO, '=') and current_node.parent.name == CONDITION_STATEMENT:
                current_node = current_node.parent
                current_node = current_node.parent
                continue

            # array element
            if (id - 1) >= 0 and token == '[' and tokens[id - 1][1] == IDENTIFIER_TOKEN and current_node.name != ARRAY_INDEX:
                temp_node = current_node.children[-1]
                temp_node = temp_node.children[0]
                current_node.children = current_node.children[:len(current_node.children) - 1]
                node = Node(ARRAY_ELEMENT, parent=current_node)
                temp_node.parent = node
                current_node = node
                continue 
            if token_type == LITERAL_TOKEN and current_node.name == ARRAY_ELEMENT:
                node = Node(ARRAY_INDEX, parent=current_node)
                Node(token, parent=node)
                current_node = node
                continue
            if token_type == IDENTIFIER_TOKEN and current_node.name == ARRAY_ELEMENT:
                node = Node(ARRAY_INDEX, parent=current_node)
                identifier = Node(VARIABLE, parent=node)
                Node(token, parent=identifier)
                current_node = node
                continue
            if token == ']' and current_node.name == ARRAY_INDEX and tokens[id + 1][2] != '[':
                current_node = current_node.parent
                current_node = current_node.parent
                continue

            # switch statement
            if token == 'switch':
                node = Node(SWITCH_STATEMENT, parent=current_node)
                current_node = node
                continue
            if token == '(' and current_node.name == SWITCH_STATEMENT:
                node = Node(CONDITION_STATEMENT, parent=current_node)
                current_node = node
                continue
            if token == 'case':
                node = Node(CASE_STATEMENT, parent=current_node)
                current_node = node
                node = Node(CASE_CONDITION, parent=current_node)
                current_node = node
                continue
            if token == ':' and current_node.name == CASE_CONDITION:
                current_node = current_node.parent
                node = Node(CASE_CODE, parent=current_node)
                current_node = node
                continue
            if token == 'break' and current_node.name == CASE_CODE:
                current_node = current_node.parent
                current_node = current_node.parent
                continue 
            if token == 'default':
                node = Node(DEFAULT_STATEMENT, parent=current_node)
                current_node = node
                continue
            if token == ':' and current_node.name == DEFAULT_STATEMENT:
                node = Node(DEFAULT_CODE, parent=current_node)
                current_node = node
                continue
            if token == '}' and current_node.name == DEFAULT_CODE:
                current_node = current_node.parent
                current_node = current_node.parent
                current_node = current_node.parent
                current_node = current_node.parent
                continue

            if token == '{': 
                node = Node(BLOCK_OF_CODE, parent=current_node)
                current_node = node
                continue
            if token == ')' and current_node.name == CONDITION_STATEMENT:
                current_node = current_node.parent
                continue
            if token == ';' and current_node.name == CONDITION_STATEMENT:
                continue

            # variable
            if token_type == IDENTIFIER_TOKEN and current_node.name not in (VARIABLE_DECLARATION, STRUCTURE_DEFINITION,
                                                                            ARRAY_DECLARATION, FUNCTION_DEFINITION):
                node = Node(VARIABLE, parent=current_node)
                Node(token, parent=node)
                continue

            if token not in (';', 'struct', '[', ']'):
                node = Node(token, parent=current_node)     
                
        return root
                

def print_tree(root):
    for pre, _, node in RenderTree(root):
        print('%s%s' % (pre, node.name))
