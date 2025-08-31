from pydantic import BaseModel, Field
from enum import Enum
import random

class RetryStrategy(str, Enum):
    EXPONENTIAL = "EXPONENTIAL"
    EXPONENTIAL_FULL_JITTER = "EXPONENTIAL_FULL_JITTER"
    EXPONENTIAL_EQUAL_JITTER = "EXPONENTIAL_EQUAL_JITTER"

    LINEAR = "LINEAR"
    LINEAR_FULL_JITTER = "LINEAR_FULL_JITTER"
    LINEAR_EQUAL_JITTER = "LINEAR_EQUAL_JITTER"

    FIXED = "FIXED"
    FIXED_FULL_JITTER = "FIXED_FULL_JITTER"
    FIXED_EQUAL_JITTER = "FIXED_EQUAL_JITTER"

class RetryPolicyModel(BaseModel):
    max_retries: int = Field(default=3, description="The maximum number of retries", ge=0)
    strategy: RetryStrategy = Field(default=RetryStrategy.EXPONENTIAL, description="The method of retry")
    backoff_factor: int = Field(default=2000, description="The backoff factor in milliseconds (default: 2000 = 2 seconds)", gt=0)
    exponent: int = Field(default=2, description="The exponent for the exponential retry strategy", gt=0)
    max_delay: int | None = Field(default=None, description="The maximum delay in milliseconds (default: 3600000 = 1 hour)", gt=0)

    def compute_delay(self, retry_count: int) -> int:

        def _cap(value: int) -> int:
            if self.max_delay is not None:
                return min(value, self.max_delay)
            return value

        if retry_count < 1:
            raise ValueError(f"Retry count must be greater than 1, got {retry_count}")
        
        if self.strategy == RetryStrategy.EXPONENTIAL:
            return _cap(self.backoff_factor * (self.exponent ** (retry_count - 1)))
        
        elif self.strategy == RetryStrategy.EXPONENTIAL_FULL_JITTER:
            base = self.backoff_factor * (self.exponent ** (retry_count - 1))
            return _cap(int(random.uniform(0, base)))
        
        elif self.strategy == RetryStrategy.EXPONENTIAL_EQUAL_JITTER:
            base = self.backoff_factor * (self.exponent ** (retry_count - 1))
            return _cap(int(base/2 + random.uniform(0, base / 2)))
        
        elif self.strategy == RetryStrategy.LINEAR:
            return _cap(self.backoff_factor * retry_count)
        
        elif self.strategy == RetryStrategy.LINEAR_FULL_JITTER:
            base = self.backoff_factor * retry_count
            return _cap(int(random.uniform(0, base)))

        elif self.strategy == RetryStrategy.LINEAR_EQUAL_JITTER:
            base = self.backoff_factor * retry_count
            return _cap(int(base/2 + random.uniform(0, base / 2)))

        elif self.strategy == RetryStrategy.FIXED:
            return _cap(self.backoff_factor)
        
        elif self.strategy == RetryStrategy.FIXED_FULL_JITTER:
            base = self.backoff_factor
            return _cap(int(random.uniform(0, base)))

        elif self.strategy == RetryStrategy.FIXED_EQUAL_JITTER:
            base = self.backoff_factor
            return _cap(int(base/2 + random.uniform(0, base / 2)))

        else:
            raise ValueError(f"Invalid retry strategy: {self.strategy}")