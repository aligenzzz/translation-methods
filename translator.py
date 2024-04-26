from syntax_analyzer import FUNCTION_DEFINITION, VARIABLE_DECLARATION, ASSIGNMENT, TYPES, FUNCTION_PARAMETERS, \
                            VARIABLE, OPERATORS_TWO, OPERATORS_ONE, BLOCK_OF_CODE, LOOP_STATEMENT, CONDITION_STATEMENT, \
                            FUNCTION_CALLING, STRING_STATEMENT, STRUCTURE_DEFINITION, ARRAY_DECLARATION, \
                            DATASET, CHAR_STATEMENT, MEMBER_ACCESS, ARRAY_ELEMENT, IF_ELSE_STATEMENT, IF_STATEMENT, \
                            ELSE_STATEMENT, SWITCH_STATEMENT, CASE_STATEMENT, CASE_CONDITION, CASE_CODE, DEFAULT_STATEMENT, DEFAULT_CODE, \
                            FUNCTION_PARAMETERS, RETURN_STATEMENT
import re


class Translator():
    _result = []
    __tabs = 0
    __struct = None
    __switch = None
    __was_case = False
    __main = False
    
    @staticmethod
    def translate(root):
        for child in root.children:
            if child.name == BLOCK_OF_CODE and root.name == STRUCTURE_DEFINITION:                
                fields = [Translator.__get_element(field) for field in child.children]
                
                temp_line = Translator._result[-1]
                for field in fields:
                    temp_line += f'{field}, '
                Translator._result[-1] = temp_line[:-2] + '):'
                
                Translator.__tabs += 1
                
                for field in fields:
                    Translator._result.append(Translator.__tabs * '\t' + f'self.{field} = {field}')
                    
                Translator.__tabs -= 2
                continue
            
            if child.name == BLOCK_OF_CODE and root.name == SWITCH_STATEMENT:
                Translator.translate(child)
                continue
            
            if child.name in BLOCK_OF_CODE:
                Translator.__tabs += 1
                Translator.translate(child)
                Translator.__tabs -= 1
                continue
            
            if child.name == CASE_STATEMENT:
                Translator.translate(child)
                continue
            
            if child.name == DEFAULT_STATEMENT:
                Translator._result.append(Translator.__tabs * '\t' + f'else:')
                Translator.translate(child)
                continue
            
            if child.name == CASE_CONDITION:
                if not Translator.__was_case:
                    Translator._result.append(Translator.__tabs * '\t' + 
                                              f'if {Translator.__switch} == {Translator.__get_element(child.children[0])}:')
                    Translator.__was_case = True
                else:
                    Translator._result.append(Translator.__tabs * '\t' + 
                                              f'elif {Translator.__switch} == {Translator.__get_element(child.children[0])}:')
                continue
            
            if child.name in (CASE_CODE, DEFAULT_CODE):
                Translator.__tabs += 1
                Translator.translate(child)
                Translator.__tabs -= 1
                continue
            
            if child.name in (FUNCTION_DEFINITION, IF_ELSE_STATEMENT, IF_STATEMENT, SWITCH_STATEMENT):
                Translator.translate(child)
                continue
            
            if child.name == SWITCH_STATEMENT:
                Translator.translate(child)
                Translator.__was_case = False
                Translator.__switch = None
                continue
            
            if child.name == ELSE_STATEMENT:
                Translator._result.append(Translator.__tabs * '\t' + 'else:')
                Translator.translate(child)
                continue
           
            if root.name == FUNCTION_DEFINITION and child.name not in (*TYPES, FUNCTION_PARAMETERS):
                if child.name == 'main':
                    Translator.__main = True
                    Translator._result.append(Translator.__tabs * '\t' + 'if __name__ == \'__main__\':')
                else:
                    Translator._result.append(Translator.__tabs * '\t' + f'def {child.name}(')
                continue
            
            if child.name == FUNCTION_PARAMETERS:
                if len(child.children) == 0:
                    continue
                parameters = [Translator.__get_element(parameter) for parameter in child.children]
                temp_line = Translator._result[-1]
                for parameter in parameters:
                    temp_line += parameter + ', '
                Translator._result[-1] = temp_line[:-2] + '):'
                continue
            
            if child.name == STRUCTURE_DEFINITION:
                Translator.translate(child)
                continue
            
            if root.name == STRUCTURE_DEFINITION and child.name != BLOCK_OF_CODE:
                Translator._result.append(Translator.__tabs * '\t' + f'class {child.name}:')
                Translator.__tabs += 1
                Translator._result.append(Translator.__tabs * '\t' + f'def __init__(self, ')
                continue
            
            if child.name == ASSIGNMENT:
                if root.name != CONDITION_STATEMENT:
                    Translator._result.append(Translator.__tabs * '\t')
                statement = []
                Translator.__inorder_traversal(child, statement)   
                Translator._result[-1] += ' '.join(statement)                
                continue
            
            if child.name == RETURN_STATEMENT and not Translator.__main:
                Translator._result.append(Translator.__tabs * '\treturn ')
                Translator.translate(child)                
                continue
            
            if child.name in (VARIABLE_DECLARATION, ARRAY_DECLARATION):   
                Translator._result.append(Translator.__tabs * '\t' + f'{Translator.__get_element(child)} = None')  
                continue
            
            if child.name in (VARIABLE, MEMBER_ACCESS, CHAR_STATEMENT, STRING_STATEMENT):
                temp_line = Translator._result[-1]
                
                if temp_line.endswith(f'{root.name} ') or temp_line.endswith(f'{root.parent.name} '):
                    temp_line += f'{Translator.__get_element(child)}'
                else:
                    temp_line += f'{Translator.__get_element(child)} {root.name} '
       
                Translator._result[-1] = temp_line             
                continue  
            
            if root.name == RETURN_STATEMENT:          
                statement = []
                Translator.__inorder_traversal(child, statement)   
                Translator._result[-1] += ' '.join(statement)
                continue
            
            if child.name in (*OPERATORS_TWO, *OPERATORS_ONE):          
                statement = []
                Translator.__inorder_traversal(child, statement)   
                Translator._result.append(Translator.__tabs * '\t' + ' '.join(statement))
                
                Translator._result[-1] = Translator._result[-1].replace('++', '+= 1')
                Translator._result[-1] = Translator._result[-1].replace('--', '-= 1')
                continue
            
            if child.name == LOOP_STATEMENT:
                if len(child.children[0].children) == 3:
                    Translator._result.append(Translator.__tabs * '\t' + 'for ')
                else:   
                    Translator._result.append(Translator.__tabs * '\t' + 'while ')
                Translator.translate(child)
                continue
            
            if root.name == IF_STATEMENT and child.name == CONDITION_STATEMENT:
                Translator._result.append(Translator.__tabs * '\t' + 'if ')
                
                statement = []
                Translator.__inorder_traversal(child, statement)   
                
                temp_line = Translator._result[-1]
                temp_line += ' '.join(statement) + ':'
                Translator._result[-1] = temp_line 
                continue
            
            if root.name == LOOP_STATEMENT and child.name == CONDITION_STATEMENT:      
                statements = []        
                for condition in child.children:                      
                    statement = []
                    Translator.__inorder_traversal(condition, statement)   
                    statements.append(' '.join(statement))
                
                temp_line = Translator._result[-1]
                temp_line += ''.join(statements)
                
                if temp_line.startswith('\t' * Translator.__tabs + 'for'):     
                    match = re.search(r'for\s+(\w)\s*=', temp_line)
                    if match:
                        var_name = match.group(1)
                        
                    match = re.findall(rf'([^\s=><]+){var_name}', temp_line)
                    if match:
                        initial_value = match[0]
                        condition_value = match[1]
                        
                    match = re.search(r'[^=><\s]+$', temp_line)
                    if match:
                        modified_value = match.group(0)
                        
                    if modified_value == '++':
                        modified_value = '1'
                    elif modified_value == '--':
                        modified_value = '-1'
                        
                    temp_line = '\t' * Translator.__tabs + \
                                f'for {var_name} in range({initial_value}, {condition_value}, {modified_value})'
                
                temp_line += f':'
                Translator._result[-1] = temp_line 
                continue
            
            if root.name == SWITCH_STATEMENT and child.name == CONDITION_STATEMENT:
                Translator.__switch = Translator.__get_element(child.children[0])
                continue
            
            if child.name == FUNCTION_CALLING:
                Translator._result.append(Translator.__tabs * '\t' + Translator.__get_element(child))
                continue
                                                                
            
    @staticmethod
    def write():
        with open('result.txt', 'w') as file:
            for line in Translator._result:
                file.write(line + '\n')
                
    
    @staticmethod
    def __get_element(node):
        element_type = node.name
        
        if element_type in (ARRAY_DECLARATION, VARIABLE_DECLARATION):
            return node.children[1].name
        elif element_type == VARIABLE:
            return node.children[0].name
        elif element_type == CHAR_STATEMENT:
            return f'\'{node.children[0].name}\''
        elif element_type == STRING_STATEMENT:
            result = ''
            for part in node.children:
                result += part.name.replace('\'', '\\\'')
            return f'f\'{result}\''
        elif element_type == MEMBER_ACCESS:
            result = ''
            for part in node.children:
                result += part.name
            return f'{result}'
        elif element_type == ARRAY_ELEMENT:
            result = f'{node.children[0].name}'
            indexes = node.children[1].children
            for index in indexes:
                result += f'[{Translator.__get_element(index)}]'
            return result
        elif element_type == DATASET:
            if Translator.__struct is None:
                dataset = '['
                for element in node.children:
                    dataset += f'{Translator.__get_element(element)}, '
                dataset = dataset[:-2] + ']'
            else:
                dataset = f'{Translator.__struct}('
                for element in node.children:
                    dataset += f'{Translator.__get_element(element)}, '
                dataset = dataset[:-2] + ')' 
                Translator.__struct = None
            return dataset
        elif element_type == FUNCTION_CALLING:
            result = f'{node.children[0].name}('
            for argument in node.children[1].children:
                result += f'{Translator.__get_element(argument)}, '
            result = result[:-2] + ')' 
            if 'printf' in result:
                result = result.replace('printf', 'print')
                match = re.search(r',\s(.+)\)', result)
                if match:
                    result = re.sub(r'%[dcs]', f'{{{match.group(1)}}}', result)
                    result = re.sub(r',.+\)', '', result) + ')'    
            return result
        else:
            return element_type
    
    @staticmethod
    def __inorder_traversal(node, result: list):
        if node.children and node.name not in (DATASET, ARRAY_ELEMENT):
            Translator.__inorder_traversal(node.children[0], result)
            
        if node.name == VARIABLE_DECLARATION and node.children[0].name not in TYPES:
            Translator.__struct = node.children[0].name
                        
        if node.name in (ASSIGNMENT, *OPERATORS_TWO, *OPERATORS_ONE, VARIABLE_DECLARATION, VARIABLE,
                         ARRAY_DECLARATION, ARRAY_ELEMENT, CHAR_STATEMENT, STRING_STATEMENT, DATASET):
            result.append(Translator.__get_element(node))                      
        elif node.name not in (ASSIGNMENT, *OPERATORS_TWO, *OPERATORS_ONE, VARIABLE_DECLARATION, VARIABLE,
                               ARRAY_DECLARATION, ARRAY_ELEMENT, CHAR_STATEMENT, STRING_STATEMENT, DATASET) and \
                               node.parent.name in (ASSIGNMENT, *OPERATORS_TWO, *OPERATORS_ONE):
            result.append(Translator.__get_element(node))
                        
        if len(node.children) > 1 and node.name not in (DATASET, ARRAY_ELEMENT):
            Translator.__inorder_traversal(node.children[1], result)
    