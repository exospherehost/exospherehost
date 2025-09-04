# API Changes (Beta)

This document outlines the latest beta API changes and enhancements in ExosphereHost.

## StateManager.upsert_graph() - Model-Based Parameters (Beta)

The `upsert_graph` method now supports model-based parameters for improved type safety, validation, and developer experience.

### New Signature

```python
async def upsert_graph(
    self, 
    graph_name: str, 
    graph_nodes: list[GraphNodeModel], 
    secrets: dict[str, str], 
    retry_policy: RetryPolicyModel | None = None, 
    store_config: StoreConfigModel | None = None, 
    validation_timeout: int = 60, 
    polling_interval: int = 1
):
```

### Key Changes

1. **Model-Based Nodes**: `graph_nodes` parameter now expects a list of `GraphNodeModel` objects instead of raw dictionaries
2. **Retry Policy Model**: Optional `retry_policy` parameter using `RetryPolicyModel` with enum-based strategy selection
3. **Store Configuration**: Optional `store_config` parameter using `StoreConfigModel` for graph-level key-value store
4. **Validation Control**: New `validation_timeout` and `polling_interval` parameters for better control over graph validation

### Migration Guide

#### Before (Traditional)
```python
# Old dictionary-based approach
graph_nodes = [
    {
        "node_name": "DataProcessor",
        "namespace": "MyProject",
        "identifier": "processor",
        "inputs": {"data": "initial"},
        "next_nodes": []
    }
]

retry_policy = {
    "max_retries": 3,
    "strategy": "EXPONENTIAL",
    "backoff_factor": 2000
}
```

#### After (Beta Model-Based)
```python
from exospherehost import GraphNodeModel, RetryPolicyModel, RetryStrategyEnum

# New model-based approach
graph_nodes = [
    GraphNodeModel(
        node_name="DataProcessor",
        namespace="MyProject", 
        identifier="processor",
        inputs={"data": "initial"},
        next_nodes=[]
    )
]

retry_policy = RetryPolicyModel(
    max_retries=3,
    strategy=RetryStrategyEnum.EXPONENTIAL,  # Use enum instead of string
    backoff_factor=2000
)
```

### Available Models

#### GraphNodeModel
- **node_name** (str): Class name of the node
- **namespace** (str): Namespace where node is registered  
- **identifier** (str): Unique identifier in the graph
- **inputs** (dict[str, Any]): Input values for the node
- **next_nodes** (Optional[List[str]]): List of next node identifiers
- **unites** (Optional[UnitesModel]): Unite configuration for parallel execution

#### RetryPolicyModel (Beta)
- **max_retries** (int): Maximum number of retry attempts (default: 3)
- **strategy** (RetryStrategyEnum): Retry strategy using enum values (default: EXPONENTIAL)
- **backoff_factor** (int): Base delay in milliseconds (default: 2000)
- **exponent** (int): Exponential multiplier (default: 2)
- **max_delay** (int | None): Maximum delay cap in milliseconds (optional)

#### StoreConfigModel (Beta)
- **required_keys** (list[str]): Keys that must be present in the store
- **default_values** (dict[str, str]): Default values for store keys

### Retry Strategy Enums

```python
from exospherehost import RetryStrategyEnum

# Exponential strategies
RetryStrategyEnum.EXPONENTIAL                  # Pure exponential backoff
RetryStrategyEnum.EXPONENTIAL_FULL_JITTER      # Exponential with full randomization
RetryStrategyEnum.EXPONENTIAL_EQUAL_JITTER     # Exponential with 50% randomization

# Linear strategies  
RetryStrategyEnum.LINEAR                       # Linear backoff
RetryStrategyEnum.LINEAR_FULL_JITTER           # Linear with full randomization
RetryStrategyEnum.LINEAR_EQUAL_JITTER          # Linear with 50% randomization

# Fixed strategies
RetryStrategyEnum.FIXED                        # Fixed delay
RetryStrategyEnum.FIXED_FULL_JITTER            # Fixed with full randomization
RetryStrategyEnum.FIXED_EQUAL_JITTER           # Fixed with 50% randomization
```

### Complete Example

```python
from exospherehost import (
    StateManager, 
    GraphNodeModel, 
    RetryPolicyModel, 
    StoreConfigModel,
    RetryStrategyEnum
)

async def create_advanced_graph():
    state_manager = StateManager(namespace="MyProject")
    
    # Define nodes using models
    graph_nodes = [
        GraphNodeModel(
            node_name="DataLoader",
            namespace="MyProject",
            identifier="loader",
            inputs={"source": "initial"},
            next_nodes=["processor"]
        ),
        GraphNodeModel(
            node_name="DataProcessor", 
            namespace="MyProject",
            identifier="processor",
            inputs={"data": "${{ loader.outputs.data }}"},
            next_nodes=[]
        )
    ]
    
    # Define retry policy with enum
    retry_policy = RetryPolicyModel(
        max_retries=5,
        strategy=RetryStrategyEnum.EXPONENTIAL_FULL_JITTER,
        backoff_factor=1000,
        exponent=2,
        max_delay=30000
    )
    
    # Define store configuration
    store_config = StoreConfigModel(
        required_keys=["cursor", "batch_id"],
        default_values={
            "cursor": "0",
            "batch_size": "100"
        }
    )
    
    # Create graph with all beta features
    result = await state_manager.upsert_graph(
        graph_name="advanced-workflow",
        graph_nodes=graph_nodes,
        secrets={"api_key": "your-key"},
        retry_policy=retry_policy,      # beta
        store_config=store_config,      # beta
        validation_timeout=120,
        polling_interval=2
    )
    
    return result
```

### Benefits

1. **Type Safety**: Pydantic models catch configuration errors at definition time
2. **IDE Support**: Better autocomplete, error detection, and documentation
3. **Validation**: Automatic validation of parameters and relationships
4. **Consistency**: Standardized parameter names and types across the SDK
5. **Extensibility**: Easy to add new fields and maintain backward compatibility

### Beta Status

These features are currently in beta and the API may change based on user feedback. The traditional dictionary-based approach will continue to work alongside the new model-based approach.

For questions or feedback about these beta features, please reach out through our [Discord community](https://discord.com/invite/zT92CAgvkj). 