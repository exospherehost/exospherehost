from enum import Enum


class StateStatusEnum(str, Enum):

    CREATED = 'CREATED'
    QUEUED = 'QUEUED'
    EXECUTED = 'EXECUTED'
    ERRORED = 'ERRORED'
    CANCELLED = 'CANCELLED'
    SUCCESS = 'SUCCESS'
    NEXT_CREATED_ERROR = 'NEXT_CREATED_ERROR'
    PRUNED = 'PRUNED'