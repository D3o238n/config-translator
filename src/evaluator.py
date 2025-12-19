"""
Вычислитель константных выражений для учебного конфигурационного языка.
"""

from typing import Any, Dict
from src.lexer import Token, TokenType
from src.parser import (
    ASTNode, NumberNode, NameNode, ArrayNode, DictNode, 
    ConstExpressionNode, ParseError
)


class EvaluationError(Exception):
    """Ошибка вычисления константного выражения."""
    def __init__(self, message: str, token: Token = None):
        self.message = message
        self.token = token
        if token:
            super().__init__(f"Ошибка вычисления на строке {token.line}, колонке {token.column}: {message}")
        else:
            super().__init__(f"Ошибка вычисления: {message}")


class Evaluator:
    """Вычислитель константных выражений."""
    
    def __init__(self, constants: Dict[str, Any] = None):
        self.constants = constants or {}
        self.stack = []
        
    def evaluate_expression(self, expr_tokens: List[Token]) -> Any:
        """Вычисляет значение постфиксного выражения."""
        self.stack = []
        
        for token in expr_tokens:
            if token.type == TokenType.NUMBER:
                self.stack.append(token.value)
                
            elif token.type == TokenType.NAME:
                # Это может быть константа или функция
                if token.value == 'sort':
                    # Функция sort()
                    if not self.stack:
                        raise EvaluationError("Недостаточно операндов для sort()", token)
                    operand = self.stack.pop()
                    if not isinstance(operand, list):
                        raise EvaluationError("sort() ожидает массив", token)
                    result = sorted(operand)
                    self.stack.append(result)
                else:
                    # Ссылка на константу
                    if token.value not in self.constants:
                        raise EvaluationError(f"Неизвестная константа: {token.value}", token)
                    self.stack.append(self.constants[token.value])
                    
            elif token.type == TokenType.PLUS:
                if len(self.stack) < 2:
                    raise EvaluationError("Недостаточно операндов для +", token)
                b = self.stack.pop()
                a = self.stack.pop()
                
                # Числа
                if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                    self.stack.append(a + b)
                # Массивы
                elif isinstance(a, list) and isinstance(b, list):
                    self.stack.append(a + b)
                else:
                    raise EvaluationError(f"Несовместимые типы для +: {type(a)} и {type(b)}", token)
                    
            elif token.type == TokenType.MINUS:
                if len(self.stack) < 2:
                    raise EvaluationError("Недостаточно операндов для -", token)
                b = self.stack.pop()
                a = self.stack.pop()
                
                # Только числа
                if isinstance(a, (int, float)) and isinstance(b, (int, float)):
                    self.stack.append(a - b)
                else:
                    raise EvaluationError(f"Несовместимые типы для -: {type(a)} и {type(b)}", token)
                    
            else:
                raise EvaluationError(f"Неожиданный токен в выражении: {token.type.name}", token)
                
        if len(self.stack) != 1:
            raise EvaluationError(f"Некорректное выражение, осталось {len(self.stack)} значений в стеке")
            
        return self.stack[0]
        
    def evaluate_node(self, node: ASTNode) -> Any:
        """Вычисляет значение узла AST."""
        if isinstance(node, NumberNode):
            return node.value
            
        elif isinstance(node, NameNode):
            if node.name not in self.constants:
                raise EvaluationError(f"Неизвестная константа: {node.name}")
            return self.constants[node.name]
            
        elif isinstance(node, ArrayNode):
            return [self.evaluate_node(elem) for elem in node.elements]
            
        elif isinstance(node, DictNode):
            return {key: self.evaluate_node(value) for key, value in node.pairs.items()}
            
        elif isinstance(node, ConstExpressionNode):
            return self.evaluate_expression(node.tokens)
            
        else:
            raise EvaluationError(f"Неизвестный тип узла: {type(node)}")
            
    def evaluate_all(self, nodes: List[ASTNode]) -> Dict[str, Any]:
        """Вычисляет все объявления в порядке их следования."""
        results = {}
        
        for node in nodes:
            if isinstance(node, ConstDeclarationNode):
                # Вычисляем значение
                value = self.evaluate_node(node.value)
                # Сохраняем в константы для использования в последующих выражениях
                self.constants[node.name] = value
                results[node.name] = value
            else:
                # Безымянное значение (не сохраняем в константы)
                value = self.evaluate_node(node)
                # Генерируем уникальное имя для вывода
                key = f"unnamed_{len(results)}"
                results[key] = value
                
        return results