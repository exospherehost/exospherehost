from beanie import Document
from pydantic import Field
from pymongo import IndexModel

class Store(Document):
    run_id: str = Field(..., description="Run ID of the corresponding graph execution")
    namespace: str = Field(..., description="Namespace of the graph")
    graph_name: str = Field(..., description="Name of the graph")
    key: str = Field(..., description="Key of the store")
    value: str = Field(..., description="Value of the store")

    class Settings:
        indexes = [
            IndexModel(
                [
                    ("run_id", 1),
                    ("namespace", 1),
                    ("graph_name", 1),
                    ("key", 1),
                ],
                unique=True,
                name="uniq_run_id_namespace_graph_name_key",
            )
        ]

    @staticmethod   
    async def get_value(run_id: str, namespace: str, graph_name: str, key: str) -> str | None:
        store = await Store.find_one(
            Store.run_id == run_id,
            Store.namespace == namespace,
            Store.graph_name == graph_name,
            Store.key == key,
        )
        if store is None:
            return None
        return store.value
