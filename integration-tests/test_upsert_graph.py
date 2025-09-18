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
    assert data["validation_status"] == "VALID"


async def test_valid_invalid_valid_upsert_graph(running_server):
    class Node1(BaseNode):
        class Inputs(BaseModel):
            message: str
        
        async def execute(self):
            print(self.inputs.message) # type: ignore

    class Node2(BaseNode):
        class Inputs(BaseModel):
            message: str
        
        async def execute(self):
            print(self.inputs.message) # type: ignore

    state_machine_url = running_server.base_url
    runtime = Runtime(
        namespace="test",
        name="test",
        nodes=[
            Node1,
            Node2
        ],
        state_manager_uri=state_machine_url,
    )
    
    thread = threading.Thread(target=runtime.start, daemon=True)
    thread.start()

    await asyncio.sleep(2)

    state_manager = StateManager(
        namespace="test",
        state_manager_uri=state_machine_url
    )

    data = await state_manager.upsert_graph(
        graph_name="valid_graph",
        graph_nodes=[
            GraphNodeModel(
                node_name="Node1",
                namespace="test",
                identifier="node1",
                inputs={
                    "message": "Hello, world!",
                }
            )
        ],
        secrets={},
    )

    assert data is not None
    assert data["validation_status"] == "VALID"

    with pytest.raises(Exception) as exec_info:
        data = await state_manager.upsert_graph(
            graph_name="valid_graph",
            graph_nodes=[
                GraphNodeModel(
                    node_name="Node1",
                    namespace="test",
                    identifier="node1",
                    inputs={
                        "message": "Hello, world!",
                    }
                ),
                GraphNodeModel(
                    node_name="Node2",
                    namespace="test",
                    identifier="node2",
                    inputs={
                        "message": "Hello, world!",
                    }
                )
            ],
            secrets={},
        )
    print(exec_info.value)

    data = await state_manager.upsert_graph(
        graph_name="valid_graph",
        graph_nodes=[
            GraphNodeModel(
                node_name="Node1",
                namespace="test",
                identifier="node1",
                inputs={
                    "message": "Hello, world!",
                },
                next_nodes=["node2"]
            ),
            GraphNodeModel(
                node_name="Node2",
                namespace="test",
                identifier="node2",
                inputs={
                    "message": "Hello, world!",
                }
            )
        ],
        secrets={},
    )
    assert data is not None
    assert data["validation_status"] == "VALID"
