from enum import Enum


class PermissionEnum(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"