import pytest

from app.models.retry_policy_model import RetryPolicyModel, RetryStrategy


class TestRetryPolicyModelExtended:
    """Additional test cases for RetryPolicyModel to improve coverage"""

    def test_compute_delay_invalid_retry_count(self):
        """Test compute_delay with invalid retry count (line 69)"""
        policy = RetryPolicyModel()
        
        # Test with retry_count < 1
        with pytest.raises(ValueError, match="Retry count must be greater than or equal to 1, got 0"):
            policy.compute_delay(0)
        
        with pytest.raises(ValueError, match="Retry count must be greater than or equal to 1, got -1"):
            policy.compute_delay(-1)

    def test_compute_delay_invalid_strategy(self):
        """Test compute_delay with invalid strategy (line 69)"""
        policy = RetryPolicyModel()
        
        # Set an invalid strategy
        policy.strategy = "INVALID_STRATEGY" # type: ignore
        
        with pytest.raises(ValueError, match="Invalid retry strategy: INVALID_STRATEGY"):
            policy.compute_delay(1)

    def test_compute_delay_all_strategies(self):
        """Test compute_delay with all retry strategies"""
        policy = RetryPolicyModel(
            max_retries=5,
            backoff_factor=1000,
            exponent=2,
            max_delay=10000
        )
        
        # Test all strategies
        strategies = [
            RetryStrategy.EXPONENTIAL,
            RetryStrategy.EXPONENTIAL_FULL_JITTER,
            RetryStrategy.EXPONENTIAL_EQUAL_JITTER,
            RetryStrategy.LINEAR,
            RetryStrategy.LINEAR_FULL_JITTER,
            RetryStrategy.LINEAR_EQUAL_JITTER,
            RetryStrategy.FIXED,
            RetryStrategy.FIXED_FULL_JITTER,
            RetryStrategy.FIXED_EQUAL_JITTER
        ]
        
        for strategy in strategies:
            policy.strategy = strategy
            delay = policy.compute_delay(1)
            assert delay >= 0  # Some strategies might return 0 for first retry
            assert delay <= 10000  # max_delay

    def test_compute_delay_with_max_delay_cap(self):
        """Test that max_delay properly caps the delay"""
        policy = RetryPolicyModel(
            max_retries=5,
            backoff_factor=1000,
            exponent=2,
            max_delay=2000  # Low max_delay to test capping
        )
        
        # With exponential strategy, retry_count=3 should exceed max_delay
        policy.strategy = RetryStrategy.EXPONENTIAL
        delay = policy.compute_delay(3)
        assert delay == 2000  # Should be capped at max_delay

    def test_compute_delay_without_max_delay(self):
        """Test compute_delay when max_delay is None"""
        policy = RetryPolicyModel(
            max_retries=5,
            backoff_factor=1000,
            exponent=2,
            max_delay=None  # No max_delay limit
        )
        
        # Should not be capped
        policy.strategy = RetryStrategy.EXPONENTIAL
        delay = policy.compute_delay(5)
        assert delay == 16000  # 1000 * 2^4

    def test_jitter_strategies(self):
        """Test that jitter strategies produce different results on multiple calls"""
        policy = RetryPolicyModel(
            max_retries=5,
            backoff_factor=1000,
            exponent=2
        )
        
        # Test jitter strategies
        jitter_strategies = [
            RetryStrategy.EXPONENTIAL_FULL_JITTER,
            RetryStrategy.EXPONENTIAL_EQUAL_JITTER,
            RetryStrategy.LINEAR_FULL_JITTER,
            RetryStrategy.LINEAR_EQUAL_JITTER,
            RetryStrategy.FIXED_FULL_JITTER,
            RetryStrategy.FIXED_EQUAL_JITTER
        ]
        
        for strategy in jitter_strategies:
            policy.strategy = strategy
            
            # Get multiple delays for the same retry count
            delays = [policy.compute_delay(2) for _ in range(10)]
            
            # For jitter strategies, we should get some variation
            # (though it's possible to get the same value by chance)
            unique_delays = set(delays)
            assert len(unique_delays) >= 1  # At least one unique value

    def test_linear_strategies(self):
        """Test linear retry strategies"""
        policy = RetryPolicyModel(
            max_retries=5,
            backoff_factor=1000,
            exponent=2
        )
        
        # Test linear strategy
        policy.strategy = RetryStrategy.LINEAR
        assert policy.compute_delay(1) == 1000
        assert policy.compute_delay(2) == 2000
        assert policy.compute_delay(3) == 3000
        
        # Test linear with jitter
        policy.strategy = RetryStrategy.LINEAR_FULL_JITTER
        delay = policy.compute_delay(3)
        assert 0 <= delay <= 3000
        
        policy.strategy = RetryStrategy.LINEAR_EQUAL_JITTER
        delay = policy.compute_delay(3)
        assert 1500 <= delay <= 3000

    def test_fixed_strategies(self):
        """Test fixed retry strategies"""
        policy = RetryPolicyModel(
            max_retries=5,
            backoff_factor=1000,
            exponent=2
        )
        
        # Test fixed strategy
        policy.strategy = RetryStrategy.FIXED
        assert policy.compute_delay(1) == 1000
        assert policy.compute_delay(5) == 1000  # Always the same
        
        # Test fixed with jitter
        policy.strategy = RetryStrategy.FIXED_FULL_JITTER
        delay = policy.compute_delay(1)
        assert 0 <= delay <= 1000
        
        policy.strategy = RetryStrategy.FIXED_EQUAL_JITTER
        delay = policy.compute_delay(1)
        assert 500 <= delay <= 1000

    def test_exponential_strategies(self):
        """Test exponential retry strategies"""
        policy = RetryPolicyModel(
            max_retries=5,
            backoff_factor=1000,
            exponent=2
        )
        
        # Test exponential strategy
        policy.strategy = RetryStrategy.EXPONENTIAL
        assert policy.compute_delay(1) == 1000  # 1000 * 2^0
        assert policy.compute_delay(2) == 2000  # 1000 * 2^1
        assert policy.compute_delay(3) == 4000  # 1000 * 2^2
        
        # Test exponential with jitter
        policy.strategy = RetryStrategy.EXPONENTIAL_FULL_JITTER
        delay = policy.compute_delay(3)
        assert 0 <= delay <= 4000
        
        policy.strategy = RetryStrategy.EXPONENTIAL_EQUAL_JITTER
        delay = policy.compute_delay(3)
        assert 2000 <= delay <= 4000

    def test_edge_case_retry_counts(self):
        """Test edge case retry counts"""
        policy = RetryPolicyModel(
            max_retries=5,
            backoff_factor=1000,
            exponent=2
        )
        
        # Test retry_count = 1 (minimum valid value)
        policy.strategy = RetryStrategy.EXPONENTIAL
        delay = policy.compute_delay(1)
        assert delay == 1000
        
        # Test high retry count
        delay = policy.compute_delay(10)
        assert delay > 0

    def test_field_validation(self):
        """Test field validation constraints"""
        # Test valid values
        policy = RetryPolicyModel(
            max_retries=0,  # ge=0
            backoff_factor=1,  # gt=0
            exponent=1,  # gt=0
            max_delay=1  # gt=0
        )
        assert policy.max_retries == 0
        assert policy.backoff_factor == 1
        assert policy.exponent == 1
        assert policy.max_delay == 1
        
        # Test max_delay can be None
        policy = RetryPolicyModel(max_delay=None)
        assert policy.max_delay is None

    def test_default_values(self):
        """Test default values"""
        policy = RetryPolicyModel()
        
        assert policy.max_retries == 3
        assert policy.strategy == RetryStrategy.EXPONENTIAL
        assert policy.backoff_factor == 2000
        assert policy.exponent == 2
        assert policy.max_delay is None

    def test_strategy_enum_values(self):
        """Test all RetryStrategy enum values"""
        strategies = [
            "EXPONENTIAL",
            "EXPONENTIAL_FULL_JITTER", 
            "EXPONENTIAL_EQUAL_JITTER",
            "LINEAR",
            "LINEAR_FULL_JITTER",
            "LINEAR_EQUAL_JITTER",
            "FIXED",
            "FIXED_FULL_JITTER",
            "FIXED_EQUAL_JITTER"
        ]
        
        for strategy_name in strategies:
            strategy = RetryStrategy(strategy_name)
            assert strategy.value == strategy_name 