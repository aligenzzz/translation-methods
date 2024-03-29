from constants import KEYWORDS, INVALID_OPERATORS, OPERATORS, SPECIAL_SYMBOLS, SEPARATORS
import re

class LexicalAnalyzer:
    # enum of all tokens
    TOKENS = { 
        'Keyword', 'Identifier', 'Operator', 'Literal', 
        'Separator', 'Special symbol', 'Unknown', 'Error'
    }

    @staticmethod
    def analyze(text: str):    
        text = LexicalAnalyzer._remove_comments(text)

        result = []
        position = 0
        ID = 1

        while position < len(text):
            current_char = text[position]

            if current_char in SPECIAL_SYMBOLS:
                result.append((ID, 'Special symbol', current_char))

                ID += 1
                position += 1
                continue

            if current_char.isspace():
                # if len(result) == 0 or result[-1][1] != 'Separator':
                #     result.append((ID, 'Separator', ' '))
                #     ID += 1

                position += 1
                continue

            if current_char.isdigit():
                literal = LexicalAnalyzer._read_while_with_two(text, position, 
                                                    lambda c: c.isdigit() or c in ['.','E','E'],
                                                    lambda c, next_c: c in ['E','e'] and next_c in ['+','-'])   
                # Error 1
                if literal.count('.') > 1:
                    result.append((ID, 'Error', literal))
                else:
                    result.append((ID, 'Literal', literal))

                ID += 1         
                position += len(literal)
                continue

            if current_char.isalpha():
                identifier = LexicalAnalyzer._read_while_with_one(text, position, lambda c: c.isalnum() or c == '_')

                # Error 2
                if len(result) > 1 and result[-1][2].isnumeric():
                    result[-1] = (result[-1][0], 'Error', result[-1][2] + identifier)
                    position += len(identifier)
                    continue

                if identifier in KEYWORDS:
                    result.append((ID, 'Keyword', identifier)) 
                else:
                    result.append((ID, 'Identifier', identifier))

                ID += 1
                position += len(identifier)
                continue

            if len(result) > 1 and result[-1][2] == 'include' and current_char == '<':
                identifier = LexicalAnalyzer._read_while_with_one(text, position, lambda c: c.isalpha() or c in ['.', '>', '<', '"'])
                result.append((ID, 'Identifier', identifier))

                ID += 1
                position += len(identifier)
                continue     

            if current_char == '"' or current_char == '\'':
                result.append((ID, 'Separator', current_char))
                ID += 1
                position += 1

                literal = LexicalAnalyzer._read_while_with_one(text, position, lambda c: c != current_char)

                parts = re.split(r'(?<!\\)(\\n|\\t)', literal)
                while '' in parts:
                    parts.remove('')

                for part in parts:
                    if part in ['\\n', '\\t']:
                        result.append((ID, 'Separator', part))   
                    else:
                        result.append((ID, 'Literal', part))
                    ID += 1

                result.append((ID, 'Separator', current_char))
                ID += 1
                position += len(literal) + 1

                continue

            if current_char in OPERATORS:
                operator = LexicalAnalyzer._read_while_with_one(text, position, lambda c: c in OPERATORS)
                
                # Error 3
                if len(result) > 1 and result[-1][2] + operator in INVALID_OPERATORS:
                    result[-1] = (result[-1][0], 'Error', result[-1][2] + operator)
                    position += len(operator)
                    continue

                result.append((ID, 'Operator', operator))

                ID += 1
                position += len(operator)
                continue  

            # Error 4
            if current_char not in SEPARATORS:
                result.append((ID, 'Error', current_char))
            else:
                result.append((ID, 'Separator', current_char))
            ID += 1
            position += 1

        return result

    @staticmethod
    def _read_while_with_one(text, start, condition):
        end = start
        while end < len(text) and condition(text[end]):
            end += 1
        return text[start:end]
    
    @staticmethod
    def _read_while_with_two(text, start, condition1, condition2):
        end = start
        while end < len(text) - 1 and condition1(text[end]):
            if condition2(text[end], text[end + 1]):
                end += 2
                continue
            end += 1
        return text[start:end]
    
    @staticmethod
    def _remove_comments(text):
        in_comment = False
        in_line_comment = False
        result = ''
        i = 0
        while i < len(text):
            if not in_comment and text[i:i+2] == '/*':
                in_comment = True
                i += 2
            elif in_comment and text[i:i+2] == '*/':
                in_comment = False
                i += 2
            elif not in_comment and text[i:i+2] == '//':
                in_line_comment = True
                i += 2
            elif in_line_comment and text[i] == '\n':
                in_line_comment = False
                i += 1
            elif not in_comment and not in_line_comment:
                result += text[i]
                i += 1
            else:
                i += 1
        return result          
