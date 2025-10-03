import time
from beanie.operators import Ne
from app.models.db.state import State
from app.models.state_status_enum import StateStatusEnum
from app.singletons.logs_manager import LogsManager
from app.config.settings import get_settings

logger = LogsManager().get_logger()


async def check_node_timeout():
    try:
        settings = get_settings()
        current_time_ms = int(time.time() * 1000)

        logger.info(f"Checking for timed out nodes at {current_time_ms}")

        # Find all QUEUED states with queued_at set
        queued_states = await State.find(
            State.status == StateStatusEnum.QUEUED,
            Ne(State.queued_at, None)
        ).to_list()

        states_to_timeout = []
        
        for state in queued_states:
            # Use state-specific timeout if available, otherwise fall back to global
            timeout_minutes = state.timeout_minutes if state.timeout_minutes else settings.node_timeout_minutes
            timeout_ms = timeout_minutes * 60 * 1000
            timeout_threshold = current_time_ms - timeout_ms
            
            if state.queued_at <= timeout_threshold:
                state.status = StateStatusEnum.TIMEDOUT
                state.error = f"Node execution timed out after {timeout_minutes} minutes"
                states_to_timeout.append(state)

        if states_to_timeout:
            # Update all timed out states in bulk
            await State.save_all(states_to_timeout)
            logger.info(f"Marked {len(states_to_timeout)} states as TIMEDOUT")
        
    except Exception:
        logger.error("Error checking node timeout", exc_info=True)
