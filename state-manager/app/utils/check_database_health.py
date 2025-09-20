from ..singletons.logs_manager import LogsManager

async def check_database_health(models_to_check):
    logger = LogsManager().get_logger()
    checks_per_model = 3 
    
    logger.info("Starting database health check")

    for model in models_to_check:
        try:
            for i in range(checks_per_model):
                await model.find_one()
            logger.info(f"Health check passed for {model.__name__} ({checks_per_model} checks)")
        except Exception as e:
            error_msg = f"Database migrations needed as per the current version of state-manager. Failed to query {model.__name__}: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    logger.info("Database health check completed successfully")