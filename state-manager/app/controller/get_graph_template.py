from app.singletons.logs_manager import LogsManager
from app.models.graph_models import UpsertGraphTemplateResponse
from app.models.db.graph_template_model import GraphTemplate

logger = LogsManager().get_logger()


async def get_graph_template(namespace_name: str, graph_name: str, x_exosphere_request_id: str) -> UpsertGraphTemplateResponse:
    try:
        graph_template = await GraphTemplate.find_one(
            GraphTemplate.name == graph_name,
            GraphTemplate.namespace == namespace_name
        )

        if not graph_template:
            logger.error(
                "Graph template not found",
                graph_name=graph_name,
                namespace_name=namespace_name,
                x_exosphere_request_id=x_exosphere_request_id,
            )
            raise ValueError(f"Graph template {graph_name} not found in namespace {namespace_name}")

        logger.info(
            "Graph template retrieved",
            graph_name=graph_name,
            namespace_name=namespace_name,
            x_exosphere_request_id=x_exosphere_request_id,
        )

        return UpsertGraphTemplateResponse(
            nodes=graph_template.nodes,
            validation_status=graph_template.validation_status,
            validation_errors=graph_template.validation_errors,
            secrets={secret_name: True for secret_name in graph_template.get_secrets().keys()},
            created_at=graph_template.created_at,
            updated_at=graph_template.updated_at,
        )
    except Exception as e:
        logger.error(
            "Error retrieving graph template",
            error=e,
            graph_name=graph_name,
            namespace_name=namespace_name,
            x_exosphere_request_id=x_exosphere_request_id,
        )
        raise e 