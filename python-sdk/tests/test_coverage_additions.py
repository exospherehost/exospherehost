import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from pydantic import BaseModel

from exospherehost.statemanager import StateManager
from exospherehost.runtime import Runtime
from exospherehost.node.BaseNode import BaseNode
from exospherehost.signals import PruneSignal, ReQueueAfterSignal


def _make_mock_session_with_status(status: int):
    mock_session = MagicMock()
    mock_resp = MagicMock()
    mock_resp.status = status
    mock_resp.json = AsyncMock(return_value={})

    mock_ctx = MagicMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
    mock_ctx.__aexit__ = AsyncMock(return_value=None)

    mock_session.post.return_value = mock_ctx
    mock_session.get.return_value = mock_ctx
    mock_session.put.return_value = mock_ctx

    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    return mock_session, mock_resp


@pytest.mark.asyncio
async def test_statemanager_trigger_defaults(monkeypatch):
    monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
    monkeypatch.setenv("EXOSPHERE_API_KEY", "k")

    sm = StateManager(namespace="ns")

    mock_session, _ = _make_mock_session_with_status(200)

    with patch('exospherehost.statemanager.aiohttp.ClientSession', return_value=mock_session):
        await sm.trigger("g")

    # Verify it sent empty inputs/store when omitted
    mock_session.post.assert_called_once()
    _, kwargs = mock_session.post.call_args
    assert kwargs["json"] == {"inputs": {}, "store": {}}


class _DummyNode(BaseNode):
    class Inputs(BaseModel):
        x: str = ""
    class Outputs(BaseModel):
        y: str
    class Secrets(BaseModel):
        pass
    async def execute(self):  # type: ignore
        return self.Outputs(y="ok")


@pytest.mark.asyncio
async def test_runtime_enqueue_puts_states_and_sleeps(monkeypatch):
    monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
    monkeypatch.setenv("EXOSPHERE_API_KEY", "k")

    rt = Runtime(namespace="ns", name="rt", nodes=[_DummyNode], batch_size=2, workers=1)

    with patch.object(rt, "_enqueue_call", new=AsyncMock(side_effect=[{"states": [{"state_id": "s1", "node_name": _DummyNode.__name__, "inputs": {}}]}, asyncio.CancelledError()])):
        task = asyncio.create_task(rt._enqueue())
        await asyncio.sleep(0.01)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    assert rt._state_queue.qsize() >= 1


def test_runtime_validate_nodes_not_subclass(monkeypatch):
    monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
    monkeypatch.setenv("EXOSPHERE_API_KEY", "k")

    class NotNode:
        pass

    with pytest.raises(ValueError) as e:
        Runtime(namespace="ns", name="rt", nodes=[NotNode]) # type: ignore
    msg = str(e.value)
    # Expect multiple validation messages
    assert "does not inherit" in msg
    assert "does not have an Inputs class" in msg
    assert "does not have an Outputs class" in msg
    assert "does not have an Secrets class" in msg


class _PruneNode(BaseNode):
    class Inputs(BaseModel):
        a: str
    class Outputs(BaseModel):
        b: str
    class Secrets(BaseModel):
        pass
    async def execute(self):  # type: ignore
        raise PruneSignal({"reason": "test"})


class _RequeueNode(BaseNode):
    class Inputs(BaseModel):
        a: str
    class Outputs(BaseModel):
        b: str
    class Secrets(BaseModel):
        pass
    async def execute(self):  # type: ignore
        from datetime import timedelta
        raise ReQueueAfterSignal(timedelta(seconds=1))


@pytest.mark.asyncio
async def test_worker_handles_prune_signal(monkeypatch):
    monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
    monkeypatch.setenv("EXOSPHERE_API_KEY", "k")

    rt = Runtime(namespace="ns", name="rt", nodes=[_PruneNode], workers=1)

    with patch('exospherehost.signals.PruneSignal.send', new=AsyncMock(return_value=None)) as send_mock:
        await rt._state_queue.put({"state_id": "s1", "node_name": _PruneNode.__name__, "inputs": {"a": "1"}})
        worker = asyncio.create_task(rt._worker(1))
        await asyncio.sleep(0.02)
        worker.cancel()
        try:
            await worker
        except asyncio.CancelledError:
            pass
        send_mock.assert_awaited()


@pytest.mark.asyncio
async def test_worker_handles_requeue_signal(monkeypatch):
    monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
    monkeypatch.setenv("EXOSPHERE_API_KEY", "k")

    rt = Runtime(namespace="ns", name="rt", nodes=[_RequeueNode], workers=1)

    with patch('exospherehost.signals.ReQueueAfterSignal.send', new=AsyncMock(return_value=None)) as send_mock:
        await rt._state_queue.put({"state_id": "s2", "node_name": _RequeueNode.__name__, "inputs": {"a": "1"}})
        worker = asyncio.create_task(rt._worker(2))
        await asyncio.sleep(0.02)
        worker.cancel()
        try:
            await worker
        except asyncio.CancelledError:
            pass
        send_mock.assert_awaited()


@pytest.mark.asyncio
async def test_runtime_start_creates_tasks(monkeypatch):
    monkeypatch.setenv("EXOSPHERE_STATE_MANAGER_URI", "http://sm")
    monkeypatch.setenv("EXOSPHERE_API_KEY", "k")

    rt = Runtime(namespace="ns", name="rt", nodes=[_DummyNode], workers=1)

    with patch.object(rt, "_register", new=AsyncMock(return_value=None)):
        with patch.object(rt, "_enqueue", new=AsyncMock(side_effect=asyncio.CancelledError())):
            with patch.object(rt, "_worker", new=AsyncMock(side_effect=asyncio.CancelledError())):
                t = asyncio.create_task(rt._start())
                await asyncio.sleep(0.01)
                t.cancel()
                try:
                    await t
                except asyncio.CancelledError:
                    pass 