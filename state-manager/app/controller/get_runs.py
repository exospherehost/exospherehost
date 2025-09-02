import asyncio
from beanie.operators import In, NotIn

from ..models.run_models import RunsResponse, RunListItem, RunStatusEnum
from ..models.db.state import State
from ..models.db.run import Run
from ..models.state_status_enum import StateStatusEnum
from ..singletons.logs_manager import LogsManager

logger = LogsManager().get_logger()

async def get_run_status(run_id: str) -> RunStatusEnum:
    if await State.find(State.run_id == run_id, State.status == StateStatusEnum.ERRORED).count() > 0:
        return RunStatusEnum.FAILED
    elif await State.find(State.run_id == run_id, NotIn(State.status, [StateStatusEnum.SUCCESS, StateStatusEnum.RETRY_CREATED, StateStatusEnum.PRUNED])).count() == 0:
        return RunStatusEnum.SUCCESS
    else:
        return RunStatusEnum.PENDING

async def get_run_info(run: Run) -> RunListItem:
    return RunListItem(
        run_id=run.run_id,
        graph_name=run.graph_name,
        success_count=await State.find(State.run_id == run.run_id, In(State.status, [StateStatusEnum.SUCCESS, StateStatusEnum.PRUNED])).count(),
        pending_count=await State.find(State.run_id == run.run_id, In(State.status, [StateStatusEnum.CREATED, StateStatusEnum.QUEUED, StateStatusEnum.EXECUTED])).count(),
        errored_count=await State.find(State.run_id == run.run_id, In(State.status, [StateStatusEnum.ERRORED, StateStatusEnum.NEXT_CREATED_ERROR])).count(),
        retried_count=await State.find(State.run_id == run.run_id, State.status == StateStatusEnum.RETRY_CREATED).count(),
        total_count=await State.find(State.run_id == run.run_id,).count(),
        status=await get_run_status(run.run_id),
        created_at=run.created_at
    )


async def get_runs(namespace_name: str, page: int, size: int, x_exosphere_request_id: str) -> RunsResponse:
    try:
        logger.info(f"Getting runs for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)

        runs = await Run.find(Run.namespace_name == namespace_name).sort(-Run.created_at).skip((page - 1) * size).limit(size).to_list() # type: ignore
        
        return RunsResponse(
            namespace=namespace_name,
            total=await Run.find(Run.namespace_name == namespace_name).count(),
            page=page,
            size=size,
            runs=await asyncio.gather(*[get_run_info(run) for run in runs])
        )
        
    except Exception as e:
        logger.error(f"Error getting runs for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id, error=e)
        raise