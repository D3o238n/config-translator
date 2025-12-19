"""
Лексический анализатор для учебного конфигурационного языка.
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """Типы токенов."""
    # Литералы
    NUMBER = auto()
    NAME = auto()
    
    # Операторы и разделители
    LBRACKET = auto()      # [
    RBRACKET = auto()      # ]
    LBRACE = auto()        # {
    RBRACE = auto()        # }
    LPAREN = auto()        # (
    RPAREN = auto()        # )
    SEMICOLON = auto()     # ;
    EQUALS = auto()        # =
    ASSIGN = auto()        # <-
    DOT = auto()           # .
    
    # Операторы
    PLUS = auto()          # +
    MINUS = auto()         # -
    
    # Ключевые слова/функции
    SORT = auto()
    
    # Специальные
    EOF = auto()
    NEWLINE = auto()


@dataclass
class Token:
    """Токен с типом, значением и позицией."""
    type: TokenType
    value: any
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, {self.line}:{self.column})"


class LexerError(Exception):
    """Ошибка лексического анализа."""
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"Ошибка на строке {line}, колонке {column}: {message}")


class Lexer:
    """Лексический анализатор."""
    
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        
    def error(self, message: str):
        """Генерирует ошибку лексического анализа."""
        raise LexerError(message, self.line, self.column)
        
    def peek(self, offset: int = 0) -> Optional[str]:
        """Возвращает символ на позиции pos + offset без изменения позиции."""
        pos = self.pos + offset
        if pos < len(self.text):
            return self.text[pos]
        return None
        
    def advance(self) -> Optional[str]:
        """Переходит к следующему символу."""
        if self.pos >= len(self.text):
            return None
        char = self.text[self.pos]
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char
        
    def skip_whitespace(self):
        """Пропускает пробельные символы."""
        while self.peek() and self.peek() in ' \t\r\n':
            self.advance()
            
    def skip_single_line_comment(self):
        """Пропускает однострочный комментарий."""
        # Пропускаем ::
        self.advance()
        self.advance()
        # Читаем до конца строки
        while self.peek() and self.peek() != '\n':
            self.advance()
            
    def skip_multi_line_comment(self):
        """Пропускает многострочный комментарий."""
        # Пропускаем <#
        self.advance()
        self.advance()
        
        # Читаем до #>
        while True:
            char = self.peek()
            if char is None:
                self.error("Незакрытый многострочный комментарий")
            if char == '#' and self.peek(1) == '>':
                self.advance()  # #
                self.advance()  # >
                break
            self.advance()
            
    def read_number(self) -> Token:
        """Читает число."""
        start_line = self.line
        start_column = self.column
        num_str = ''
        
        # Читаем целую часть
        while self.peek() and self.peek().isdigit():
            num_str += self.advance()
            
        # Проверяем дробную часть
        if self.peek() == '.':
            num_str += self.advance()
            # После точки должна быть хотя бы одна цифра или ничего
            while self.peek() and self.peek().isdigit():
                num_str += self.advance()
                
        return Token(TokenType.NUMBER, float(num_str), start_line, start_column)
        
    def read_name(self) -> Token:
        """Читает имя."""
        start_line = self.line
        start_column = self.column
        name = ''
        
        # Первый символ - строчная буква
        name += self.advance()
        
        # Последующие символы - буквы, цифры, подчеркивание
        while self.peek() and (self.peek().isalnum() or self.peek() == '_'):
            char = self.peek()
            if char.isupper():
                self.error(f"Недопустимый символ в имени: '{char}'")
            name += self.advance()
            
        # Проверяем на ключевые слова
        if name == 'sort':
            return Token(TokenType.SORT, name, start_line, start_column)
            
        return Token(TokenType.NAME, name, start_line, start_column)
        
    def tokenize(self) -> List[Token]:
        """Выполняет лексический анализ."""
        while self.pos < len(self.text):
            self.skip_whitespace()
            
            if self.pos >= len(self.text):
                break
                
            char = self.peek()
            
            # Комментарии
            if char == ':' and self.peek(1) == ':':
                self.skip_single_line_comment()
                continue
                
            if char == '<' and self.peek(1) == '#':
                self.skip_multi_line_comment()
                continue
                
            # Числа
            if char.isdigit():
                self.tokens.append(self.read_number())
                continue
                
            # Имена
            if char.islower():
                self.tokens.append(self.read_name())
                continue
                
            # Операторы и разделители
            start_line = self.line
            start_column = self.column
            
            if char == '[':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACKET, '[', start_line, start_column))
            elif char == ']':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACKET, ']', start_line, start_column))
            elif char == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, '{', start_line, start_column))
            elif char == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, '}', start_line, start_column))
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', start_line, start_column))
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', start_line, start_column))
            elif char == ';':
                self.advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ';', start_line, start_column))
            elif char == '=':
                self.advance()
                self.tokens.append(Token(TokenType.EQUALS, '=', start_line, start_column))
            elif char == '<' and self.peek(1) == '-':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.ASSIGN, '<-', start_line, start_column))
            elif char == '.':
                self.advance()
                self.tokens.append(Token(TokenType.DOT, '.', start_line, start_column))
            elif char == '+':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS, '+', start_line, start_column))
            elif char == '-':
                self.advance()
                self.tokens.append(Token(TokenType.MINUS, '-', start_line, start_column))
            else:
                self.error(f"Неожиданный символ: '{char}'")
                
        # Добавляем EOF
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens