from enum import Enum


class IdentifierType(Enum):
    EMAIL = "email"
    SECRET = "secret"


class IdentifierStatus(Enum):
    NOT_VERIFIED = "not_verified"
    VERIFIED = "verified"
    BLOCKED = "blocked"
    DELETED = "deleted"


class UserStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"
    DELETED = "deleted"


class AuthMethods(Enum):
    PASSWORD = "password"
    KEY = "key"
