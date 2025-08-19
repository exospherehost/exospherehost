from beanie import PydanticObjectId
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
        for key in range(len(self.dependents)):
            dependent = self.dependents[key]
            if not dependent.value:
                raise Exception(f"Dependent value is not set for: {dependent}")
            base += dependent.value + dependent.tail
        return base

async def mark_success_states(state_ids: list[PydanticObjectId]):
    await State.find(
        In(State.id, state_ids)
    ).set({
        "status": StateStatusEnum.SUCCESS
    }) # type: ignore


async def check_unites_satisfied(namespace: str, graph_name: str, node_template: NodeTemplate, parents: dict[str, PydanticObjectId]) -> bool:
    satisfied = True

    if node_template.unites is None or len(node_template.unites) == 0:
        return satisfied
    
    for unit in node_template.unites:
        unites_id = parents.get(unit.identifier)
        if not unites_id:
            raise ValueError(f"Unit identifier not found in parents: {unit.identifier}")
        else:
            pending_count = await State.find(
                State.identifier == unit.identifier,
                State.namespace_name == namespace,
                State.graph_name == graph_name,
                NE(State.status, StateStatusEnum.SUCCESS),
                {
                    f"parents.{unit.identifier}": unites_id
                }
            ).count()
            if pending_count == 0:
                satisfied = False
                break

    return satisfied

def get_dependents(syntax_string: str) -> DependentString:
    splits = syntax_string.split("${{")
    if len(splits) == 0:
        return DependentString(head=syntax_string, dependents={})

    dependent_string = DependentString(head=splits[0].strip(), dependents={})
    order = 0

    for split in splits[1:]:
        if not "}}" in split:
            raise Exception(f"Invalid syntax string placefolder {split} for: {syntax_string}"+"${{ not closed")
        placeholder_content, tail = split.split("}}")

        parts = [p.strip() for p in placeholder_content.split(".")]
        if len(parts) != 3 or parts[1] != "outputs":
            raise Exception(f"Invalid syntax string placefolder {placeholder_content} for: {syntax_string}")
        
        dependent_string.dependents[order] = Dependent(identifier=parts[0], field=parts[2], tail=tail.strip())
        order += 1

    return dependent_string

async def create_next_states(state_ids: list[PydanticObjectId], identifier: str, namespace: str, graph_name: str, parents_ids: dict[str, PydanticObjectId]):

    try:
        graph_template = await GraphTemplate.get_valid(namespace, graph_name)
        
        current_state_node_template = graph_template.get_node_by_identifier(identifier)
        if not current_state_node_template:
            raise ValueError(f"Current state node template not found for identifier: {identifier}")
        
        next_state_identifiers = current_state_node_template.next_nodes
        if not next_state_identifiers or len(next_state_identifiers) == 0:
            await mark_success_states(state_ids)
            return
        
        cached_states = {}
        cached_registerd_nodes = {}
        cached_input_models = {}
        current_states = []
        new_states = []

        async def get_registerd_node(node_template: NodeTemplate) -> RegisteredNode:
            if node_template.node_name not in cached_registerd_nodes:
                registerd_node = await RegisteredNode.find_one(
                    RegisteredNode.name == node_template.node_name,
                    RegisteredNode.namespace == node_template.namespace,
                )
                if not registerd_node:
                    raise ValueError(f"Registered node not found for node name: {node_template.node_name} and namespace: {node_template.namespace}")
                cached_registerd_nodes[node_template.node_name] = registerd_node
            return cached_registerd_nodes[node_template.node_name]
        
        async def get_input_model(node_template: NodeTemplate) -> Type[BaseModel]:
            if node_template.node_name not in cached_input_models:
                cached_input_models[node_template.node_name] = create_model((await get_registerd_node(node_template)).inputs_schema)
            return cached_input_models[node_template.node_name]

        current_states = await State.find(
            In(State.id, state_ids)
        ).to_list()

        parent_states = await State.find(
            In(State.id, parents_ids.values())
        ).to_list()

        parents = {}
        for parent_state in parent_states:
            parents[parent_state.identifier] = parent_state

        for current_state in current_states:
            for next_state_identifier in next_state_identifiers:
                next_state_node_template = graph_template.get_node_by_identifier(next_state_identifier)
                if not next_state_node_template:
                    raise ValueError(f"Next state node template not found for identifier: {next_state_identifier}")
                
                if not await check_unites_satisfied(namespace, graph_name, next_state_node_template, parents_ids):
                    continue
                
                next_state_input_model = await get_input_model(next_state_node_template)
                next_state_input_data = {}

                for field_name, _ in next_state_input_model.model_fields.items():
                    dependency_string = get_dependents(next_state_node_template.inputs[field_name])

                    for key in range(len(dependency_string.dependents)):
                        if dependency_string.dependents[key].identifier == identifier:
                            dependency_string.dependents[key].value = current_state.outputs[dependency_string.dependents[key].field]
                        else:
                            dependency_string.dependents[key].value = parents[dependency_string.dependents[key].identifier].outputs[dependency_string.dependents[key].field]
                    
                    next_state_input_data[field_name] = dependency_string.generate_string()
                
                new_parents = {
                    **parents_ids,
                    identifier: current_state.id
                }
                
                new_states.append(
                    State(
                        node_name=next_state_node_template.node_name,
                        identifier=next_state_node_template.identifier,
                        namespace_name=next_state_node_template.namespace,
                        graph_name=graph_name,
                        status=StateStatusEnum.CREATED,
                        parents=new_parents,
                        inputs=next_state_input_data,
                        outputs={},
                        run_id=current_state.run_id,
                        error=None
                    )
                )
        
        await State.insert_many(new_states)
        await mark_success_states(state_ids)
    
    except Exception as e:
        await State.find(
            In(State.id, state_ids)
        ).set({
            "status": StateStatusEnum.NEXT_CREATED_ERROR,
            "error": str(e)
        }) # type: ignore
        raise e