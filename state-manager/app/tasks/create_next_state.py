import asyncio
import time

from app.models.db.state import State
from app.models.db.graph_template_model import GraphTemplate
from app.models.graph_template_validation_status import GraphTemplateValidationStatus
from app.models.db.registered_node import RegisteredNode
from app.models.state_status_enum import StateStatusEnum
from beanie.operators import NE
from app.singletons.logs_manager import LogsManager

from json_schema_to_pydantic import create_model

logger = LogsManager().get_logger()

async def create_next_state(state: State):
    graph_template = None

    if state is None or state.id is None:
        raise ValueError("State is not valid")
    try:
        start_time = time.time()
        timeout_seconds = 300  # 5 minutes
        
        while True:
            graph_template = await GraphTemplate.find_one(GraphTemplate.name == state.graph_name, GraphTemplate.namespace == state.namespace_name)
            if not graph_template:
                raise Exception(f"Graph template {state.graph_name} not found")
            if graph_template.validation_status == GraphTemplateValidationStatus.VALID:
                break
            
            # Check if we've exceeded the timeout
            if time.time() - start_time > timeout_seconds:
                raise Exception(f"Timeout waiting for graph template {state.graph_name} to become valid after {timeout_seconds} seconds")
            
            await asyncio.sleep(1)

        node_template = graph_template.get_node_by_identifier(state.identifier)
        if not node_template:
            raise Exception(f"Node template {state.identifier} not found")
        
        next_node_identifier = node_template.next_nodes
        if not next_node_identifier:
            state.status = StateStatusEnum.SUCCESS
            await state.save()
            return
        
        cache_states = {}   

        parents = state.parents | {state.identifier: state.id}

        for identifier in next_node_identifier:
            next_node_template = graph_template.get_node_by_identifier(identifier)
            if not next_node_template:
                continue

            depends_satisfied = True
            if next_node_template.unites is not None and len(next_node_template.unites) > 0:
                pending_count = 0
                for depend in next_node_template.unites:
                    if depend.identifier == state.identifier:
                        continue
                    else:
                        root_parent = state.parents.get(depend.identifier)
                        if root_parent is None:
                            raise Exception(f"Root parent of {depend.identifier} not found")
                        
                        pending_count = await State.find(
                            State.identifier == depend.identifier,
                            State.namespace_name == state.namespace_name,
                            State.graph_name == state.graph_name,
                            NE(State.status, StateStatusEnum.SUCCESS),
                            {f"parents.{depend.identifier}": parents[depend.identifier]}
                        ).count()
                    if pending_count > 0:
                        logger.info(f"Node {next_node_template.identifier} depends on {depend.identifier} but it is not satisfied")
                        depends_satisfied = False
                        break
            
            if not depends_satisfied:
                continue

            registered_node = await RegisteredNode.find_one(RegisteredNode.name == next_node_template.node_name, RegisteredNode.namespace == next_node_template.namespace)

            if not registered_node:
                raise Exception(f"Registered node {next_node_template.node_name} not found")

            next_node_input_model = create_model(registered_node.inputs_schema)
            next_node_input_data = {}

            for field_name, _ in next_node_input_model.model_fields.items():
                temporary_input = next_node_template.inputs[field_name]
                splits = temporary_input.split("${{")
                    
                if len(splits) == 0:
                    next_node_input_data[field_name] = temporary_input
                    continue

                constructed_string = ""
                for split in splits:
                    if "}}" in split:
                        placeholder_content = split.split("}}")[0]
                        parts = [p.strip() for p in placeholder_content.split('.')]
                            
                        if len(parts) != 3 or parts[1] != 'outputs':
                            raise Exception(f"Invalid input placeholder format: '{placeholder_content}' for field {field_name}")
                            
                        input_identifier = parts[0]
                        input_field = parts[2]                        

                        parent_id = parents.get(input_identifier)
                            
                        if not parent_id:
                            raise Exception(f"Parent identifier '{input_identifier}' not found in state parents.")

                        if parent_id not in cache_states:
                            dependent_state = await State.get(parent_id)
                            if not dependent_state:
                                raise Exception(f"Dependent state {input_identifier} not found")
                            cache_states[parent_id] = dependent_state
                        else:
                            dependent_state = cache_states[parent_id]
                            
                        if input_field not in dependent_state.outputs:
                            raise Exception(f"Input field {input_field} not found in dependent state {input_identifier}")
                            
                        constructed_string += dependent_state.outputs[input_field] + split.split("}}")[1]

                    else:
                        constructed_string += split
                    
                next_node_input_data[field_name] = constructed_string

            new_state = State(
                node_name=next_node_template.node_name,
                namespace_name=next_node_template.namespace,
                identifier=next_node_template.identifier,
                graph_name=state.graph_name,
                run_id=state.run_id,
                status=StateStatusEnum.CREATED,
                inputs=next_node_input_data,
                outputs={},
                error=None,
                parents=parents
            )

            await new_state.save()
        
        state.status = StateStatusEnum.SUCCESS
        await state.save()

    except Exception as e:
        state.status = StateStatusEnum.ERRORED
        state.error = str(e)
        await state.save()
        return
