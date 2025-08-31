import pytest
import random
from app.models.retry_policy_model import RetryPolicyModel, RetryStrategy


class TestRetryPolicyModel:
    """Test cases for RetryPolicyModel"""

    def test_default_initialization(self):
        """Test RetryPolicyModel with default values"""
        policy = RetryPolicyModel()
        
        assert policy.max_retries == 3
        assert policy.strategy == RetryStrategy.EXPONENTIAL
        assert policy.backoff_factor == 2000
        assert policy.exponent == 2
        assert policy.max_delay is None

    def test_custom_initialization(self):
        """Test RetryPolicyModel with custom values"""
        policy = RetryPolicyModel(
            max_retries=5,
            strategy=RetryStrategy.LINEAR,
            backoff_factor=1000,
            exponent=3,
            max_delay=10000
        )
        
        assert policy.max_retries == 5
        assert policy.strategy == RetryStrategy.LINEAR
        assert policy.backoff_factor == 1000
        assert policy.exponent == 3
        assert policy.max_delay == 10000

    def test_exponential_strategy(self):
        """Test exponential retry strategy"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.EXPONENTIAL,
            backoff_factor=1000,
            exponent=2
        )
        
        # Test retry count 1
        delay = policy.compute_delay(1)
        assert delay == 1000  # 1000 * 2^0
        
        # Test retry count 2
        delay = policy.compute_delay(2)
        assert delay == 2000  # 1000 * 2^1
        
        # Test retry count 3
        delay = policy.compute_delay(3)
        assert delay == 4000  # 1000 * 2^2

    def test_exponential_strategy_with_max_delay(self):
        """Test exponential retry strategy with max delay cap"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.EXPONENTIAL,
            backoff_factor=1000,
            exponent=2,
            max_delay=3000
        )
        
        # Test retry count 1
        delay = policy.compute_delay(1)
        assert delay == 1000  # 1000 * 2^0
        
        # Test retry count 2
        delay = policy.compute_delay(2)
        assert delay == 2000  # 1000 * 2^1
        
        # Test retry count 3 (should be capped at max_delay)
        delay = policy.compute_delay(3)
        assert delay == 3000  # Capped at max_delay

    def test_linear_strategy(self):
        """Test linear retry strategy"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.LINEAR,
            backoff_factor=1000
        )
        
        # Test retry count 1
        delay = policy.compute_delay(1)
        assert delay == 1000  # 1000 * 1
        
        # Test retry count 2
        delay = policy.compute_delay(2)
        assert delay == 2000  # 1000 * 2
        
        # Test retry count 3
        delay = policy.compute_delay(3)
        assert delay == 3000  # 1000 * 3

    def test_fixed_strategy(self):
        """Test fixed retry strategy"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.FIXED,
            backoff_factor=1000
        )
        
        # Test retry count 1
        delay = policy.compute_delay(1)
        assert delay == 1000  # Always 1000
        
        # Test retry count 2
        delay = policy.compute_delay(2)
        assert delay == 1000  # Always 1000
        
        # Test retry count 3
        delay = policy.compute_delay(3)
        assert delay == 1000  # Always 1000

    def test_exponential_full_jitter_strategy(self):
        """Test exponential full jitter retry strategy"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.EXPONENTIAL_FULL_JITTER,
            backoff_factor=1000,
            exponent=2
        )
        
        # Test retry count 1
        delay = policy.compute_delay(1)
        assert 0 <= delay <= 1000  # Random between 0 and 1000
        
        # Test retry count 2
        delay = policy.compute_delay(2)
        assert 0 <= delay <= 2000  # Random between 0 and 2000

    def test_exponential_equal_jitter_strategy(self):
        """Test exponential equal jitter retry strategy"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.EXPONENTIAL_EQUAL_JITTER,
            backoff_factor=1000,
            exponent=2
        )
        
        # Test retry count 1
        delay = policy.compute_delay(1)
        assert 500 <= delay <= 1000  # Random between 500 and 1000
        
        # Test retry count 2
        delay = policy.compute_delay(2)
        assert 1000 <= delay <= 2000  # Random between 1000 and 2000

    def test_linear_full_jitter_strategy(self):
        """Test linear full jitter retry strategy"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.LINEAR_FULL_JITTER,
            backoff_factor=1000
        )
        
        # Test retry count 1
        delay = policy.compute_delay(1)
        assert 0 <= delay <= 1000  # Random between 0 and 1000
        
        # Test retry count 2
        delay = policy.compute_delay(2)
        assert 0 <= delay <= 2000  # Random between 0 and 2000

    def test_linear_equal_jitter_strategy(self):
        """Test linear equal jitter retry strategy"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.LINEAR_EQUAL_JITTER,
            backoff_factor=1000
        )
        
        # Test retry count 1
        delay = policy.compute_delay(1)
        assert 500 <= delay <= 1000  # Random between 500 and 1000
        
        # Test retry count 2
        delay = policy.compute_delay(2)
        assert 1000 <= delay <= 2000  # Random between 1000 and 2000

    def test_fixed_full_jitter_strategy(self):
        """Test fixed full jitter retry strategy"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.FIXED_FULL_JITTER,
            backoff_factor=1000
        )
        
        # Test retry count 1
        delay = policy.compute_delay(1)
        assert 0 <= delay <= 1000  # Random between 0 and 1000
        
        # Test retry count 2
        delay = policy.compute_delay(2)
        assert 0 <= delay <= 1000  # Random between 0 and 1000

    def test_fixed_equal_jitter_strategy(self):
        """Test fixed equal jitter retry strategy"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.FIXED_EQUAL_JITTER,
            backoff_factor=1000
        )
        
        # Test retry count 1
        delay = policy.compute_delay(1)
        assert 500 <= delay <= 1000  # Random between 500 and 1000
        
        # Test retry count 2
        delay = policy.compute_delay(2)
        assert 500 <= delay <= 1000  # Random between 500 and 1000

    def test_invalid_retry_count(self):
        """Test that invalid retry count raises ValueError"""
        policy = RetryPolicyModel()
        
        # Test retry count 0
        with pytest.raises(ValueError, match="Retry count must be greater than or equal to 1"):
            policy.compute_delay(0)
        
        # Test retry count -1
        with pytest.raises(ValueError, match="Retry count must be greater than or equal to 1"):
            policy.compute_delay(-1)

    def test_max_delay_capping(self):
        """Test that max_delay properly caps the delay"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.EXPONENTIAL,
            backoff_factor=1000,
            exponent=2,
            max_delay=1500
        )
        
        # Test retry count 1
        delay = policy.compute_delay(1)
        assert delay == 1000  # Not capped
        
        # Test retry count 2
        delay = policy.compute_delay(2)
        assert delay == 1500  # Capped at max_delay
        
        # Test retry count 3
        delay = policy.compute_delay(3)
        assert delay == 1500  # Capped at max_delay

    def test_jitter_strategies_with_max_delay(self):
        """Test jitter strategies with max delay capping"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.EXPONENTIAL_FULL_JITTER,
            backoff_factor=1000,
            exponent=2,
            max_delay=1500
        )
        
        # Test multiple calls to ensure max_delay is respected
        for _ in range(10):
            delay = policy.compute_delay(3)
            assert delay <= 1500  # Should never exceed max_delay

    def test_different_exponents(self):
        """Test different exponent values"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.EXPONENTIAL,
            backoff_factor=1000,
            exponent=3
        )
        
        # Test retry count 1
        delay = policy.compute_delay(1)
        assert delay == 1000  # 1000 * 3^0
        
        # Test retry count 2
        delay = policy.compute_delay(2)
        assert delay == 3000  # 1000 * 3^1
        
        # Test retry count 3
        delay = policy.compute_delay(3)
        assert delay == 9000  # 1000 * 3^2

    def test_different_backoff_factors(self):
        """Test different backoff factor values"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.LINEAR,
            backoff_factor=500
        )
        
        # Test retry count 1
        delay = policy.compute_delay(1)
        assert delay == 500  # 500 * 1
        
        # Test retry count 2
        delay = policy.compute_delay(2)
        assert delay == 1000  # 500 * 2

    def test_model_validation(self):
        """Test Pydantic model validation"""
        # Test valid model
        policy = RetryPolicyModel(
            max_retries=5,
            strategy=RetryStrategy.EXPONENTIAL,
            backoff_factor=1000,
            exponent=2,
            max_delay=10000
        )
        
        # Test invalid max_retries (negative)
        with pytest.raises(ValueError):
            RetryPolicyModel(max_retries=-1)
        
        # Test invalid backoff_factor (non-positive)
        with pytest.raises(ValueError):
            RetryPolicyModel(backoff_factor=0)
        
        # Test invalid exponent (non-positive)
        with pytest.raises(ValueError):
            RetryPolicyModel(exponent=0)
        
        # Test invalid max_delay (non-positive)
        with pytest.raises(ValueError):
            RetryPolicyModel(max_delay=0)

    def test_strategy_enum_values(self):
        """Test all RetryStrategy enum values"""
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
            policy = RetryPolicyModel(strategy=strategy)
            assert policy.strategy == strategy
            # Should not raise any exceptions
            delay = policy.compute_delay(1)
            assert isinstance(delay, int)
            assert delay >= 0

    def test_edge_case_large_numbers(self):
        """Test edge cases with large numbers"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.EXPONENTIAL,
            backoff_factor=1000000,
            exponent=10
        )
        
        # Test that large numbers don't cause overflow
        delay = policy.compute_delay(3)
        assert isinstance(delay, int)
        assert delay > 0

    def test_consistency_across_calls(self):
        """Test that non-jitter strategies are consistent"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.EXPONENTIAL,
            backoff_factor=1000,
            exponent=2
        )
        
        # Multiple calls should return the same result for non-jitter strategies
        delay1 = policy.compute_delay(2)
        delay2 = policy.compute_delay(2)
        assert delay1 == delay2

    def test_jitter_variability(self):
        """Test that jitter strategies produce different results"""
        policy = RetryPolicyModel(
            strategy=RetryStrategy.EXPONENTIAL_FULL_JITTER,
            backoff_factor=1000,
            exponent=2
        )
        
        # Multiple calls should return different results for jitter strategies
        delays = set()
        for _ in range(100):
            delay = policy.compute_delay(2)
            delays.add(delay)
        
        # Should have multiple different values (not all the same)
        assert len(delays) > 1 