import asyncio
import croniter

from datetime import datetime, timedelta
from beanie.operators import In
from json_schema_to_pydantic import create_model

from app.models.db.graph_template_model import GraphTemplate
from app.models.graph_template_validation_status import GraphTemplateValidationStatus
from app.models.db.registered_node import RegisteredNode
from app.singletons.logs_manager import LogsManager
from app.models.trigger_models import Trigger, CronTrigger, TriggerStatusEnum, TriggerTypeEnum
from app.models.db.trigger import DatabaseTriggers
from app.config.settings import get_settings

logger = LogsManager().get_logger()

async def verify_node_exists(graph_template: GraphTemplate, registered_nodes: list[RegisteredNode]) -> list[str]:
    errors = []
    template_nodes_set = set([(node.node_name, node.namespace) for node in graph_template.nodes])
    registered_nodes_set = set([(node.name, node.namespace) for node in registered_nodes])

    nodes_not_found = template_nodes_set - registered_nodes_set
    
    for node in nodes_not_found:
        errors.append(f"Node {node[0]} in namespace {node[1]} does not exist.")
    return errors
   
async def verify_secrets(graph_template: GraphTemplate, registered_nodes: list[RegisteredNode]) -> list[str]:
    errors = []
    required_secrets_set = set()

    for node in registered_nodes:
        if node.secrets is None:
            continue
        for secret in node.secrets:
            required_secrets_set.add(secret)
    
    present_secrets_set = set()
    for secret_name in graph_template.secrets.keys():
        present_secrets_set.add(secret_name)
    
    missing_secrets_set = required_secrets_set - present_secrets_set
    
    for secret_name in missing_secrets_set:
        errors.append(f"Secret {secret_name} is required but not present in the graph template")
    
    return errors

async def verify_inputs(graph_template: GraphTemplate, registered_nodes: list[RegisteredNode]) -> list[str]:
    errors = []
    look_up_table = {
        (rn.name, rn.namespace): rn
        for rn in registered_nodes
    }

    for node in graph_template.nodes:
        if node.inputs is None:
            continue
        
        registered_node = look_up_table.get((node.node_name, node.namespace))
        if registered_node is None:
            errors.append(f"Node {node.node_name} in namespace {node.namespace} does not exist")
            continue
        
        registered_node_input_model  = create_model(registered_node.inputs_schema)

        for input_name, input_info in registered_node_input_model.model_fields.items():
            if input_info.annotation is not str:
                errors.append(f"Input {input_name} in node {node.node_name} in namespace {node.namespace} is not a string")
                continue
            
            if input_name not in node.inputs.keys():
                errors.append(f"Input {input_name} in node {node.node_name} in namespace {node.namespace} is not present in the graph template")
                continue

        dependent_strings = node.get_dependent_strings()
        for dependent_string in dependent_strings:
            identifier_field_pairs = dependent_string.get_identifier_field()
            for identifier, field in identifier_field_pairs:
                
                if identifier == "store":
                    continue
                
                temp_node = graph_template.get_node_by_identifier(identifier)
                if temp_node is None:
                    errors.append(f"Node {identifier} does not exist in the graph template")
                    continue

                registered_node = look_up_table.get((temp_node.node_name, temp_node.namespace))
                if registered_node is None:
                    errors.append(f"Node {temp_node.node_name} in namespace {temp_node.namespace} does not exist")
                    continue
                
                output_model = create_model(registered_node.outputs_schema)
                if field not in output_model.model_fields.keys():
                    errors.append(f"Field {field} in node {temp_node.node_name} in namespace {temp_node.namespace} does not exist")
                    continue
                
                if output_model.model_fields[field].annotation is not str:
                    errors.append(f"Field {field} in node {temp_node.node_name} in namespace {temp_node.namespace} is not a string")
                
    return errors

async def cancel_crons(graph_template: GraphTemplate, old_triggers: list[Trigger]):
    old_crons = set([CronTrigger(**trigger.value) for trigger in old_triggers if trigger.type == TriggerTypeEnum.CRON])
    new_crons = set([CronTrigger(**trigger.value) for trigger in graph_template.triggers if trigger.type == TriggerTypeEnum.CRON])

    removed = old_crons - new_crons

    await DatabaseTriggers.find(
        DatabaseTriggers.graph_name == graph_template.name,
        DatabaseTriggers.trigger_status == TriggerStatusEnum.PENDING,
        DatabaseTriggers.type == TriggerTypeEnum.CRON,
        In(DatabaseTriggers.expression, [cron.expression for cron in removed])
    ).update(
        {
            "$set": {
                "trigger_status": TriggerStatusEnum.CANCELLED
            }
        }
    ) # type: ignore

async def create_crons(graph_template: GraphTemplate, old_triggers: list[Trigger]):
    old_crons = set([CronTrigger(**trigger.value) for trigger in old_triggers if trigger.type == TriggerTypeEnum.CRON])
    new_crons = set([CronTrigger(**trigger.value) for trigger in graph_template.triggers if trigger.type == TriggerTypeEnum.CRON])

    crons_to_create = new_crons - old_crons

    current_time = datetime.now()
    
    new_db_triggers = []
    for cron in crons_to_create:
        iter = croniter.croniter(cron.expression, current_time)

        next_trigger_time = iter.get_next(datetime)
            
        new_db_triggers.append(
            DatabaseTriggers(
                type=TriggerTypeEnum.CRON,
                expression=cron.expression,
                graph_name=graph_template.name,
                namespace=graph_template.namespace,
                trigger_status=TriggerStatusEnum.PENDING,
                trigger_time=next_trigger_time
            )
        )

    if len(new_db_triggers) > 0:
        await DatabaseTriggers.insert_many(new_db_triggers)

async def verify_graph(graph_template: GraphTemplate, old_triggers: list[Trigger]):
    try:
        errors = []
        registered_nodes = await RegisteredNode.list_nodes_by_templates(graph_template.nodes)

        basic_verify_tasks = [
            verify_node_exists(graph_template, registered_nodes),
            verify_secrets(graph_template, registered_nodes),
            verify_inputs(graph_template, registered_nodes)
        ]
        resultant_errors = await asyncio.gather(*basic_verify_tasks)

        for error in resultant_errors:
            errors.extend(error)
        
        if len(errors) > 0:
            graph_template.validation_status = GraphTemplateValidationStatus.INVALID
            graph_template.validation_errors = errors
            await graph_template.save()
            return
        
        graph_template.validation_status = GraphTemplateValidationStatus.VALID
        graph_template.validation_errors = []

        await asyncio.gather(*[cancel_crons(graph_template, old_triggers), create_crons(graph_template, old_triggers)])

        await graph_template.save()
        
    except Exception as e:
        logger.error(f"Exception during graph validation for graph template {graph_template.id}: {str(e)}", exc_info=True)
        graph_template.validation_status = GraphTemplateValidationStatus.INVALID
        graph_template.validation_errors = [f"Validation failed due to unexpected error: {str(e)}"]
        await graph_template.save()
        raise