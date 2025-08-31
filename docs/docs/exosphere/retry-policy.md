# Retry Policy

!!! beta "Beta Feature"
    Retry Policy is currently available in beta. The API and functionality may change in future releases.

The Retry Policy feature in Exosphere provides sophisticated retry mechanisms for handling transient failures in your workflow nodes. When a node execution fails, the retry policy automatically determines when and how to retry the execution based on configurable strategies.

## Overview

Retry policies are configured at the graph level and apply to all nodes within that graph. When a node fails with an error, the state manager automatically creates a retry state with a calculated delay before the next execution attempt.

## Configuration

Retry policies are defined in your graph template configuration:

```json
{
  "secrets": {
    "api_key": "your-api-key"
  },
  "nodes": [
    {
      "node_name": "MyNode",
      "namespace": "MyProject",
      "identifier": "my_node",
      "inputs": {
        "data": "initial"
      },
      "next_nodes": []
    }
  ],
  "retry_policy": {
    "max_retries": 3,
    "strategy": "EXPONENTIAL",
    "backoff_factor": 2000,
    "exponent": 2,
    "max_delay": 3600000
  }
}
```

## Parameters

### max_retries

- **Type**: `int`
- **Default**: `3`
- **Description**: The maximum number of retry attempts before giving up
- **Constraints**: Must be >= 0

### strategy

