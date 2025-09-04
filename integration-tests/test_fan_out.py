import pytest
import asyncio
import threading
import os
from aiohttp import ClientSession
from pydantic import BaseModel
from exospherehost import BaseNode, Runtime, StateManager, GraphNodeModel

@pytest.mark.asyncio
async def test_upsert_graph(running_server):

    class Node1(BaseNode):
        class Inputs(BaseModel):
            message: str

        class Outputs(BaseModel):
            count: str
        
        async def execute(self):
            return [self.Outputs(count=str(i)) for i in range(10)]


    state_machine_url = running_server.base_url
    runtime = Runtime(
        namespace="test",
        name="test",
        nodes=[
            Node1
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
            node_name="Node1",
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

    trigger = await state_manager.trigger(
        graph_name="test_graph",
        inputs={},
    )

    assert trigger is not None
    assert "run_id" in trigger
    run_id = trigger["run_id"]
    
    await asyncio.sleep(30)

    run_object = None

    async with ClientSession() as session:
        async with session.get(f"{state_machine_url}/v0/namespace/test/runs/1/100", headers={"x-api-key": os.getenv("EXOSPHERE_API_KEY")}) as response: # type: ignore
            assert response.status == 200
            data = await response.json()
            
            assert "runs" in data

            for run in data["runs"]:
                if run["run_id"] == run_id:
                    run_object = run
                    break
                    
    assert run_object is not None
    assert run_object["run_id"] == run_id
    assert run_object["graph_name"] == "test_graph"
    assert run_object["success_count"] == 10
    assert run_object["pending_count"] == 0
    assert run_object["errored_count"] == 0
    assert run_object["retried_count"] == 0
    assert run_object["total_count"] == 10
    assert run_object["status"] == "SUCCESS"
