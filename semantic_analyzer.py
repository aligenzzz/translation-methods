from anytree import RenderTree
from syntax_analyzer import (VARIABLE_DECLARATION, VARIABLE, CHAR_STATEMENT, 
                             ARRAY_DECLARATION, FUNCTION_DEFINITION, FUNCTION_CALLING, 
                             ASSIGNMENT, ARRAY_ELEMENT, CONDITION_STATEMENT, CASE_CONDITION,
                             OPERATORS_TWO, LOOP_STATEMENT, TYPES)


class SemanticAnalyzer():
    @staticmethod
    def analyze(root):
        result = []

        variables = []
        arrays = []
        functions = []

        for _, _, node in RenderTree(root):
            if node.name == VARIABLE_DECLARATION:
                variables.append((node.children[0].name, node.children[1].name))
                continue

            if node.name == ARRAY_DECLARATION:
                arrays.append((node.children[0].name, node.children[1].name, node.children[2].children[0].name))
                array_name = node.children[1].name
                array_size = node.children[2].children[0].name

                if not SemanticAnalyzer._check_type('int', array_size):
                    result.append(f'Invalid type of array size: {array_name}, {array_size} -> int')
                    continue
                continue

            if node.name == FUNCTION_DEFINITION:
                parameters_types = [p.children[0] for p in node.children[2].children]
                functions.append((node.children[0].name, node.children[1].name, parameters_types))
                continue

            if node.name == FUNCTION_CALLING and node.children[0].name != 'printf':
                function_name = node.children[0].name
                functions_names = [f[1] for f in functions]

                if function_name not in functions_names:
                    result.append(f'Not declarated function: {function_name}')
                    continue

                function_arguments = node.children[1].children
                function = next((f for f in functions if f[1] == function_name), None)

                if len(function_arguments) != len(function[2]):
                    result.append(f'Invalid count of arguments: {function_name}, ' \
                                  f'{len(function_arguments)} -> {len(function[2])}')
                    continue

                for i, arg in enumerate(function_arguments):
                    type_ = function[2][i].name
                    if not SemanticAnalyzer._check_type(type_, arg.name):
                        result.append(f'Invalid type of argument: {function_name}, {arg.name} -> {type_}')
                continue
            
            if node.name == VARIABLE:
                variables_names = [v[-1] for v in variables]
                if node.children[0].name not in variables_names:
                    result.append(f'Not declarated variable: {node.children[0].name}')
                continue                

            if node.name == CHAR_STATEMENT:
                children_names = [child.name for child in node.children]
                char = ''.join(children_names)
                if len(char) != 1 and char not in ('\\n', '\\t'):
                    result.append(f'Invalid char statement: {char}')
                continue

            if node.name == ASSIGNMENT and node.children[0].name == ARRAY_DECLARATION:
                array_name = node.children[0].children[1].name
                array_type = node.children[0].children[0].name

                dataset = [v.name for v in node.children[1].children]

                for val in dataset:
                    if not SemanticAnalyzer._check_type(array_type, val):
                        result.append(f'Invalid type of array element: {array_name}, {val} -> {array_type}')
                continue

            if node.name == ASSIGNMENT and node.children[0].name == ARRAY_ELEMENT:
                array_name = node.children[0].children[0].name
                array_index = node.children[0].children[1].children[0].name

                arrays_names = [a[1] for a in arrays]
                if array_name not in arrays_names:
                    result.append(f'Not declarated array: {array_name}')
                    continue

                if not SemanticAnalyzer._check_type('int', array_index):
                    result.append(f'Invalid type of array index: {array_name}, {array_index} -> int')
                    continue

                array_index = int(array_index)
                array = next((a for a in arrays if a[1] == array_name), None)
                if array_index < 0 or array_index >= int(array[2]):
                    result.append(f'Invalid array index: {array_name}, size = {array[2]}, but index = {array_index}')
                    continue

                value = node.children[1].name
                if not SemanticAnalyzer._check_type(array[0], value):
                    result.append(f'Invalid type of array element: {array_name}, {val} -> {array_type}')
                    continue  

            if node.name == CONDITION_STATEMENT and node.parent.name != LOOP_STATEMENT:
                if node.children[0].name == ASSIGNMENT:
                    result.append('Invalid operator in condition: = -> ==')
                    continue   

            if node.name == CASE_CONDITION:
                if node.children[0].name == VARIABLE:
                    result.append(f'Invalid condition in case: {node.children[0].name} -> literal')
                    continue   

            if node.name == ASSIGNMENT and node.children[0].name == VARIABLE_DECLARATION and node.children[1].is_leaf:
                variable_type = node.children[0].children[0].name
                variable_name = node.children[0].children[1].name
                variable_value = node.children[1].name

                if not SemanticAnalyzer._check_type(variable_type, variable_value):
                    result.append(f'Invalid type for variable: {variable_name}, {variable_value} -> {variable_type}')
                    continue

            if node.name == ASSIGNMENT and node.children[0].name == VARIABLE and node.children[1].is_leaf:
                variable_name = node.children[0].children[0].name
                variable_value = node.children[1].name

                variable = next((v for v in variables if v[-1] == variable_name), None)
                if variable is None:
                    continue

                variable_type = variable[0]
                if not SemanticAnalyzer._check_type(variable_type, variable_value):
                    result.append(f'Invalid type for variable: {variable_name}, {variable_value} -> {variable_type}')
                    continue

            if node.name in OPERATORS_TWO and node.children[0].name == VARIABLE and node.children[1].is_leaf:
                variable_name = node.children[0].children[0].name
                variable_value = node.children[1].name

                variable = next((v for v in variables if v[-1] == variable_name), None)
                if variable is None:
                    continue

                variable_type = variable[0]
                if not SemanticAnalyzer._check_type(variable_type, variable_value):
                    result.append(f'Invalid operation for variable: {variable_name}')
                    continue

            if node.name in TYPES and node.parent.name not in (VARIABLE_DECLARATION, ARRAY_DECLARATION, FUNCTION_DEFINITION):
                result.append(f'Invalid type in: {node.parent.name}')
                continue
                
        return result
    
    @staticmethod
    def _check_type(type_: str, value: str) -> bool:
        try:
            if type_ in ('int', 'long', 'short'):
                int(value)
                return True
            elif type_ in ('float', 'double'):
                float(value)
                return True
            elif type_ == 'char' and value == CHAR_STATEMENT:
                return True
            else:
                return False
        except Exception:
            return False
