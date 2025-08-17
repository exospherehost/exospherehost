import asyncio
from exospherehost import StateManager, TriggerState

stateManager = StateManager(namespace="test", state_manager_uri="http://localhost:8000", key="Mathrithms@2021")

asyncio.run(stateManager.trigger("test", TriggerState(identifier="test", inputs={"test": "test"})))
