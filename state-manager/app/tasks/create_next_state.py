import asyncio

from bson import ObjectId

from app.models.db.state import State
from app.models.db.graph_template_model import GraphTemplate
from app.models.graph_template_validation_status import GraphTemplateValidationStatus
from app.models.db.registered_node import RegisteredNode
from app.models.state_status_enum import StateStatusEnum

from json_schema_to_pydantic import create_model

async def create_next_state(state: State):
    graph_template = None

    while True:
        graph_template = await GraphTemplate.find_one(GraphTemplate.name == state.graph_name, GraphTemplate.namespace == state.namespace_name)
        if not graph_template:
            return
        if graph_template.validation_status == GraphTemplateValidationStatus.VALID:
            break
        await asyncio.sleep(1)

    node_template = graph_template.get_node_by_identifier(state.identifier)
    if not node_template:
        return
    
    next_node_identifier = node_template.next_nodes
    if not next_node_identifier:
        return

    for identifier in next_node_identifier:
        next_node_template = graph_template.get_node_by_identifier(identifier)
        if not next_node_template:
            continue

        registered_node = await RegisteredNode.find_one(RegisteredNode.name == next_node_template.node_name, RegisteredNode.namespace == next_node_template.namespace)

        if not registered_node:
            continue

        try: 
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
                        input_identifier = split.split("}}")[0].split(".")[0].strip()
                        input_field = split.split("}}")[0].split(".")[2].strip()

                        dependent_state = await State.get(ObjectId(state.parents[input_identifier]))
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

        except Exception as e:
            state.status = StateStatusEnum.ERRORED
            state.error = str(e)
            await state.save()
            return
    
    state.status = StateStatusEnum.SUCCESS
