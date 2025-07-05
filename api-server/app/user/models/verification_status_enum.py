from enum import Enum

class VerificationStatusEnum(str, Enum):
    VERIFIED = "VERIFIED"
    NOT_VERIFIED = "NOT_VERIFIED"
    BLOCKED = "BLOCKED"
    DELETED = "DELETED"
    NOT_REQUIRED = "NOT_REQUIRED"
