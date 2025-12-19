"""
Тесты для лексического анализатора.
"""

import pytest
from src.lexer import Lexer, LexerError, TokenType


class TestLexerNumbers:
    """Тесты распознавания чисел."""
    
    def test_integer(self):
        lexer = Lexer("42")
        tokens = lexer.tokenize()
        assert len(tokens) == 2  # NUMBER + EOF
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 42.0
        
    def test_float_with_decimal(self):
        lexer = Lexer("3.14159")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 3.14159
        
    def test_float_ending_with_dot(self):
        lexer = Lexer("10.")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == 10.0
        
    def test_multiple_numbers(self):
        lexer = Lexer("1.5 2.0 3.")
        tokens = lexer.tokenize()
        assert tokens[0].value == 1.5
        assert tokens[1].value == 2.0
        assert tokens[2].value == 3.0


class TestLexerNames:
    """Тесты распознавания имён."""
    
    def test_simple_name(self):
        lexer = Lexer("variable")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NAME
        assert tokens[0].value == "variable"
        
    def test_name_with_numbers(self):
        lexer = Lexer("var123")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NAME
        assert tokens[0].value == "var123"
        
    def test_name_with_underscore(self):
        lexer = Lexer("my_var_2")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NAME
        assert tokens[0].value == "my_var_2"
        
    def test_uppercase_not_allowed(self):
        with pytest.raises(LexerError):
            lexer = Lexer("MyVar")
            lexer.tokenize()
            
    def test_sort_keyword(self):
        lexer = Lexer("sort")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.SORT


class TestLexerOperators:
    """Тесты распознавания операторов."""
    
    def test_brackets(self):
        lexer = Lexer("[ ]")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LBRACKET
        assert tokens[1].type == TokenType.RBRACKET
        
    def test_braces(self):
        lexer = Lexer("{ }")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.LBRACE
        assert tokens[1].type == TokenType.RBRACE
        
    def test_assignment(self):
        lexer = Lexer("<-")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.ASSIGN
        
    def test_equals(self):
        lexer = Lexer("=")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.EQUALS
        
    def test_arithmetic(self):
        lexer = Lexer("+ -")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.PLUS
        assert tokens[1].type == TokenType.MINUS


class TestLexerComments:
    """Тесты обработки комментариев."""
    
    def test_single_line_comment(self):
        lexer = Lexer("x :: это комментарий\ny")
        tokens = lexer.tokenize()
        assert len(tokens) == 3  # x, y, EOF
        assert tokens[0].value == "x"
        assert tokens[1].value == "y"
        
    def test_multi_line_comment(self):
        lexer = Lexer("a <# это\nмного\nстрочный\nкомментарий #> b")
        tokens = lexer.tokenize()
        assert len(tokens) == 3  # a, b, EOF
        assert tokens[0].value == "a"
        assert tokens[1].value == "b"
        
    def test_unclosed_multiline_comment(self):
        with pytest.raises(LexerError) as exc_info:
            lexer = Lexer("<# незакрытый комментарий")
            lexer.tokenize()
        assert "Незакрытый" in str(exc_info.value)


class TestLexerComplex:
    """Тесты сложных конструкций."""
    
    def test_array_declaration(self):
        lexer = Lexer("arr <- [ 1.0; 2.0; 3.0 ];")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.NAME
        assert tokens[1].type == TokenType.ASSIGN
        assert tokens[2].type == TokenType.LBRACKET
        assert tokens[3].type == TokenType.NUMBER
        
    def test_dict_declaration(self):
        lexer = Lexer("cfg <- { key = 1.0 };")
        tokens = lexer.tokenize()
        assert tokens[0].value == "cfg"
        assert tokens[1].type == TokenType.ASSIGN
        assert tokens[2].type == TokenType.LBRACE
        assert tokens[3].value == "key"
        assert tokens[4].type == TokenType.EQUALS
        
    def test_const_expression(self):
        lexer = Lexer(".(x 1.0 +).")
        tokens = lexer.tokenize()
        assert tokens[0].type == TokenType.DOT
        assert tokens[1].type == TokenType.LPAREN
        assert tokens[2].value == "x"
        assert tokens[3].value == 1.0
        assert tokens[4].type == TokenType.PLUS
        assert tokens[5].type == TokenType.RPAREN
        assert tokens[6].type == TokenType.DOT


class TestLexerErrors:
    """Тесты обработки ошибок."""
    
    def test_invalid_character(self):
        with pytest.raises(LexerError):
            lexer = Lexer("@")
            lexer.tokenize()
            
    def test_uppercase_in_name(self):
        with pytest.raises(LexerError):
            lexer = Lexer("myVariable")
            lexer.tokenize()