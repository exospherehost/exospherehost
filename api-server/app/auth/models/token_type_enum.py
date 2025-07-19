from enum import Enum


class TokenType(str, Enum):
    access = "access"
    refresh = "refresh"