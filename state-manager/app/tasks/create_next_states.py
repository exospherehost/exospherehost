from beanie import PydanticObjectId
from pymongo.errors import DuplicateKeyError
from beanie.operators import In, NE
from app.singletons.logs_manager import LogsManager
from app.models.db.graph_template_model import GraphTemplate
from app.models.db.state import State
from app.models.state_status_enum import StateStatusEnum
from app.models.node_template_model import NodeTemplate
from app.models.db.registered_node import RegisteredNode
from json_schema_to_pydantic import create_model
from pydantic import BaseModel
from typing import Type

logger = LogsManager().get_logger()

class Dependent(BaseModel):
    identifier: str
    field: str
    tail: str
    value: str | None = None

class DependentString(BaseModel):
    head: str
    dependents: dict[int, Dependent]
    
    def generate_string(self) -> str:
        base = self.head
        for key in sorted(self.dependents.keys()):
            dependent = self.dependents[key]
            if dependent.value is None:
                raise ValueError(f"Dependent value is not set for: {dependent}")
            base += dependent.value + dependent.tail
        return base

async def mark_success_states(state_ids: list[PydanticObjectId]):
    await State.find(
        In(State.id, state_ids)
    ).set({
        "status": StateStatusEnum.SUCCESS
    }) # type: ignore


async def check_unites_satisfied(namespace: str, graph_name: str, node_template: NodeTemplate, parents: dict[str, PydanticObjectId]) -> bool:
    if node_template.unites is None:
        return True
    
    unites_id = parents.get(node_template.unites.identifier)
    if not unites_id:
        raise ValueError(f"Unit identifier not found in parents: {node_template.unites.identifier}")
    else:
        if await State.find(
                State.namespace_name == namespace,
                State.graph_name == graph_name,
                NE(State.status, StateStatusEnum.SUCCESS),
                {
                    f"parents.{node_template.unites.identifier}": unites_id
                }
            ).count() > 0:
                return False
    return True


def get_dependents(syntax_string: str) -> DependentString:
    splits = syntax_string.split("${{")
    if len(splits) <= 1:
        return DependentString(head=syntax_string, dependents={})

    dependent_string = DependentString(head=splits[0], dependents={})
    order = 0

    for split in splits[1:]:
        if "}}" not in split:
            raise ValueError(f"Invalid syntax string placeholder {split} for: {syntax_string} '${{' not closed")
        placeholder_content, tail = split.split("}}")

        parts = [p.strip() for p in placeholder_content.split(".")]
        if len(parts) != 3 or parts[1] != "outputs":
            raise ValueError(f"Invalid syntax string placeholder {placeholder_content} for: {syntax_string}")
        
        dependent_string.dependents[order] = Dependent(identifier=parts[0], field=parts[2], tail=tail)
        order += 1

    return dependent_string

def validate_dependencies(next_state_node_template: NodeTemplate, next_state_input_model: Type[BaseModel], identifier: str, parents: dict[str, State]) -> None:
    """Validate that all dependencies exist before processing them."""
    # 1) Confirm each model field is present in next_state_node_template.inputs
    for field_name in next_state_input_model.model_fields.keys():
        if field_name not in next_state_node_template.inputs:
            raise ValueError(f"Field '{field_name}' not found in inputs for template '{next_state_node_template.identifier}'")
    
        dependency_string = get_dependents(next_state_node_template.inputs[field_name])
        
        for dependent in dependency_string.dependents.values():
            # 2) For each placeholder, verify the identifier is either current or present in parents
            if dependent.identifier != identifier and dependent.identifier not in parents:
                raise KeyError(f"Identifier '{dependent.identifier}' not found in parents for template '{next_state_node_template.identifier}'")
    
             # 3) For each dependent, verify the target output field exists on the resolved state
            if dependent.identifier == identifier:
                # This will be resolved to current_state later, skip validation here
                continue
            else:
                parent_state = parents[dependent.identifier]
                if dependent.field not in parent_state.outputs:
                    raise AttributeError(f"Output field '{dependent.field}' not found on state '{dependent.identifier}' for template '{next_state_node_template.identifier}'")


