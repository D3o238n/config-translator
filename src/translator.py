"""
Транслятор учебного конфигурационного языка в YAML.
"""

import yaml
from typing import Dict, Any
from src.lexer import Lexer, LexerError
from src.parser import parse_text, ParseError
from src.evaluator import Evaluator, EvaluationError


class TranslationError(Exception):
    """Ошибка трансляции."""
    def __init__(self, message: str, cause: Exception = None):
        self.message = message
        self.cause = cause
        super().__init__(message)


class Translator:
    """Транслятор из учебного языка в YAML."""
    
    def __init__(self):
        pass
        
    def translate(self, text: str) -> str:
        """
        Транслирует текст на учебном языке в YAML.
        
        Args:
            text: Исходный текст
            
        Returns:
            YAML строка
            
        Raises:
            TranslationError: при любой ошибке обработки
        """
        try:
            # 1. Лексический анализ
            lexer = Lexer(text)
            tokens = lexer.tokenize()
            
            # 2. Синтаксический анализ
            ast_nodes = parse_text(text)
            
            # 3. Вычисление константных выражений
            evaluator = Evaluator()
            results = evaluator.evaluate_all(ast_nodes)
            
            # 4. Генерация YAML
            yaml_output = yaml.dump(
                results,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                indent=2
            )
            
            return yaml_output
            
        except LexerError as e:
            raise TranslationError(f"Лексическая ошибка: {e}", e)
        except ParseError as e:
            raise TranslationError(f"Синтаксическая ошибка: {e}", e)
        except EvaluationError as e:
            raise TranslationError(f"Ошибка вычисления: {e}", e)
        except Exception as e:
            raise TranslationError(f"Неожиданная ошибка: {e}", e)
            
    def translate_file(self, input_path: str, output_path: str) -> None:
        """
        Транслирует файл и сохраняет результат.
        
        Args:
            input_path: Путь к входному файлу
            output_path: Путь для сохранения YAML
            
        Raises:
            TranslationError: при любой ошибке
        """
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
            yaml_output = self.translate(text)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(yaml_output)
                
        except IOError as e:
            raise TranslationError(f"Ошибка ввода/вывода: {e}", e)
        except TranslationError:
            raise  # Пробрасываем дальше
        except Exception as e:
            raise TranslationError(f"Неожиданная ошибка: {e}", e)