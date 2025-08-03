"""
Status constants for state management in the exospherehost system.

These constants represent the various states that a workflow state can be in
during its lifecycle from creation to completion or failure.
"""

from enum import Enum


class Status(str, Enum):
    """
    Enumeration of workflow state status values.
    
    This enum provides type-safe constants for the various states that a workflow
    state can be in during its lifecycle from creation to completion or failure.
    """
    
    # State has been created but not yet queued for execution
    CREATED = 'CREATED'
    
    # State has been queued and is waiting to be picked up by a worker
    QUEUED = 'QUEUED'
    
    # State has been successfully executed by a worker
    EXECUTED = 'EXECUTED'
    
    # Next state in the workflow has been created based on successful execution
    NEXT_CREATED = 'NEXT_CREATED'
    
    # A retry state has been created due to a previous failure
    RETRY_CREATED = 'RETRY_CREATED'
    
    # State execution has timed out
    TIMEDOUT = 'TIMEDOUT'
    
    # State execution has failed with an error
    ERRORED = 'ERRORED'
    
    # State execution has been cancelled
    CANCELLED = 'CANCELLED'
    
    # State has completed successfully (final state)
    SUCCESS = 'SUCCESS'