import asyncio
import time

from bson import ObjectId

from app.models.db.state import State
from app.models.db.graph_template_model import GraphTemplate
from app.models.graph_template_validation_status import GraphTemplateValidationStatus
from app.models.db.registered_node import RegisteredNode
from app.models.state_status_enum import StateStatusEnum

from json_schema_to_pydantic import create_model

async def create_next_state(state: State):
    graph_template = None

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
            raise Exception(f"Node template {state.identifier} has no next nodes")

        for identifier in next_node_identifier:
            next_node_template = graph_template.get_node_by_identifier(identifier)
            if not next_node_template:
                continue

            registered_node = await RegisteredNode.find_one(RegisteredNode.name == next_node_template.node_name, RegisteredNode.namespace == next_node_template.namespace)

            if not registered_node:
                continue

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

                        parent_id = state.parents.get(input_identifier)
                            
                        if not parent_id:
                            raise Exception(f"Parent identifier '{input_identifier}' not found in state parents.")
                            
                        dependent_state = await State.get(ObjectId(parent_id))
                        if not dependent_state:
                            raise Exception(f"Dependent state {input_identifier} not found")
                            
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
                status=StateStatusEnum.CREATED,
                inputs=next_node_input_data,
                outputs={},
                error=None,
                parents={
                    **state.parents,
                    next_node_template.identifier: ObjectId(state.id)
                }
            )
            await new_state.save()
        
        state.status = StateStatusEnum.SUCCESS
        await state.save()

    except Exception as e:
        state.status = StateStatusEnum.ERRORED
        state.error = str(e)
        await state.save()
        return
