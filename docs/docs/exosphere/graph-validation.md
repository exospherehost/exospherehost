# Graph Validation

The Exosphere system validates your graph templates to ensure they can execute successfully.

## Validation Rules

### Node Validation
- All nodes must be registered in the specified namespace
- Node identifiers must be unique within the graph
- Node names must match registered node classes exactly

### Input Validation
- Mapped fields must exist in source node schemas
- Input field names must match node input schemas
- No circular dependencies allowed in `next_nodes`

### Secret Validation
- All referenced secrets must be defined in the secrets object
- Secret names must be valid identifiers

## Common Errors

```
ValidationError: Node "DataProcessorNode" not found in namespace "MyProject"
```
**Solution**: Ensure the node is registered or check spelling.

```
ValidationError: Duplicate node identifier: "data_processor"
```
**Solution**: Use unique identifiers for each node.

```
ValidationError: Unknown input field: "raw_data" for node "DataValidatorNode"
```
**Solution**: Check the node's input schema for correct field names.

```
ValidationError: Circular dependency detected in graph
```
**Solution**: Review `next_nodes` configuration to remove circular references.

## Validation in Python SDK

```python
try:
    result = await state_manager.upsert_graph(
        graph_name="my-workflow",
        graph_nodes=graph_nodes,
        secrets=secrets
    )
    print("Graph created successfully!")
    return result
    
except ValidationError as e:
    print(f"Validation failed: {e}")
    return None
```

## Next Steps

- **[Create Graph](./create-graph.md)** - Return to main guide
- **[Graph Components](./graph-components.md)** - Learn about components
- **[Python SDK](./python-sdk-graph.md)** - Use Python SDK for type-safe graph creation

## Related Concepts

- **[Fanout](./fanout.md)** - Create parallel execution paths dynamically
- **[Unite](./unite.md)** - Synchronize parallel execution paths
- **[Retry Policy](./retry-policy.md)** - Build resilient workflows
- **[Store](./store.md)** - Persist data across workflow execution
