# Python SDK

Use the Exosphere Python SDK with Pydantic models for type-safe graph creation.

## Basic Usage

```python hl_lines="42-48"
from exospherehost import StateManager, GraphNodeModel, RetryPolicyModel, StoreConfigModel, CronTrigger, RetryStrategyEnum

async def create_graph():
    state_manager = StateManager(
        namespace="MyProject",
        state_manager_uri=EXOSPHERE_STATE_MANAGER_URI,
        key=EXOSPHERE_API_KEY
    )
    
    graph_nodes = [
        GraphNodeModel(
            node_name="DataLoaderNode",
            namespace="MyProject",
            identifier="loader",
            inputs={"source": "initial"},
            next_nodes=["processor"]
        ),
        GraphNodeModel(
            node_name="DataProcessorNode",
            namespace="MyProject",
            identifier="processor",
            inputs={"data": "${{ loader.outputs.data }}"},
            next_nodes=[]
        )
    ]
    
    retry_policy = RetryPolicyModel(
        max_retries=3,
        strategy=RetryStrategyEnum.EXPONENTIAL,
        backoff_factor=2000,
        exponent=2
    )
    
    store_config = StoreConfigModel(
        required_keys=["cursor", "batch_id"],
        default_values={
            "cursor": "0",
            "batch_size": "100"
        }
    )
    
    triggers = [
        CronTrigger(expression="0 9 * * 1-5"),  # Every weekday at 9 AM
        CronTrigger(expression="0 */6 * * *")   # Every 6 hours
    ]
    
    result = await state_manager.upsert_graph(
        graph_name="my-workflow",
        graph_nodes=graph_nodes,
        secrets={"api_key": "your-key"},
        retry_policy=retry_policy,
        store_config=store_config,
        triggers=triggers  # Beta: SDK version 0.0.3b1
    )
    return result
```

## Models

### GraphNodeModel
```python
GraphNodeModel(
    node_name="NodeClassName",      # Must be registered
    namespace="MyProject",          # Node namespace
    identifier="unique_id",         # Unique in graph
    inputs={                        # Input values
        "field": "value",
        "mapped": "${{ other.outputs.field }}"
    },
    next_nodes=["next_node_id"]     # Connected nodes
)
```

**Fields:**

- **`node_name`** (str): The class name of the node that must be registered in the Exosphere runtime
- **`namespace`** (str): The project namespace for organizing and isolating nodes
- **`identifier`** (str): A unique identifier within the graph, used for referencing this node
- **`inputs`** (dict): Key-value pairs defining the input parameters for the node execution
- **`next_nodes`** (list[str]): List of node identifiers that this node connects to in the workflow

### RetryPolicyModel
```python
RetryPolicyModel(
    max_retries=3,                 # Max retry attempts
    strategy=RetryStrategyEnum.EXPONENTIAL,  # Strategy enum
    backoff_factor=2000,           # Base delay (ms)
    exponent=2                     # Multiplier
)
```

**Fields:**

- **`max_retries`** (int): Maximum number of retry attempts before marking the node as failed
- **`strategy`** (RetryStrategyEnum): The retry strategy to use (EXPONENTIAL, LINEAR, FIXED)
- **`backoff_factor`** (int): Base delay in milliseconds before the first retry attempt
- **`exponent`** (int): Multiplier for exponential backoff calculations

### StoreConfigModel
```python
StoreConfigModel(
    required_keys=["cursor", "batch_id"],  # Keys that must be present
    default_values={                       # Default values for keys
        "cursor": "0",
        "batch_size": "100"
    }
)
```

**Fields:**

- **`required_keys`** (list[str]): List of keys that must be present in the store for the graph to function
- **`default_values`** (dict): Default values for store keys when they are not present

## Retry Strategies

Available strategies from `RetryStrategyEnum`:

- `EXPONENTIAL`, `LINEAR`, `FIXED`
- Add `_FULL_JITTER` or `_EQUAL_JITTER` for jitter variants

More info: [Retry Policies Guide](./retry-policy.md)

## Next Steps

- **[Create Graph](./create-graph.md)** - Return to main guide
- **[Graph Components](./graph-components.md)** - Learn about components

## Related Concepts

- **[Fanout](./fanout.md)** - Create parallel execution paths dynamically
- **[Unite](./unite.md)** - Synchronize parallel execution paths
- **[Retry Policy](./retry-policy.md)** - Build resilient workflows
- **[Store](./store.md)** - Persist data across workflow execution
