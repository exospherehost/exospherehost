import pytest
import asyncio
import threading
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
    
    thread = threading.Thread(target=runtime.start, daemon=True)
    thread.start()

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