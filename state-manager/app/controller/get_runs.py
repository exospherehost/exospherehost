import asyncio
from beanie.operators import In, NotIn

from ..models.run_models import RunsResponse, RunListItem, RunStatusEnum
from ..models.db.state import State
from ..models.db.run import Run
from ..models.state_status_enum import StateStatusEnum
from ..singletons.logs_manager import LogsManager

logger = LogsManager().get_logger()

async def get_runs(namespace_name: str, page: int, size: int, x_exosphere_request_id: str) -> RunsResponse:
    try:
        logger.info(f"Getting runs for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id)

        runs = await Run.find(Run.namespace_name == namespace_name).sort(-Run.created_at).skip((page - 1) * size).limit(size).to_list() # type: ignore

        if len(runs) == 0:
            return RunsResponse(
                namespace=namespace_name,
                total=0,
                page=page,
                size=size,
                runs=[]
            )
        
        look_up_table = {
            run.run_id: run for run in runs
        }
        viewed = set()


        data = await (await State.get_pymongo_collection().aggregate(
            [
                {
                    "$match": {
                        "run_id": {
                            "$in": [run.run_id for run in runs]
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$run_id",
                        "total_count": {
                            "$sum": 1
                        },
                        "success_count": {
                            "$sum": {
                                "$cond": {
                                    "if": {"$in": ["$status", [StateStatusEnum.SUCCESS, StateStatusEnum.PRUNED]]},
                                    "then": 1,
                                    "else": 0
                                }
                            }
                        },
                        "pending_count": {
                            "$sum": {
                                "$cond": {
                                    "if": {"$in": ["$status", [StateStatusEnum.CREATED, StateStatusEnum.QUEUED, StateStatusEnum.EXECUTED]]},
                                    "then": 1,
                                    "else": 0
                                }
                            }
                        },
                        "errored_count": {
                            "$sum": {
                                "$cond": {
                                    "if": {"$in": ["$status", [StateStatusEnum.ERRORED, StateStatusEnum.NEXT_CREATED_ERROR]]},
                                    "then": 1,
                                    "else": 0
                                }
                            }
                        },
                        "retried_count": {
                            "$sum": {
                                "$cond": {
                                    "if": {"$eq": ["$status", StateStatusEnum.RETRY_CREATED]},
                                    "then": 1,
                                    "else": 0
                                }
                            }
                        }
                    }
                }
            ]
        )).to_list()
        
        runs = []
        for run in data:
            success_count = run["success_count"]
            pending_count = run["pending_count"]
            errored_count = run["errored_count"]
            retried_count = run["retried_count"]

            runs.append(
                RunListItem(
                    run_id=run["_id"],
                    graph_name=look_up_table[run["_id"]].graph_name,
                    success_count=success_count,
                    pending_count=pending_count,
                    errored_count=errored_count,
                    retried_count=retried_count,
                    total_count=run["total_count"],
                    status=RunStatusEnum.PENDING if pending_count > 0 else RunStatusEnum.FAILED if errored_count > 0 else RunStatusEnum.SUCCESS,
                    created_at=look_up_table[run["_id"]].created_at
                )
            )
            viewed.add(run["_id"])
        
        if len(look_up_table) > 0:
            for run_id in look_up_table:
                if run_id not in viewed:
                    runs.append(
                        RunListItem(
                            run_id=run_id,
                            graph_name=look_up_table[run_id].graph_name,
                            success_count=0,
                            pending_count=0,
                            errored_count=0,
                            retried_count=0,
                            total_count=0,
                            status=RunStatusEnum.FAILED,
                            created_at=look_up_table[run_id].created_at
                        )
                    )

        return RunsResponse(
            namespace=namespace_name,
            total=await Run.find(Run.namespace_name == namespace_name).count(),
            page=page,
            size=size,
            runs=sorted(runs, key=lambda x: x.created_at, reverse=True)
        )
        
    except Exception as e:
        logger.error(f"Error getting runs for namespace {namespace_name}", x_exosphere_request_id=x_exosphere_request_id, error=e)
        raise