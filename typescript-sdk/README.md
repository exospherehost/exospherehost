# ExosphereHost TypeScript SDK

This package provides a TypeScript interface to interact with the ExosphereHost state manager. It mirrors the functionality of the Python SDK, offering utilities to manage graphs and trigger executions.

It also ships a lightweight runtime for executing `BaseNode` subclasses and utility signals for advanced control flow.

## Installation

```bash
npm install exospherehost
```

## Usage

```typescript
import { StateManager, GraphNode, TriggerState } from 'exospherehost';

const sm = new StateManager('my-namespace', {
  stateManagerUri: 'https://state-manager.example.com',
  key: 'api-key'
});

const nodes: GraphNode[] = [
  {
    node_name: 'Start',
    identifier: 'start-node',
    inputs: {},
    next_nodes: ['end-node']
  },
  {
    node_name: 'End',
    identifier: 'end-node',
    inputs: {},
    next_nodes: []
  }
];

await sm.upsertGraph('sample-graph', nodes, {});

const trigger: TriggerState = {
  identifier: 'demo',
  inputs: { foo: 'bar' }
};

await sm.trigger('sample-graph', trigger);
```

### Defining Nodes and Running the Runtime

```typescript
import { BaseNode, Runtime } from 'exospherehost';
import { z } from 'zod';

class ExampleNode extends BaseNode<typeof ExampleNode.Inputs, typeof ExampleNode.Outputs> {
  static Inputs = z.object({ message: z.string() });
  static Outputs = z.object({ result: z.string() });
  static Secrets = z.object({});

  async execute() {
    return { result: this.inputs.message.toUpperCase() };
  }
}

const runtime = new Runtime('my-namespace', 'example-runtime', [ExampleNode], {
  stateManagerUri: 'https://state-manager.example.com',
  key: 'api-key'
});

await runtime.start();
```

Nodes can also throw `PruneSignal` to drop a state or `ReQueueAfterSignal` to requeue it after a delay.

## License

MIT
