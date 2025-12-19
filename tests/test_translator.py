"""
Интеграционные тесты транслятора.
"""

import pytest
import yaml
from src.translator import Translator, TranslationError
from src.evaluator import EvaluationError


class TestTranslatorBasic:
    """Базовые тесты трансляции."""
    
    def test_simple_number(self):
        translator = Translator()
        output = translator.translate("x <- 42.0;")
        data = yaml.safe_load(output)
        assert data['x'] == 42.0
        
    def test_simple_array(self):
        translator = Translator()
        output = translator.translate("nums <- [ 1.0; 2.0; 3.0 ];")
        data = yaml.safe_load(output)
        assert data['nums'] == [1.0, 2.0, 3.0]
        
    def test_simple_dict(self):
        translator = Translator()
        output = translator.translate("person <- { age = 25.0; score = 100.0 };")
        data = yaml.safe_load(output)
        assert data['person']['age'] == 25.0
        assert data['person']['score'] == 100.0


class TestTranslatorNested:
    """Тесты вложенных структур."""
    
    def test_nested_array(self):
        translator = Translator()
        output = translator.translate("matrix <- [ [ 1.0; 2.0 ]; [ 3.0; 4.0 ] ];")
        data = yaml.safe_load(output)
        assert data['matrix'] == [[1.0, 2.0], [3.0, 4.0]]
        
    def test_nested_dict(self):
        translator = Translator()
        text = """
        config <- {
            database = {
                host = 1.0;
                port = 2.0
            };
            cache = {
                enabled = 1.0
            }
        };
        """
        output = translator.translate(text)
        data = yaml.safe_load(output)
        assert data['config']['database']['host'] == 1.0
        assert data['config']['cache']['enabled'] == 1.0
        
    def test_dict_with_array(self):
        translator = Translator()
        text = "data <- { items = [ 1.0; 2.0; 3.0 ]; count = 3.0 };"
        output = translator.translate(text)
        data = yaml.safe_load(output)
        assert data['data']['items'] == [1.0, 2.0, 3.0]
        assert data['data']['count'] == 3.0


class TestTranslatorConstExpressions:
    """Тесты константных выражений."""
    
    def test_addition(self):
        translator = Translator()
        output = translator.translate("result <- .(5.0 3.0 +).;")
        data = yaml.safe_load(output)
        assert data['result'] == 8.0
        
    def test_subtraction(self):
        translator = Translator()
        output = translator.translate("diff <- .(10.0 7.0 -).;")
        data = yaml.safe_load(output)
        assert data['diff'] == 3.0
        
    def test_with_variable_reference(self):
        translator = Translator()
        text = """
        base <- 10.0;
        result <- .(base 5.0 +).;
        """
        output = translator.translate(text)
        data = yaml.safe_load(output)
        assert data['base'] == 10.0
        assert data['result'] == 15.0
        
    def test_sort_function(self):
        translator = Translator()
        text = """
        unsorted <- [ 3.0; 1.0; 4.0; 1.0; 5.0 ];
        sorted <- .(unsorted sort()).;
        """
        output = translator.translate(text)
        data = yaml.safe_load(output)
        assert data['sorted'] == [1.0, 1.0, 3.0, 4.0, 5.0]
        
    def test_array_concatenation(self):
        translator = Translator()
        text = """
        arr1 <- [ 1.0; 2.0 ];
        arr2 <- [ 3.0; 4.0 ];
        combined <- .(arr1 arr2 +).;
        """
        output = translator.translate(text)
        data = yaml.safe_load(output)
        assert data['combined'] == [1.0, 2.0, 3.0, 4.0]
        
    def test_complex_expression(self):
        translator = Translator()
        text = """
        a <- 10.0;
        b <- 5.0;
        c <- 3.0;
        result <- .(a b + c -).;
        """
        output = translator.translate(text)
        data = yaml.safe_load(output)
        # (10 + 5) - 3 = 12
        assert data['result'] == 12.0


class TestTranslatorComments:
    """Тесты обработки комментариев."""
    
    def test_single_line_comment(self):
        translator = Translator()
        text = """
        :: Это комментарий
        x <- 42.0;
        :: Еще комментарий
        """
        output = translator.translate(text)
        data = yaml.safe_load(output)
        assert data['x'] == 42.0
        
    def test_multi_line_comment(self):
        translator = Translator()
        text = """
        <#
        Это многострочный
        комментарий
        #>
        y <- 100.0;
        """
        output = translator.translate(text)
        data = yaml.safe_load(output)
        assert data['y'] == 100.0
        
    def test_mixed_comments(self):
        translator = Translator()
        text = """
        :: Однострочный
        a <- 1.0;
        <# Многострочный #>
        b <- 2.0;
        """
        output = translator.translate(text)
        data = yaml.safe_load(output)
        assert len(data) == 2


class TestTranslatorErrors:
    """Тесты обработки ошибок."""
    
    def test_undefined_constant(self):
        translator = Translator()
        with pytest.raises(TranslationError):
            translator.translate("x <- .(undefined_var 1.0 +).;")
            
    def test_type_error_in_subtraction(self):
        translator = Translator()
        text = """
        arr <- [ 1.0 ];
        result <- .(arr 1.0 -).;
        """
        with pytest.raises(TranslationError):
            translator.translate(text)
            
    def test_sort_non_array(self):
        translator = Translator()
        text = """
        num <- 42.0;
        result <- .(num sort()).;
        """
        with pytest.raises(TranslationError):
            translator.translate(text)
            
    def test_lexer_error(self):
        translator = Translator()
        with pytest.raises(TranslationError):
            translator.translate("x <- @invalid;")
            
    def test_parser_error(self):
        translator = Translator()
        with pytest.raises(TranslationError):
            translator.translate("x <- 1.0")  # Нет точки с запятой


class TestTranslatorComplex:
    """Тесты сложных конфигураций."""
    
    def test_complete_config(self):
        translator = Translator()
        text = """
        :: Database configuration
        db_host <- 1.0;
        db_port <- 5432.0;
        
        <# Connection settings #>
        timeout <- 30.0;
        max_retries <- 3.0;
        
        :: Combined config
        database <- {
            host = db_host;
            port = db_port;
            settings = {
                timeout = timeout;
                retries = max_retries
            }
        };
        
        :: Server list
        servers <- [ 1.0; 2.0; 3.0 ];
        sorted_servers <- .(servers sort()).;
        """
        output = translator.translate(text)
        data = yaml.safe_load(output)
        
        assert data['db_host'] == 1.0
        assert data['database']['host'] == 1.0
        assert data['database']['settings']['timeout'] == 30.0
        assert data['sorted_servers'] == [1.0, 2.0, 3.0]