def generate_next_state(next_state_input_model: Type[BaseModel], next_state_node_template: NodeTemplate, parents: dict[str, State], current_state: State) -> State:
    next_state_input_data = {}

    for field_name, _ in next_state_input_model.model_fields.items():
        dependency_string = get_dependents(next_state_node_template.inputs[field_name])

        for key in sorted(dependency_string.dependents.keys()):
                if dependency_string.dependents[key].identifier == current_state.identifier:
                    if dependency_string.dependents[key].field not in current_state.outputs:
                        raise AttributeError(f"Output field '{dependency_string.dependents[key].field}' not found on current state '{current_state.identifier}' for template '{next_state_node_template.identifier}'")
                    dependency_string.dependents[key].value = current_state.outputs[dependency_string.dependents[key].field]
                else:
                    dependency_string.dependents[key].value = parents[dependency_string.dependents[key].identifier].outputs[dependency_string.dependents[key].field]
                    
        next_state_input_data[field_name] = dependency_string.generate_string()
    
    new_parents = {
        **current_state.parents,
        current_state.identifier: current_state.id
    }

    return State(
        node_name=next_state_node_template.node_name,
        identifier=next_state_node_template.identifier,
        namespace_name=next_state_node_template.namespace,
        graph_name=current_state.graph_name,
        status=StateStatusEnum.CREATED,
        parents=new_parents,
        inputs=next_state_input_data,
        outputs={},
        run_id=current_state.run_id,
        error=None
    )


async def create_next_states(state_ids: list[PydanticObjectId], identifier: str, namespace: str, graph_name: str, parents_ids: dict[str, PydanticObjectId]):

    try:
        if len(state_ids) == 0:
            raise ValueError("State ids is empty")
        
        graph_template = await GraphTemplate.get_valid(namespace, graph_name)
        
        current_state_node_template = graph_template.get_node_by_identifier(identifier)
        if not current_state_node_template:
            raise ValueError(f"Current state node template not found for identifier: {identifier}")
        
        next_state_identifiers = current_state_node_template.next_nodes
        if not next_state_identifiers or len(next_state_identifiers) == 0:
            await mark_success_states(state_ids)
            return
        
        cached_registered_nodes: dict[tuple[str, str], RegisteredNode] = {}
        cached_input_models: dict[tuple[str, str], Type[BaseModel]] = {}
        new_states = []

        async def get_registered_node(node_template: NodeTemplate) -> RegisteredNode:
            key = (node_template.namespace, node_template.node_name)
            if key not in cached_registered_nodes:
                registered_node = await RegisteredNode.find_one(
                    RegisteredNode.name == node_template.node_name,
                    RegisteredNode.namespace == node_template.namespace,
                )
                if not registered_node:
                    raise ValueError(f"Registered node not found for node name: {node_template.node_name} and namespace: {node_template.namespace}")
                cached_registered_nodes[key] = registered_node
            return cached_registered_nodes[key]
        
        async def get_input_model(node_template: NodeTemplate) -> Type[BaseModel]:
            key = (node_template.namespace, node_template.node_name)
            if key not in cached_input_models:
                cached_input_models[key] = create_model((await get_registered_node(node_template)).inputs_schema)
            return cached_input_models[key]

        current_states = await State.find(
            In(State.id, state_ids)
        ).to_list()

        if not parents_ids:
            parent_states = []
        else:
            parent_states = await State.find(
                In(State.id, list(parents_ids.values()))
            ).to_list()

        parents = {}
        for parent_state in parent_states:
            parents[parent_state.identifier] = parent_state

        pending_unites = []
       
        for next_state_identifier in next_state_identifiers:
            next_state_node_template = graph_template.get_node_by_identifier(next_state_identifier)
            if not next_state_node_template:
                raise ValueError(f"Next state node template not found for identifier: {next_state_identifier}")
                
            if next_state_node_template.unites is not None:
                pending_unites.append(next_state_identifier)
                continue
                
            next_state_input_model = await get_input_model(next_state_node_template)
            validate_dependencies(next_state_node_template, next_state_input_model, identifier, parents)

            for current_state in current_states:                
                new_states.append(generate_next_state(next_state_input_model, next_state_node_template, parents, current_state))
        
        if len(new_states) > 0:
            await State.insert_many(new_states)
        await mark_success_states(state_ids)

        # handle unites
        new_unit_states = []
        for pending_unites_identifier in pending_unites:
            next_state_node_template = graph_template.get_node_by_identifier(pending_unites_identifier)
            if not next_state_node_template:
                raise ValueError(f"Next state node template not found for identifier: {pending_unites_identifier}")
            
            if not await check_unites_satisfied(namespace, graph_name, next_state_node_template, parents_ids):
                continue

            next_state_input_model = await get_input_model(next_state_node_template)
            validate_dependencies(next_state_node_template, next_state_input_model, identifier, parents)

            assert next_state_node_template.unites is not None
            parent_state = parents[next_state_node_template.unites.identifier]

            new_unit_states.append(generate_next_state(next_state_input_model, next_state_node_template, parents, parent_state))
        
        try:
            if len(new_unit_states) > 0:
                await State.insert_many(new_unit_states)
        except DuplicateKeyError:
            logger.warning(f"Caught an expected duplicate key error for new unit states, likely due to a race condition: {new_unit_states}")

    except Exception as e:
        await State.find(
            In(State.id, state_ids)
        ).set({
            "status": StateStatusEnum.NEXT_CREATED_ERROR,
            "error": str(e)
        }) # type: ignore
        raise