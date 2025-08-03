from app.singletons.logs_manager import LogsManager
from app.models.graph_models import UpsertGraphTemplateRequest, UpsertGraphTemplateResponse
from app.models.db.graph_template_model import GraphTemplate
from app.models.graph_template_validation_status import GraphTemplateValidationStatus
from beanie.operators import Set

logger = LogsManager().get_logger()

async def upsert_graph_template(namespace_name: str, graph_name: str, body: UpsertGraphTemplateRequest, x_exosphere_request_id: str) -> UpsertGraphTemplateResponse:
    try:
        graph_template = await GraphTemplate.find_one(
            GraphTemplate.name == graph_name,
            GraphTemplate.namespace == namespace_name
        )
        if graph_template:
            logger.info(
                "Graph template already exists in namespace", graph_template=graph_template,
                namespace_name=namespace_name,
                x_exosphere_request_id=x_exosphere_request_id)
            
            await graph_template.update(
                Set({
                    GraphTemplate.nodes: body.nodes, # type: ignore
                    GraphTemplate.validation_status: GraphTemplateValidationStatus.PENDING, # type: ignore
                    GraphTemplate.validation_errors: [] # type: ignore
                })
            )
            
        else:
            logger.info(
                "Graph template does not exist in namespace",
                namespace_name=namespace_name,
                graph_name=graph_name,
                x_exosphere_request_id=x_exosphere_request_id)
            
            graph_template = await GraphTemplate.insert(
                GraphTemplate(
                    name=graph_name,
                    namespace=namespace_name,
                    nodes=body.nodes,
                    validation_status=GraphTemplateValidationStatus.PENDING,
                    validation_errors=[]
                )
            )

        return UpsertGraphTemplateResponse(
            name=graph_template.name,
            namespace=graph_template.namespace,
            nodes=graph_template.nodes,
            validation_status=graph_template.validation_status,
            validation_errors=graph_template.validation_errors,
            created_at=graph_template.created_at,
            updated_at=graph_template.updated_at
        )
    
    except Exception as e:
        logger.error("Error upserting graph template", error=e, x_exosphere_request_id=x_exosphere_request_id)
        raise e