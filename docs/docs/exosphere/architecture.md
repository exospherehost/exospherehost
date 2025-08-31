# Exosphere Architecture

This document provides a comprehensive overview of Exosphere's top-level architecture, focusing on state execution, fanout mechanisms, and the unites keyword for stage unification.

## Overview

Exosphere is built around a **state-based execution model** where workflows are composed of discrete states that can be executed independently. The architecture consists of several key components:

- **State Manager**: Central orchestrator that manages state lifecycle and transitions
- **Runtimes**: Distributed execution engines that process individual states
- **Graph Templates**: Declarative workflow definitions
- **States**: Individual execution units with inputs, outputs, and metadata

## State Execution Model

### State Lifecycle

Each state in Exosphere follows a well-defined lifecycle:

```
CREATED → QUEUED → EXECUTED/ERRORED → SUCCESS
```

1. **CREATED**: State is initialized with inputs and dependencies
2. **QUEUED**: State is ready for execution and waiting for a runtime
3. **EXECUTED**: State finished (with outputs) — terminal for that state
4. **ERRORED**: State failed during executionState and all its dependencies are complete
5. **SUCCESS**: Workflow/branch-level success once all dependent states complete


## Fanout Mechanism

### Single vs Multiple Outputs

Exosphere supports two execution patterns:

1. **Single Output**: A state produces one output and continues to the next stage
2. **Multiple Outputs (Fanout)**: A state produces multiple outputs, creating parallel execution paths


### Fanout Example

Consider a data processing workflow:

```python hl_lines="9-11"
class DataSplitterNode(BaseNode):
    async def execute(self) -> list[Outputs]:
        data = json.loads(self.inputs.data)
        chunk_size = 100
        
        outputs = []
        for i in range(0, len(data), chunk_size):
            chunk = data[i:i + chunk_size]
            outputs.append(self.Outputs(
                chunk=json.dumps(chunk)
            ))
        
        return outputs  # This creates fanout on each output
```

When this node executes:
1. **Original state** gets the first chunk as output
2. **Additional states** are created for each remaining chunk
3. **All states** are marked as EXECUTED
4. **Next stages** are created for each state independently

**This enables parallel processing of data chunks across multiple runtime instances.**

## Unites Keyword

### Purpose

The `unites` keyword is a powerful mechanism for **synchronizing parallel execution paths**. It allows a node to wait for multiple parallel states to complete before executing.

### Unites Logic

When a node has a `unites` configuration:

1. **Execution is deferred** until all states with the specified identifier are complete
2. **State fingerprinting** ensures only one unites state is created per unique combination
3. **Dependency validation** ensures the unites node depends on the specified identifier

### Unites Strategy (Beta)

The `unites` keyword supports different strategies to control when the uniting node should execute. This feature is currently in **beta**.

#### Available Strategies

- **`ALL_SUCCESS`** (default): The uniting node executes only when all states with the specified identifier have reached `SUCCESS` status. If any state fails or is still processing, the uniting node will wait.

- **`ALL_DONE`**: The uniting node executes when all states with the specified identifier have completed their execution (reached `SUCCESS`, `ERRORED`, or any terminal status). This strategy allows the uniting node to proceed even if some states have failed.

#### Strategy Configuration

You can specify the strategy in your unites configuration:

```json hl_lines="22-26"
{
  "nodes": [
    {
      "node_name": "DataSplitterNode",
      "identifier": "data_splitter",
      "next_nodes": ["processor_1"]
    },
    {
      "node_name": "DataProcessorNode",
      "identifier": "processor_1",
      "inputs":{
        "x":"${{data_splitter.outputs.data_chunk}}"
      },
      "next_nodes": ["result_merger"]
    },    
    {
      "node_name": "ResultMergerNode",
      "identifier": "result_merger",
      "inputs":{
        "x_processed":"${{processor_1.outputs.processed_data}}"
      },
      "unites": {
        "identifier": "data_splitter",
        "strategy": "ALL_SUCCESS"
      },
      "next_nodes": []
    }
  ]
}
```

#### Use Cases

- **`ALL_SUCCESS`**: Use when you need all parallel processes to complete successfully before proceeding. Ideal for data processing workflows where partial failures are not acceptable.

- **`ALL_DONE`**: Use when you want to proceed with partial results or when you have error handling logic in the uniting node. Useful for scenarios where you want to aggregate results from successful processes while handling failures separately.

### Unites Example

```json hl_lines="22-24"
{
  "nodes": [
    {
      "node_name": "DataSplitterNode",
      "identifier": "data_splitter",
      "next_nodes": ["processor_1"]
    },
    {
      "node_name": "DataProcessorNode",
      "identifier": "processor_1",
      "inputs":{
        "x":"${{data_splitter.outputs.data_chunk}}"
      }
      "next_nodes": ["result_merger"]
    },    
    {
      "node_name": "ResultMergerNode",
      "identifier": "result_merger",
      "inputs":{
        "x_processed":"${{processor_1.outputs.processed_data}}"
      }
      "unites": {
        "identifier": "data_splitter"
      },
      "next_nodes": []
    }
  ]
}
```

In this example:
1. `data_splitter` creates fanout with 3 outputs
2. `processor_1` executes in parallel for all three data chunks
3. `result_merger` waits for all processors to complete (unites with `data_splitter`)
4. Only one `result_merger` state is created due to fingerprinting

## Architecture Benefits

### Scalability

- **Horizontal scaling**: Add more runtime instances to handle increased load
- **Parallel processing**: Fanout enables concurrent execution
- **Load distribution**: State manager distributes work across available runtimes

### Fault Tolerance

- **State persistence**: All states are stored in the database
- **Retry mechanisms**: Failed states can be retried automatically
- **Recovery**: Workflows can resume from where they left off

### Flexibility

- **Dynamic fanout**: Nodes can produce variable numbers of outputs
- **Synchronization**: Unites keyword provides precise control over parallel execution
- **Dependency management**: Automatic resolution of complex dependencies

### Observability

- **State tracking**: Complete visibility into execution progress
- **Error handling**: Detailed error information and retry logic
- **Performance monitoring**: Track execution times and resource usage


Exosphere's architecture provides a robust foundation for building distributed, scalable workflows. The combination of state-based execution, fanout mechanisms, and the unites keyword enables complex parallel processing patterns while maintaining simplicity and reliability.