- **Type**: `string`
- **Default**: `"EXPONENTIAL"`
- **Description**: The retry strategy to use for calculating delays
- **Options**: See [Retry Strategies](#retry-strategies) below

### backoff_factor

- **Type**: `int` (milliseconds)
- **Default**: `2000` (2 seconds)
- **Description**: The base delay factor in milliseconds
- **Constraints**: Must be > 0

### exponent

- **Type**: `int`
- **Default**: `2`
- **Description**: The exponent used for exponential strategies
- **Constraints**: Must be > 0

### max_delay

- **Type**: `int | null` (milliseconds)
- **Default**: `null` (no maximum delay)
- **Description**: The maximum delay in milliseconds that any retry attempt can have. When set, all calculated delays are capped at this value using the `_cap` function
- **Constraints**: Must be > 0 when not null
- **Example**: `3600000` (1 hour) would cap all delays to a maximum of 1 hour

## Retry Strategies

Exosphere supports three main categories of retry strategies, each with jitter variants to prevent thundering herd problems.

### Exponential Strategies

Exponential strategies increase the delay exponentially with each retry attempt.

#### EXPONENTIAL

Standard exponential backoff without jitter.

**Formula**: `backoff_factor * (exponent ^ (retry_count - 1))`

**Example**:

- Retry 1: 2000ms (2 seconds)
- Retry 2: 4000ms (4 seconds)
- Retry 3: 8000ms (8 seconds)

#### EXPONENTIAL_FULL_JITTER

Exponential backoff with full jitter (random delay between 0 and calculated delay).

**Formula**: `random(0, backoff_factor * (exponent ^ (retry_count - 1)))`

*Note: `random(a, b)` denotes a uniform random draw over the inclusive range [a, b].*

**Example**:

- Retry 1: 0-2000ms (random)
- Retry 2: 0-4000ms (random)
- Retry 3: 0-8000ms (random)

#### EXPONENTIAL_EQUAL_JITTER

Exponential backoff with equal jitter (random delay around half the calculated delay).

**Formula**: `(backoff_factor * (exponent ^ (retry_count - 1))) / 2 + random(0, (backoff_factor * (exponent ^ (retry_count - 1))) / 2)`

*Note: `random(a, b)` denotes a uniform random draw over the inclusive range [a, b].*

**Example**:

- Retry 1: 1000-2000ms (random)
- Retry 2: 2000-4000ms (random)
- Retry 3: 4000-8000ms (random)

### Linear Strategies

Linear strategies increase the delay linearly with each retry attempt.

#### LINEAR

Standard linear backoff without jitter.

**Formula**: `backoff_factor * retry_count`

**Example**:

- Retry 1: 2000ms (2 seconds)
- Retry 2: 4000ms (4 seconds)
- Retry 3: 6000ms (6 seconds)

#### LINEAR_FULL_JITTER

Linear backoff with full jitter.

**Formula**: `random(0, backoff_factor * retry_count)`

*Note: `random(a, b)` denotes a uniform random draw over the inclusive range [a, b].*

**Example**:

- Retry 1: 0-2000ms (random)
- Retry 2: 0-4000ms (random)
- Retry 3: 0-6000ms (random)

#### LINEAR_EQUAL_JITTER

Linear backoff with equal jitter.

**Formula**: `(backoff_factor * retry_count) / 2 + random(0, (backoff_factor * retry_count) / 2)`

*Note: `random(a, b)` denotes a uniform random draw over the inclusive range [a, b].*

**Example**:

- Retry 1: 1000-2000ms (random)
- Retry 2: 2000-4000ms (random)
- Retry 3: 3000-6000ms (random)

### Fixed Strategies

Fixed strategies use a constant delay for all retry attempts.

#### FIXED

Standard fixed delay without jitter.

**Formula**: `backoff_factor`

**Example**:

- Retry 1: 2000ms (2 seconds)
- Retry 2: 2000ms (2 seconds)
- Retry 3: 2000ms (2 seconds)

#### FIXED_FULL_JITTER

Fixed delay with full jitter.

**Formula**: `random(0, backoff_factor)`

*Note: `random(a, b)` denotes a uniform random draw over the inclusive range [a, b].*

**Example**:

- Retry 1: 0-2000ms (random)
- Retry 2: 0-2000ms (random)
- Retry 3: 0-2000ms (random)

#### FIXED_EQUAL_JITTER

Fixed delay with equal jitter.

**Formula**: `backoff_factor / 2 + random(0, backoff_factor / 2)`

*Note: `random(a, b)` denotes a uniform random draw over the inclusive range [a, b].*

**Example**:

- Retry 1: 1000-2000ms (random)
- Retry 2: 1000-2000ms (random)
- Retry 3: 1000-2000ms (random)

## Delay Capping

The retry policy includes a built-in delay capping mechanism through the `_cap` function and `max_delay` parameter. This ensures that retry delays never exceed a specified maximum value, even with aggressive exponential backoff strategies.

### How Delay Capping Works

The `_cap` function is applied to all calculated delays:

```python
def _cap(value: int) -> int:
    if self.max_delay is not None:
        return min(value, self.max_delay)
    return value
```

**Behavior:**
- If `max_delay` is set, all calculated delays are capped at this value
- If `max_delay` is `null` (default), no capping is applied
- The capping is applied after all strategy calculations.

### Example with Delay Capping

Consider an exponential strategy with `backoff_factor: 2000`, `exponent: 2`, and `max_delay: 10000`:

**With capping:**
- Retry 1: 2000ms
- Retry 2: 4000ms
- Retry 3: 8000ms
- Retry 4: 10000ms (capped at max_delay)

### When to Use Delay Capping

- **Long-running workflows**: Prevent excessive delays that could impact overall workflow completion time
- **User-facing applications**: Ensure retries don't create unacceptable wait times
- **Resource management**: Control resource consumption by limiting retry delays
- **Predictable behavior**: Create more predictable retry patterns for monitoring and alerting

## Usage Examples

### Basic Exponential Retry

```json
{
  "retry_policy": {
    "max_retries": 3,
    "strategy": "EXPONENTIAL",
    "backoff_factor": 1000,
    "exponent": 2
  }
}
```

### Aggressive Retry with Jitter

```json
{
  "retry_policy": {
    "max_retries": 5,
    "strategy": "EXPONENTIAL_FULL_JITTER",
    "backoff_factor": 500,
    "exponent": 3
  }
}
```

### Conservative Linear Retry

```json
{
  "retry_policy": {
    "max_retries": 2,
    "strategy": "LINEAR",
    "backoff_factor": 5000
  }
}
```

### Fixed Retry for Rate Limiting

```json
{
  "retry_policy": {
    "max_retries": 10,
    "strategy": "FIXED_EQUAL_JITTER",
    "backoff_factor": 1000
  }
}
```

### Exponential Retry with Delay Capping

```json
{
  "retry_policy": {
    "max_retries": 5,
    "strategy": "EXPONENTIAL",
    "backoff_factor": 2000,
    "exponent": 2,
    "max_delay": 30000
  }
}
```

### Conservative Retry with Maximum Delay

```json
{
  "retry_policy": {
    "max_retries": 3,
    "strategy": "EXPONENTIAL_FULL_JITTER",
    "backoff_factor": 1000,
    "exponent": 3,
    "max_delay": 60000
  }
}
```

## When Retries Are Triggered

Retries are automatically triggered when:

1. A node execution fails with an error
2. The current retry count is less than `max_retries`
3. The state status is `QUEUED` or `EXECUTED`

The retry mechanism:

- Creates a new state with `retry_count` incremented by 1
- Sets `enqueue_after` to the current time plus the calculated delay
- Sets the original state status to `ERRORED` with the error message

## Best Practices

### Choose the Right Strategy

- **EXPONENTIAL**: Best for most transient failures (network issues, temporary service unavailability)
- **LINEAR**: Good for predictable, consistent delays
- **FIXED**: Useful for rate limiting scenarios

### Use Jitter for High Concurrency

- **FULL_JITTER**: Best for high concurrency to prevent thundering herd
- **EQUAL_JITTER**: Good balance between predictability and randomization
- **No Jitter**: Use only when you need deterministic behavior

### Set Appropriate Limits

- **max_retries**: Consider the nature of your failures and downstream dependencies
- **backoff_factor**: Balance between responsiveness and resource usage
- **exponent**: Higher values create more aggressive backoff
- **max_delay**: Set a reasonable maximum delay to prevent excessive wait times, especially for exponential strategies

### Monitor Retry Patterns

- Track retry counts in your monitoring system
- Set up alerts for graphs with high retry rates
- Analyze retry patterns to identify systemic issues

## Limitations

- Retry policies apply to all nodes in a graph uniformly
- Individual node-level retry policies are not supported
- Retry delays are calculated in milliseconds
- Maximum delay can be capped using the `max_delay` parameter (recommended for long-running workflows)

## Error Handling

If a retry policy configuration is invalid:

- The graph template validation will fail
- An error will be returned during graph creation
- The graph will not be saved until the configuration is corrected

## Integration with Signals

Retry policies work alongside Exosphere's signaling system:

- Nodes can still raise `PruneSignal` to stop retries immediately
- Nodes can raise `ReQueueAfterSignal` to re-queue after some time. This will not mark nodes as failures.
- The retry count is preserved when using signals. 