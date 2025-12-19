"""
Парсер для учебного конфигурационного языка (рекурсивный спуск).
"""

from typing import List, Optional, Any, Dict
from dataclasses import dataclass
from src.lexer import Lexer, Token, TokenType


class ParseError(Exception):
    """Ошибка синтаксического анализа."""
    def __init__(self, message: str, token: Optional[Token] = None):
        self.message = message
        self.token = token
        if token:
            super().__init__(f"Ошибка синтаксиса на строке {token.line}, колонке {token.column}: {message}")
        else:
            super().__init__(f"Ошибка синтаксиса: {message}")


@dataclass
class ASTNode:
    """Абстрактный базовый класс узла AST."""
    pass


@dataclass
class NumberNode(ASTNode):
    """Числовое значение."""
    value: float


@dataclass
class NameNode(ASTNode):
    """Идентификатор (имя переменной)."""
    name: str


@dataclass
class ArrayNode(ASTNode):
    """Массив значений."""
    elements: List[ASTNode]


@dataclass
class DictNode(ASTNode):
    """Словарь (пары ключ-значение)."""
    pairs: Dict[str, ASTNode]


@dataclass
class ConstDeclarationNode(ASTNode):
    """Объявление константы."""
    name: str
    value: ASTNode


@dataclass
class ConstExpressionNode(ASTNode):
    """Константное выражение в постфиксной форме."""
    tokens: List[Token]  # Для последующей обработки вычислителем


class Parser:
    """Парсер (рекурсивный спуск)."""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0] if tokens else None
        
    def error(self, message: str):
        """Генерирует ошибку парсинга."""
        raise ParseError(message, self.current_token)
        
    def eat(self, token_type: TokenType) -> Token:
        """Потребляет токен ожидаемого типа."""
        if self.current_token.type == token_type:
            token = self.current_token
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
            else:
                self.current_token = None
            return token
        self.error(f"Ожидается {token_type.name}, получено {self.current_token.type.name}")
        
    def peek(self, offset: int = 0) -> Optional[Token]:
        """Заглядывает вперед на offset токенов."""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
        
    def parse(self) -> List[ASTNode]:
        """Основной метод парсинга."""
        statements = []
        while self.current_token and self.current_token.type != TokenType.EOF:
            statements.append(self.parse_statement())
            if self.current_token and self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
        return statements
        
    def parse_statement(self) -> ASTNode:
        """Парсит инструкцию."""
        # Имя...
        if self.current_token.type == TokenType.NAME:
            name_token = self.current_token
            self.eat(TokenType.NAME)
            
            # ...следует присваивание?
            if self.current_token.type == TokenType.ASSIGN:
                self.eat(TokenType.ASSIGN)
                value = self.parse_value()
                return ConstDeclarationNode(name_token.value, value)
            else:
                # Имя может быть частью константного выражения
                self.pos -= 1  # Возвращаемся назад
                self.current_token = name_token
                return self.parse_value()
                
        # Или просто значение
        return self.parse_value()
        
    def parse_value(self) -> ASTNode:
        """Парсит значение."""
        token = self.current_token
        
        if token.type == TokenType.NUMBER:
            self.eat(TokenType.NUMBER)
            return NumberNode(token.value)
            
        elif token.type == TokenType.NAME:
            self.eat(TokenType.NAME)
            return NameNode(token.value)
            
        elif token.type == TokenType.LBRACKET:
            return self.parse_array()
            
        elif token.type == TokenType.LBRACE:
            return self.parse_dict()
            
        elif token.type == TokenType.DOT:
            return self.parse_const_expression()
            
        else:
            self.error(f"Неожиданный токен при разборе значения: {token.type.name}")
            
    def parse_array(self) -> ArrayNode:
        """Парсит массив."""
        self.eat(TokenType.LBRACKET)  # [
        elements = []
        
        # Пустой массив?
        if self.current_token.type == TokenType.RBRACKET:
            self.eat(TokenType.RBRACKET)
            return ArrayNode(elements)
            
        # Непустой массив
        while True:
            elements.append(self.parse_value())
            
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
                
                # Проверяем, следующий элемент или конец
                if self.current_token.type == TokenType.RBRACKET:
                    break
                else:
                    continue
                    
            elif self.current_token.type == TokenType.RBRACKET:
                break
            else:
                self.error(f"Ожидается ';' или ']', получено {self.current_token.type.name}")
                
        self.eat(TokenType.RBRACKET)
        return ArrayNode(elements)
        
    def parse_dict(self) -> DictNode:
        """Парсит словарь."""
        self.eat(TokenType.LBRACE)  # {
        pairs = {}
        
        # Пустой словарь?
        if self.current_token.type == TokenType.RBRACE:
            self.eat(TokenType.RBRACE)
            return DictNode(pairs)
            
        # Непустой словарь
        while True:
            # Имя ключа
            if self.current_token.type != TokenType.NAME:
                self.error(f"Ожидается имя ключа, получено {self.current_token.type.name}")
            key_name = self.current_token.value
            self.eat(TokenType.NAME)
            
            # Знак равенства
            self.eat(TokenType.EQUALS)
            
            # Значение
            value = self.parse_value()
            pairs[key_name] = value
            
            # Точка с запятой (необязательно перед })
            if self.current_token.type == TokenType.SEMICOLON:
                self.eat(TokenType.SEMICOLON)
                
                # Проверяем, следующий элемент или конец
                if self.current_token.type == TokenType.RBRACE:
                    break
                else:
                    continue
                    
            elif self.current_token.type == TokenType.RBRACE:
                break
            else:
                self.error(f"Ожидается ';' или '}}', получено {self.current_token.type.name}")
                
        self.eat(TokenType.RBRACE)
        return DictNode(pairs)
        
    def parse_const_expression(self) -> ConstExpressionNode:
        """Парсит константное выражение."""
        # Начинается с .(
        self.eat(TokenType.DOT)  # .
        self.eat(TokenType.LPAREN)  # (
        
        # Собираем все токены внутри выражения
        expr_tokens = []
        paren_count = 1  # Уже открыли одну
        
        while self.current_token and paren_count > 0:
            if self.current_token.type == TokenType.LPAREN:
                paren_count += 1
            elif self.current_token.type == TokenType.RPAREN:
                paren_count -= 1
                
            if paren_count > 0:
                expr_tokens.append(self.current_token)
                self.pos += 1
                if self.pos < len(self.tokens):
                    self.current_token = self.tokens[self.pos]
                else:
                    self.current_token = None
            else:
                # Потребляем закрывающую скобку
                self.eat(TokenType.RPAREN)
                break
                
        # Проверяем, что выражение заканчивается .
        if self.current_token and self.current_token.type == TokenType.DOT:
            self.eat(TokenType.DOT)
        else:
            self.error("Ожидается '.' после константного выражения")
            
        return ConstExpressionNode(expr_tokens)


def parse_text(text: str) -> List[ASTNode]:
    """Парсит текст в AST."""
    lexer = Lexer(text)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    return parser.parse()