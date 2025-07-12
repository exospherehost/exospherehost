from enum import Enum

class TokenStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    BLACKLISTED = "blacklisted"