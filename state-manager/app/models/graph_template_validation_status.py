from enum import Enum


class GraphTemplateValidationStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    PENDING = "PENDING"
    ONGOING = "ONGOING"
