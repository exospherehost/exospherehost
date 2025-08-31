# Create Graph

Graphs in Exosphere define executions by connecting nodes together. A graph template specifies the nodes, their connections, and how data flows between them. This guide shows you how to create and manage graph templates.

## Graph Structure

A graph template consists of:

- **Nodes**: The processing units in your workflow with their inputs and next nodes
- **Secrets**: Configuration data shared across nodes
- **Input Mapping**: How data flows between nodes using `${{ ... }}` syntax

## Basic Graph Example

One can define a graph on Exosphere through a simple json config, which specifies the nodes and their relationships on the graph.

```json
{
  "secrets": {
    "openai_api_key": "your-openai-key",
    "database_url": "your-database-url"
  },
  "nodes": [
    {
      "node_name": "DataLoaderNode",
      "namespace": "MyProject",
      "identifier": "data_loader",
      "inputs": {
        "source": "initial",
        "format": "json"
      },
      "next_nodes": ["data_processor"]
    },
    {
      "node_name": "DataProcessorNode",
      "namespace": "MyProject", 
      "identifier": "data_processor",
      "inputs": {
        "raw_data": "${{ data_loader.outputs.processed_data }}",
        "config": "initial"
      },
      "next_nodes": ["data_validator"]
    },
    {
      "node_name": "DataValidatorNode",
      "namespace": "MyProject",
      "identifier": "data_validator",
      "inputs": {
        "data": "${{ data_processor.outputs.processed_data }}",
        "validation_rules": "initial"
      },
      "next_nodes": []
    }
  ],
  "retry_policy": {
    "max_retries": 3,
    "strategy": "EXPONENTIAL",
    "backoff_factor": 2000,
    "exponent": 2
  }
}
```

## Components

### Secrets

Define secrets as an object with key-value pairs:

```json
{
  "secrets": {
    "openai_api_key": "your-openai-key",
    "aws_access_key_id": "your-aws-key",
    "aws_secret_access_key": "your-aws-secret",
    "aws_region": "us-east-1",
    "database_url": "your-database-url"
  }
}
```

**Fields:**

- **Keys**: Secret names that will be available to all nodes
- **Values**: The actual secret values (in production, these should be encrypted)

### Nodes

Define the nodes in your workflow with their inputs and next nodes:

```json
{
  "nodes": [
    {
      "node_name": "NodeClassName",
      "namespace": "MyProject",
      "identifier": "unique_node_id",
      "inputs": {
        "input_field": "initial_value",
        "mapped_field": "${{ source_node.outputs.output_field }}"
      },
      "next_nodes": ["next_node_identifier"]
    }
  ]
}
```

**Fields:**

- **`node_name`**: The class name of the node (must be registered)
- **`namespace`**: The namespace where the node is registered
- **`identifier`**: Unique identifier for the node in this graph
- **`inputs`**: Input values for the node
- **`next_nodes`**: Array of node identifiers that this node connects to

### Input Mapping

Use the `${{ ... }}` syntax to map outputs from previous nodes:

```json
{
  "inputs": {
    "static_value": "initial",
    "mapped_value": "${{ source_node.outputs.output_field }}",
    "nested_mapping": "${{ source_node.outputs.nested.field }}"
  }
}
```

**Mapping Syntax:**

- **`${{ node_identifier.outputs.field_name }}`**: Maps output from a specific node
- **`initial`**: Static value provided when the graph is triggered
- **Direct values**: String values. In v1, numbers/booleans must be string-encoded (e.g., "42", "true").

### Retry Policy

Graphs can include a retry policy to handle transient failures automatically. The retry policy is configured at the graph level and applies to all nodes within the graph.

```json
{
  "retry_policy": {
    "max_retries": 3,
    "strategy": "EXPONENTIAL",
    "backoff_factor": 2000, // milliseconds
    "exponent": 2
  }
}
```

For detailed information about retry policies, including all available strategies and configuration options, see the [Retry Policy](retry-policy.md) documentation.

## Creating Graph Templates

The recommended way to create graph templates is using the Exosphere Python SDK, which provides a clean interface to the State Manager API.

