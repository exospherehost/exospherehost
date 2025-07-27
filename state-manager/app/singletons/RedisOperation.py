from enum import Enum

class RedisOperation(Enum):
    """Enumeration of supported Redis operations."""
    PING = "ping"
    EXISTS = "exists"
    GET = "get"
    DELETE = "delete"
    SET = "set"