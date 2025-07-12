from enum import Enum

class SessionStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"