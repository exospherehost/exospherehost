import pytest
from unittest.mock import MagicMock

from app.singletons.SingletonDecorator import singleton


class TestSingletonDecorator:
    """Test cases for singleton decorator function"""

    def test_singleton_decorator_creates_single_instance(self):
        """Test that singleton decorator ensures only one instance is created"""
        
        @singleton
        class TestClass:
            def __init__(self):
                self.value = "test"
        
        # Create multiple instances
        instance1 = TestClass()
        instance2 = TestClass()
        instance3 = TestClass()
        
        # All should be the same object
        assert instance1 is instance2
        assert instance2 is instance3
        assert instance1 is instance3

    def test_singleton_decorator_preserves_class_functionality(self):
        """Test that singleton decorator preserves class methods and attributes"""
        
        @singleton
        class TestClass:
            def __init__(self, value):
                self.value = value
                self.counter = 0
            
            def increment(self):
                self.counter += 1
                return self.counter
            
            def get_value(self):
                return self.value
        
        instance1 = TestClass("first")
        instance2 = TestClass("second")  # This should be ignored due to singleton
        
        # Should be the same instance
        assert instance1 is instance2
        
        # Should preserve the original initialization (first call)
        assert instance1.get_value() == "first"
        assert instance2.get_value() == "first"
        
        # Method calls should work and share state
        assert instance1.increment() == 1
        assert instance2.increment() == 2  # Same counter, incremented
        assert instance1.counter == 2

    def test_singleton_decorator_with_no_args_constructor(self):
        """Test singleton decorator with class that has no constructor arguments"""
        
        @singleton
        class SimpleClass:
            def __init__(self):
                self.created = True
        
        instance1 = SimpleClass()
        instance2 = SimpleClass()
        
        assert instance1 is instance2
        assert instance1.created is True
        assert instance2.created is True

    def test_singleton_decorator_with_multiple_args(self):
        """Test singleton decorator with class that accepts multiple arguments"""
        
        @singleton
        class MultiArgClass:
            def __init__(self, arg1, arg2, kwarg1=None, kwarg2="default"):
                self.arg1 = arg1
                self.arg2 = arg2
                self.kwarg1 = kwarg1
                self.kwarg2 = kwarg2
        
        # First instance with specific args
        instance1 = MultiArgClass("first", "second", kwarg1="kw1", kwarg2="kw2")
        
        # Second instance with different args (should be ignored)
        instance2 = MultiArgClass("different", "args", kwarg1="ignored", kwarg2="ignored")
        
        assert instance1 is instance2
        
        # Should preserve first initialization
        assert instance1.arg1 == "first"
        assert instance1.arg2 == "second"
        assert instance1.kwarg1 == "kw1"
        assert instance1.kwarg2 == "kw2"
        
        # instance2 should have the same values
        assert instance2.arg1 == "first"
        assert instance2.arg2 == "second"
        assert instance2.kwarg1 == "kw1"
        assert instance2.kwarg2 == "kw2"

    def test_singleton_decorator_with_different_classes(self):
        """Test that singleton decorator works independently for different classes"""
        
        @singleton
        class ClassA:
            def __init__(self):
                self.type = "A"
        
        @singleton
        class ClassB:
            def __init__(self):
                self.type = "B"
        
        # Each class should have its own singleton instance
        a1 = ClassA()
        a2 = ClassA()
        b1 = ClassB()
        b2 = ClassB()
        
        # Same class instances should be identical
        assert a1 is a2
        assert b1 is b2
        
        # Different class instances should be different
        assert a1 is not b1
        assert a2 is not b2
        
        # Each should preserve their own properties
        assert a1.type == "A"
        assert b1.type == "B"

    def test_singleton_decorator_preserves_class_name(self):
        """Test that singleton decorator preserves original class name"""
        
        @singleton
        class NamedClass:
            pass
        
        instance = NamedClass()
        
        # The returned function should still reference the original class
        # Note: The decorator returns a function, not a class, but the instance
        # should still be of the original class type
        assert instance.__class__.__name__ == "NamedClass"

    def test_singleton_decorator_thread_safety_simulation(self):
        """Test singleton decorator behavior under simulated concurrent access"""
        
        call_count = 0
        
        @singleton
        class CountedClass:
            def __init__(self):
                nonlocal call_count
                call_count += 1
                self.instance_id = call_count
        
        # Simulate multiple "concurrent" calls
        instances = []
        for _ in range(10):
            instances.append(CountedClass())
        
        # All instances should be the same
        first_instance = instances[0]
        for instance in instances[1:]:
            assert instance is first_instance
        
        # Constructor should only be called once
        assert call_count == 1
        assert first_instance.instance_id == 1

    def test_singleton_decorator_with_methods_and_properties(self):
        """Test singleton decorator preserves methods and properties"""
        
        @singleton
        class MethodClass:
            def __init__(self):
                self._internal_value = 42
            
            @property
            def value(self):
                return self._internal_value
            
            @value.setter
            def value(self, new_value):
                self._internal_value = new_value
            
            def calculate(self, multiplier):
                return self._internal_value * multiplier
            
            @staticmethod
            def static_method():
                return "static"
            
            @classmethod
            def class_method(cls):
                return cls.__name__
        
        instance1 = MethodClass()
        instance2 = MethodClass()
        
        assert instance1 is instance2
        
        # Test property access
        assert instance1.value == 42
        assert instance2.value == 42
        
        # Test property setting
        instance1.value = 100
        assert instance2.value == 100  # Should be shared
        
        # Test method calls
        assert instance1.calculate(2) == 200
        assert instance2.calculate(3) == 300
        
        # Test static and class methods
        assert instance1.static_method() == "static"
        assert instance2.static_method() == "static"
        assert instance1.class_method() == "MethodClass"

    def test_singleton_decorator_with_exception_in_constructor(self):
        """Test singleton decorator behavior when constructor raises exception"""
        
        @singleton
        class FailingClass:
            def __init__(self, should_fail=True):
                if should_fail:
                    raise ValueError("Constructor failed")
                self.success = True
        
        # First call with failure
        with pytest.raises(ValueError, match="Constructor failed"):
            FailingClass()
        
        # Second call with failure (should try to create again since first failed)
        with pytest.raises(ValueError, match="Constructor failed"):
            FailingClass()
        
        # The singleton pattern should handle constructor failures gracefully
        # After failure, the class should still not be in instances dict

    def test_singleton_decorator_instances_isolation(self):
        """Test that singleton decorator maintains separate instances dict per decorated class"""
        
        # Test that different decorations maintain separate state
        @singleton
        class FirstSingleton:
            def __init__(self):
                self.name = "first"
        
        @singleton
        class SecondSingleton:
            def __init__(self):
                self.name = "second"
        
        first = FirstSingleton()
        second = SecondSingleton()
        
        # Should be different instances
        assert first is not second
        assert first.name != second.name
        
        # Multiple calls should return same instance for each class
        first_again = FirstSingleton()
        second_again = SecondSingleton()
        
        assert first is first_again
        assert second is second_again

    def test_singleton_decorator_callable_return_value(self):
        """Test that singleton decorator returns a callable"""
        
        @singleton
        class TestClass:
            pass
        
        # The decorator should return a callable (the get_instance function)
        assert callable(TestClass)
        
        # Calling it should return an instance
        instance = TestClass()
        assert instance is not None
        assert hasattr(instance, '__class__')

    def test_singleton_decorator_with_complex_initialization(self):
        """Test singleton decorator with complex initialization logic"""
        
        initialization_count = 0
        
        @singleton
        class ComplexClass:
            def __init__(self, config=None):
                nonlocal initialization_count
                initialization_count += 1
                
                self.config = config or {}
                self.initialized_at = initialization_count
                self.cache = {}
                
                # Simulate complex initialization
                self._setup_internal_state()
            
            def _setup_internal_state(self):
                self.internal_state = "configured"
        
        # First initialization
        instance1 = ComplexClass({"setting": "value1"})
        assert initialization_count == 1
        assert instance1.config == {"setting": "value1"}
        assert instance1.initialized_at == 1
        assert instance1.internal_state == "configured"
        
        # Second call (should return same instance, ignore new config)
        instance2 = ComplexClass({"setting": "value2"})  
        assert initialization_count == 1  # No additional initialization
        assert instance1 is instance2
        assert instance2.config == {"setting": "value1"}  # Original config preserved
        assert instance2.initialized_at == 1