```python hl_lines="5-9 23-27"
from exospherehost import StateManager

async def create_graph_template():
    # Initialize the State Manager
    state_manager = StateManager(
        namespace="MyProject",
        state_manager_uri=EXOSPHERE_STATE_MANAGER_URI,
        key=EXOSPHERE_API_KEY
    )
    
    # Define the graph nodes
    graph_nodes = [
       ... #nodes from the namespace MyProject
    ]
    
    # Define secrets
    secrets = {
        ...  # Store real values in a secret manager or environment variables, not in code.
    }
    
    try:
        # Create or update the graph template
        result = await state_manager.upsert_graph(
            graph_name="my-workflow",
            graph_nodes=graph_nodes,
            secrets=secrets,
            retry_policy={
                "max_retries": 3,
                "strategy": "EXPONENTIAL",
                "backoff_factor": 2000,
                "exponent": 2
            }
        )
        print("Graph template created successfully!")
        print(f"Validation status: {result['validation_status']}")
        return result
    except Exception as e:
        print(f"Error creating graph template: {e}")
        raise

# Run the function
import asyncio
asyncio.run(create_graph_template())
```
## Input Mapping Patterns

=== "Field Mapping"

    ```json
    {
      "inputs": {
        "data": "${{ source_node.outputs.data }}"
      }
    }
    ```

=== "Static Values"

    ```json
    {
      "inputs": {
        "config_value": "static_value",
        "number_value": "42",
        "boolean_value": "true"
      }
    }
    ```

## Graph Validation

The state manager validates your graph template:

### Node Validation

- All nodes must be registered in the specified namespace
- Node identifiers must be unique within the graph
- Node names must match registered node classes

### Input Validation

- Mapped fields must exist in source node schemas
- Input field names must match node input schemas
- No circular dependencies allowed in `next_nodes`

### Secret Validation

- All referenced secrets must be defined in the secrets object
- Secret names must be valid identifiers

## Graph Management

=== "Get Graph Template"

    ```python hl_lines="11"
    from exospherehost import StateManager

    async def get_graph_template():
        state_manager = StateManager(
            namespace="MyProject",
            state_manager_uri=EXOSPHERE_STATE_MANAGER_URI,
            key=EXOSPHERE_API_KEY
        )
        
        try:
            graph_info = await state_manager.get_graph("my-workflow")
            print(f"Graph validation status: {graph_info['validation_status']}")
            print(f"Number of nodes: {len(graph_info['nodes'])}")
            print(f"Validation errors: {graph_info['validation_errors']}")
            return graph_info
        except Exception as e:
            print(f"Error getting graph template: {e}")
            raise

    # Get graph information
    graph_info = asyncio.run(get_graph_template())
    ```

=== "Update Graph Template"

    ```python hl_lines="17 21-25"
    async def update_graph_template():
        state_manager = StateManager(
            namespace="MyProject",
            state_manager_uri=EXOSPHERE_STATE_MANAGER_URI,
            key=EXOSPHERE_API_KEY
        )
        
        # Updated graph nodes
        updated_nodes = [
            ...
        ]
        
        # Updated secrets
        updated_secrets = {
            "openai_api_key": "your-openai-key",
            "database_url": "your-database-url",
            "logging_endpoint": "your-logging-endpoint"  # Added new secret
        }
        
        try:
            result = await state_manager.upsert_graph(
                graph_name="my-workflow",
                graph_nodes=updated_nodes,
                secrets=updated_secrets,
                retry_policy={
                    "max_retries": 3,
                    "strategy": "EXPONENTIAL",
                    "backoff_factor": 2000,
                    "exponent": 2
                }
            )
            print("Graph template updated successfully!")
            print(f"Validation status: {result['validation_status']}")
            return result
        except Exception as e:
            print(f"Error updating graph template: {e}")
            raise

    # Update the graph
    asyncio.run(update_graph_template())
    ```

## Graph Visualization

The Exosphere dashboard provides visual representation of your graphs. Checkout the [Dashboard Guide](./dashboard.md)

- **Node View**: See all nodes and their connections via `next_nodes`
- **Execution Flow**: Track how data flows through the graph using input mapping
- **State Monitoring**: Monitor execution states in real-time
- **Error Tracking**: Identify and debug failed executions

## Next Steps

- **[Trigger Graph](./trigger-graph.md)** - Learn how to execute your workflows
- **[Dashboard](./dashboard.md)** - Use the Exosphere dashboard for monitoring
