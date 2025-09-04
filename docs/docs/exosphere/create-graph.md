# Create Graph

Graphs in Exosphere define executions by connecting nodes together. A graph template specifies the nodes, their connections, and how data flows between them.

## Graph Structure

A graph template consists of:

- **Nodes**: The processing units in your workflow with their inputs and next nodes
- **Secrets**: Configuration data shared across nodes
- **Input Mapping**: How data flows between nodes using `${{ ... }}` syntax
- **Retry Policy**: `Optional` failure handling configuration 
- **Store Configuration**: `Optional` graph-level key-value store

## Basic Example of a Graph Template

```json
{
  "secrets": {
    "api_key": "your-api-key"
  },
  "nodes": [
    {
      "node_name": "DataLoaderNode",
      "namespace": "MyProject",
      "identifier": "loader",
      "inputs": {"source": "initial"},
      "next_nodes": ["processor"]
    },
    {
      "node_name": "DataProcessorNode",
      "namespace": "MyProject",
      "identifier": "processor",
      "inputs": {"data": "${{ loader.outputs.data }}"},
      "next_nodes": []
    }
  ]
}
```

## Quick Start with Python SDK

```python
from exospherehost import StateManager, GraphNodeModel

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
    
    result = await state_manager.upsert_graph(
        graph_name="my-workflow",
        graph_nodes=graph_nodes,
        secrets={"api_key": "your-key"}
    )
    return result
```

## Next Steps

- **[Graph Components](./graph-components.md)** - Learn about secrets, nodes, and retry policy
- **[Python SDK](./python-sdk-graph.md)** - Use Python SDK with Pydantic models
- **[Graph Validation](./graph-validation.md)** - Learn about validation rules
- **[Trigger Graph](./trigger-graph.md)** - Trigger your workflows on created Graph

## Related Concepts

- **[Fanout](./fanout.md)** - Create parallel execution paths dynamically
- **[Unite](./unite.md)** - Synchronize parallel execution paths
- **[Retry Policy](./retry-policy.md)** - Build resilient workflows
- **[Store](./store.md)** - Persist data across workflow execution
