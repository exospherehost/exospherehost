from app.singletons.logs_manager import LogsManager
from app.models.graph_models import UpsertGraphTemplateRequest, UpsertGraphTemplateResponse
from app.models.db.graph_template_model import GraphTemplate
from app.models.graph_template_validation_status import GraphTemplateValidationStatus
from app.tasks.verify_graph import verify_graph

from fastapi import BackgroundTasks, HTTPException
from beanie.operators import Set

logger = LogsManager().get_logger()

async def upsert_graph_template(namespace_name: str, graph_name: str, body: UpsertGraphTemplateRequest, x_exosphere_request_id: str, background_tasks: BackgroundTasks) -> UpsertGraphTemplateResponse:
    try:
        graph_template = await GraphTemplate.find_one(
            GraphTemplate.name == graph_name,
            GraphTemplate.namespace == namespace_name
        )

        try:
            if graph_template:
                logger.info(
                    "Graph template already exists in namespace", graph_template=graph_template,
                    namespace_name=namespace_name,
                    x_exosphere_request_id=x_exosphere_request_id)
                
                await graph_template.set_secrets(body.secrets).update(
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
                    ).set_secrets(body.secrets)
                )
        except ValueError as e:
            logger.error("Error validating graph template", error=e, x_exosphere_request_id=x_exosphere_request_id)
            raise HTTPException(status_code=400, detail=f"Error validating graph template: {str(e)}")

        background_tasks.add_task(verify_graph, graph_template)

        return UpsertGraphTemplateResponse(
            nodes=graph_template.nodes,
            validation_status=graph_template.validation_status,
            validation_errors=graph_template.validation_errors,
            secrets={secret_name: True for secret_name in graph_template.get_secrets().keys()},
            created_at=graph_template.created_at,
            updated_at=graph_template.updated_at
        )
    
    except Exception as e:
        logger.error("Error upserting graph template", error=e, x_exosphere_request_id=x_exosphere_request_id)
        raise e