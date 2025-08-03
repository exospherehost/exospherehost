from enum import Enum


class GraphTemplateValidationStatus(Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    PENDING = "PENDING"
    ONGOING = "ONGOING"