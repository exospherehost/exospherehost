# State Manager Tests

This directory contains comprehensive unit tests for the state-manager application.

## Test Structure

```
tests/
├── unit/
│   └── controller/
│       ├── test_create_states.py
│       ├── test_enqueue_states.py
│       ├── test_executed_state.py
│       ├── test_errored_state.py
│       ├── test_get_graph_template.py
│       ├── test_get_secrets.py
│       ├── test_register_nodes.py
│       └── test_upsert_graph_template.py
└── README.md
```

## Test Coverage

The unit tests cover all controller functions in the state-manager:

### 1. `create_states.py`
- ✅ Successful state creation
- ✅ Graph template not found scenarios
- ✅ Node template not found scenarios
- ✅ Database error handling
- ✅ Multiple states creation

### 2. `enqueue_states.py`
- ✅ Successful state enqueuing
- ✅ No states found scenarios
- ✅ Multiple states enqueuing
- ✅ Database error handling
- ✅ Different batch sizes

### 3. `executed_state.py`
- ✅ Successful state execution with single output
- ✅ Multiple outputs handling
- ✅ State not found scenarios
- ✅ Invalid state status scenarios
- ✅ Empty outputs handling
- ✅ Database error handling

### 4. `errored_state.py`
- ✅ Successful error marking for queued states
- ✅ Successful error marking for executed states
- ✅ State not found scenarios
- ✅ Invalid state status scenarios
- ✅ Different error messages
- ✅ Database error handling

### 5. `get_graph_template.py`
- ✅ Successful template retrieval
- ✅ Template not found scenarios
- ✅ Validation errors handling
- ✅ Pending validation scenarios
- ✅ Empty nodes handling
- ✅ Complex secrets structure
- ✅ Database error handling

### 6. `get_secrets.py`
- ✅ Successful secrets retrieval
- ✅ State not found scenarios
- ✅ Namespace mismatch scenarios
- ✅ Graph template not found scenarios
- ✅ Empty secrets handling
- ✅ Complex secrets structure
- ✅ Nested secrets handling
- ✅ Database error handling

### 7. `register_nodes.py`
- ✅ New node registration
- ✅ Existing node updates
- ✅ Multiple nodes registration
- ✅ Empty secrets handling
- ✅ Complex schema handling
- ✅ Database error handling

### 8. `upsert_graph_template.py`
- ✅ Existing template updates
- ✅ New template creation
- ✅ Empty nodes handling
- ✅ Complex node structures
- ✅ Validation errors handling
- ✅ Database error handling

## Running Tests

### Prerequisites

Make sure you have the development dependencies installed:

```bash
uv sync --group dev
```

### Run All Tests

```bash
pytest
```

### Run Unit Tests Only

```bash
pytest tests/unit/
```

### Run Specific Test File

```bash
pytest tests/unit/controller/test_create_states.py
```

### Run Tests with Coverage

```bash
pytest --cov=app tests/
```

### Run Tests with Verbose Output

```bash
pytest -v
```

### Run Tests and Generate HTML Coverage Report

```bash
pytest --cov=app --cov-report=html tests/
```

## Test Patterns

### Async Testing
All controller functions are async, so tests use `pytest-asyncio` and the `async def` pattern.

### Mocking
Tests use `unittest.mock` to mock:
- Database operations (Beanie ODM)
- External dependencies
- Background tasks
- Logging

### Fixtures
Common test fixtures are defined for:
- Mock request IDs
- Mock namespaces
- Mock data structures
- Mock database objects

### Error Handling
Tests cover both success and error scenarios:
- HTTP exceptions (404, 400, etc.)
- Database errors
- Validation errors
- Business logic errors

## Adding New Tests

When adding new tests:

1. Follow the existing naming convention: `test_*.py`
2. Use descriptive test method names
3. Include both success and error scenarios
4. Mock external dependencies
5. Use fixtures for common test data
6. Add proper docstrings explaining test purpose

## Test Quality Standards

- Each test should be independent
- Tests should be fast and reliable
- Use meaningful assertions
- Mock external dependencies
- Test both happy path and error scenarios
- Include edge cases and boundary conditions

