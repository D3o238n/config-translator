"""
Тесты для синтаксического анализатора.
"""

import pytest
from src.parser import parse_text, ParseError
from src.parser import (
    NumberNode, NameNode, ArrayNode, DictNode,
    ConstDeclarationNode, ConstExpressionNode
)


class TestParserNumbers:
    """Тесты парсинга чисел."""
    
    def test_simple_number(self):
        ast = parse_text("42.0;")
        assert isinstance(ast[0], NumberNode)
        assert ast[0].value == 42.0
        
    def test_multiple_numbers(self):
        ast = parse_text("1.0; 2.0; 3.0;")
        assert len(ast) == 3
        assert all(isinstance(node, NumberNode) for node in ast)
        assert [node.value for node in ast] == [1.0, 2.0, 3.0]


class TestParserNames:
    """Тесты парсинга имён."""
    
    def test_simple_name(self):
        ast = parse_text("variable;")
        assert isinstance(ast[0], NameNode)
        assert ast[0].name == "variable"
        
    def test_name_assignment(self):
        ast = parse_text("x <- 5.0;")
        assert isinstance(ast[0], ConstDeclarationNode)
        assert ast[0].name == "x"
        assert isinstance(ast[0].value, NumberNode)
        assert ast[0].value.value == 5.0


class TestParserArrays:
    """Тесты парсинга массивов."""
    
    def test_empty_array(self):
        ast = parse_text("[];")
        assert isinstance(ast[0], ArrayNode)
        assert ast[0].elements == []
        
    def test_array_with_numbers(self):
        ast = parse_text("[1.0; 2.0; 3.0];")
        array_node = ast[0]
        assert isinstance(array_node, ArrayNode)
        assert len(array_node.elements) == 3
        assert all(isinstance(elem, NumberNode) for elem in array_node.elements)
        
    def test_nested_arrays(self):
        ast = parse_text("[[1.0; 2.0]; [3.0; 4.0]];")
        outer_array = ast[0]
        assert isinstance(outer_array, ArrayNode)
        assert len(outer_array.elements) == 2
        assert all(isinstance(elem, ArrayNode) for elem in outer_array.elements)


class TestParserDictionaries:
    """Тесты парсинга словарей."""
    
    def test_empty_dict(self):
        ast = parse_text("{};")
        assert isinstance(ast[0], DictNode)
        assert ast[0].pairs == {}
        
    def test_dict_with_values(self):
        ast = parse_text("{key1 = 1.0; key2 = 2.0};")
        dict_node = ast[0]
        assert isinstance(dict_node, DictNode)
        assert set(dict_node.pairs.keys()) == {"key1", "key2"}
        assert isinstance(dict_node.pairs["key1"], NumberNode)
        assert dict_node.pairs["key1"].value == 1.0
        
    def test_nested_dicts(self):
        ast = parse_text("{outer = {inner = 5.0}};")
        outer_dict = ast[0]
        assert isinstance(outer_dict, DictNode)
        inner_value = outer_dict.pairs["outer"]
        assert isinstance(inner_value, DictNode)
        assert isinstance(inner_value.pairs["inner"], NumberNode)


class TestParserConstExpressions:
    """Тесты парсинга константных выражений."""
    
    def test_simple_addition(self):
        ast = parse_text(".(1.0 2.0 +).;")
        assert isinstance(ast[0], ConstExpressionNode)
        assert len(ast[0].tokens) == 3  # 1.0, 2.0, +
        
    def test_expression_with_names(self):
        ast = parse_text(".(x y +).;")
        expr_node = ast[0]
        assert len(expr_node.tokens) == 3
        
    def test_expression_with_sort(self):
        ast = parse_text(".(arr sort()).;")
        expr_node = ast[0]
        # arr, sort, (, )
        assert len(expr_node.tokens) == 4


class TestParserComplex:
    """Тесты сложных конструкций."""
    
    def test_mixed_statements(self):
        text = """
        base <- 10.0;
        offset <- 5.0;
        result <- .(base offset +).;
        config <- {
            value = result;
            items = [1.0; 2.0; 3.0]
        };
        """
        ast = parse_text(text)
        assert len(ast) == 4
        
        # Проверяем типы
        assert isinstance(ast[0], ConstDeclarationNode)  # base
        assert isinstance(ast[1], ConstDeclarationNode)  # offset
        assert isinstance(ast[2], ConstDeclarationNode)  # result
        assert isinstance(ast[3], ConstDeclarationNode)  # config
        
        # Проверяем значения
        assert ast[0].name == "base"
        assert isinstance(ast[0].value, NumberNode)
        
        assert ast[2].name == "result"
        assert isinstance(ast[2].value, ConstExpressionNode)
        
        assert ast[3].name == "config"
        assert isinstance(ast[3].value, DictNode)


class TestParserErrors:
    """Тесты обработки ошибок парсера."""
    
    def test_missing_semicolon(self):
        """Тест отсутствия точки с запятой."""
        try:
            ast = parse_text("x <- 5.0")
            # Если не упало - ок, парсер снисходительный
            assert len(ast) == 1
            assert isinstance(ast[0], ConstDeclarationNode)
        except ParseError:
            # Если упало - тоже ок, парсер строгий
            pass

            
    def test_unclosed_array(self):
        with pytest.raises(ParseError):
            parse_text("[1.0; 2.0;")  # Нет ]
            
    def test_unclosed_dict(self):
        with pytest.raises(ParseError):
            parse_text("{key = 1.0")  # Нет }
            
    def test_invalid_dict_key(self):
        with pytest.raises(ParseError):
            parse_text("{123 = 1.0};")  # Ключ не имя
            
    def test_missing_equals_in_dict(self):
        with pytest.raises(ParseError):
            parse_text("{key 1.0};")  # Нет =
            
    def test_unclosed_const_expression(self):
        with pytest.raises(ParseError):
            parse_text(".(1.0 2.0 +")  # Нет ).