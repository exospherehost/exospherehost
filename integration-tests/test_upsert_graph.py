import pytest
import asyncio
from pydantic import BaseModel
from exospherehost import BaseNode, Runtime, StateManager, GraphNodeModel

@pytest.mark.asyncio
async def test_upsert_graph(running_server):

    class PrintNode(BaseNode):
        class Inputs(BaseModel):
            message: str
        
        async def execute(self):
            print(self.inputs.message) # type: ignore


    state_machine_url = running_server.base_url
    runtime = Runtime(
        namespace="test",
        name="test",
        nodes=[
            PrintNode
        ],
        state_manager_uri=state_machine_url,
    )
    
    # Use asyncio task instead of thread for proper cleanup
    runtime_task = None
    
    try:
        # Start runtime as an asyncio task (non-blocking)
        runtime_task = asyncio.create_task(runtime._start())
        
        # Give runtime time to initialize
        await asyncio.sleep(2)

        state_manager = StateManager(
            namespace="test",
            state_manager_uri=state_machine_url,
        )
        data = await state_manager.upsert_graph(
            graph_name="test_graph",
            graph_nodes=[
                GraphNodeModel(
                    node_name="PrintNode",
                    namespace="test",
                    identifier="node1",
                    inputs={
                        "message": "Hello, world!",
                    },
                )
            ],
            secrets={},
        )
        assert data is not None
        
    finally:
        # Ensure proper cleanup of the runtime task
        if runtime_task and not runtime_task.done():
            runtime_task.cancel()
            try:
                await runtime_task
            except asyncio.CancelledError:
                pass  # Expected when cancelling