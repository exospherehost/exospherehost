# injecting models
from ..models.db.state import State
from ..models.db.graph_template_model import GraphTemplate
from ..models.db.registered_node import RegisteredNode
from ..models.db.store import Store
from ..models.db.run import Run

async def check_database_health(logger):
    models_to_check = [State, GraphTemplate, RegisteredNode, Store, Run]

    logger.info("Starting database health check")

    for model in models_to_check:
        try:
            await model.find_one()
            logger.info(f"Health check passed for {model.__name__}")
        except Exception as e:
            error_msg = f"Database migrations needed as per the current version of state-manager. Failed to query {model.__name__}: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    logger.info("Database health check completed successfully")