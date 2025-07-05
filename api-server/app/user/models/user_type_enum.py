from enum import Enum

class UserTypeEnum(str, Enum):
    HUMAN = "HUMAN"
    API = "API"