from enum import Enum


class ProjectStatusEnum(str, Enum):

    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"
    BLOCKED = "blocked"