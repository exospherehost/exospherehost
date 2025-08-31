from pydantic import BaseModel, Field
from enum import Enum

class RetryMethod(str, Enum):
    EXPONENTIAL = "EXPONENTIAL"
    LINEAR = "LINEAR"
    FIXED = "FIXED"

class RetryPolicyModel(BaseModel):
    max_retries: int = Field(default=3, description="The maximum number of retries", ge=0)
    method: RetryMethod = Field(default=RetryMethod.EXPONENTIAL, description="The method of retry")
    backoff_factor: int = Field(default=2, description="The backoff factor in seconds (default: 2 = 2 seconds)", gt=0)