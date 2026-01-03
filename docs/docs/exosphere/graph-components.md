# Graph Components

Brief overview of the main components that make up an Exosphere graph.

## 1. Secrets

Configuration data shared across all nodes:

```json
{
  "secrets": {
    "api_key": "your-api-key",
    "database_url": "your-database-url"
  }
}
```

## 2. Nodes

Processing units with inputs and connections:

```json
{
  "nodes": [
    {
      "node_name": "NodeClassName",
      "namespace": "MyProject",
      "identifier": "unique_id",
      "inputs": {
        "field": "value",
        "mapped": "${{ source.outputs.field }}"
      },
      "next_nodes": ["next_node_id"]
    }
  ]
}
```

**Fields:**
- `node_name`: Class name (must be registered)
- `namespace`: Where node is registered
- `identifier`: Unique ID in this graph
- `inputs`: Input values for the node
- `next_nodes`: Connected node IDs

## 3. Input Mapping

Use `${{ ... }}` syntax to map data between nodes:

```json
{
  "inputs": {
    "static": "value",
    "mapped": "${{ source_node.outputs.field }}",
    "initial": "initial"
  }
}
```

- `"initial"`: Value provided when graph is triggered
- `${{ node.outputs.field }}`: Maps output from another node

## 4. Retry Policy

Handle failures automatically:

```json
{
  "retry_policy": {
    "max_retries": 3,
    "strategy": "EXPONENTIAL",
    "backoff_factor": 2000,
    "exponent": 2
  }
}
```

**Strategies:** EXPONENTIAL, LINEAR, FIXED (with jitter variants)

## 5. Store Configuration

Graph-level key-value storage for shared state:

```json
{
  "store_config": {
    "required_keys": ["cursor", "batch_id"],
    "default_values": {
      "cursor": "0",
      "batch_size": "100"
    }
  }
}
```

**Fields:**
- `required_keys`: Keys that must be present in the store
- `default_values`: Default values for store keys

## 6. Triggers

Schedule automatic graph execution using cron expressions:

```json
{
  "triggers": [
    {
      "type": "CRON",
      "value": {
        "expression": "0 9 * * 1-5"
      }
    },
    {
      "type": "CRON",
      "value": {
        "expression": "0 */6 * * *"
      }
    }
  ]
}
```

**Fields:**
- `type`: Currently only "CRON" is supported
- `value.expression`: Standard cron expression (5-field format)

**Common Cron Expressions:**
- `"0 9 * * 1-5"` - Every weekday at 9:00 AM
- `"0 */6 * * *"` - Every 6 hours
- `"0 0 * * 0"` - Every Sunday at midnight
- `"*/15 * * * *"` - Every 15 minutes

## Next Steps

- **[Create Graph](./create-graph.md)** - Return to main guide
- **[Graph Models](./python-sdk-graph.md)** - Use Python SDK for type-safe graph creation
- **[Triggers](./triggers.md)** - Schedule automatic graph execution

## Related Concepts

- **[Fanout](./fanout.md)** - Create parallel execution paths dynamically
- **[Unite](./unite.md)** - Synchronize parallel execution paths
- **[Retry Policy](./retry-policy.md)** - Build resilient workflows
- **[Store](./store.md)** - Persist data across workflow execution
