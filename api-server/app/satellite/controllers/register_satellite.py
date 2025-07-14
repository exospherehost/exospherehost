from beanie import Link
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from fastapi.responses import JSONResponse

from ..models.register_satellite_request import RegisterSatelliteRequest
from ..models.register_satellite_response import RegisterSatelliteResponse
from ..models.satellite_database_model import Satellite

from app.auth.models.token_claims import TokenClaims
from app.project.models.project_database_model import Project
from app.singletons.logs_manager import LogsManager

logger = LogsManager().get_logger()


async def register_satellite(request: RegisterSatelliteRequest, project_id: str, claims: TokenClaims, x_exosphere_request_id: str) -> RegisterSatelliteResponse:
    
    try:
        logger.info("Registering satellite", x_exosphere_request_id=x_exosphere_request_id, project_id=project_id, name=request.name)

        satellite = Satellite(
            name=request.name,
            friendly_name=request.friendly_name,
            description=request.description,
            access_type=request.access_type,
            configs=request.configs,
            inputs=request.inputs,
            metrics=request.metrics,
            outputs=request.outputs,
            project=Link(ObjectId(project_id), Project),
            project_name=project_id,
            image_uri=request.image_uri,
            timeout=request.timeout
        )
        await satellite.insert()
        logger.info("Satellite registered", x_exosphere_request_id=x_exosphere_request_id, project_id=project_id, name=request.name)

        return RegisterSatelliteResponse(
            id=str(satellite.id),
            name=satellite.name,
            friendly_name=satellite.friendly_name,
            description=satellite.description,
            access_type=satellite.access_type,
            configs=satellite.configs,
            inputs=satellite.inputs,
            metrics=satellite.metrics,
            outputs=satellite.outputs,
            project=project_id,
            project_name=satellite.project_name,
            image_uri=satellite.image_uri,
            timeout=satellite.timeout,
            created_at=satellite.created_at,
            updated_at=satellite.updated_at
        )
    except DuplicateKeyError as e:
        logger.error("Error registering satellite", x_exosphere_request_id=x_exosphere_request_id, project_id=project_id, name=request.name, error=e)
        return JSONResponse(status_code=400, content={"message": "Satellite already exists", "success": False})
    
    except Exception as e:
        logger.error("Error registering satellite", x_exosphere_request_id=x_exosphere_request_id, project_id=project_id, name=request.name, error=e)
        raise e