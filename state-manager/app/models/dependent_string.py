from pydantic import BaseModel, PrivateAttr

class Dependent(BaseModel):
    identifier: str
    field: str
    tail: str
    value: str | None = None

class DependentString(BaseModel):
    head: str
    dependents: dict[int, Dependent]
    _mapping_key_to_dependent: dict[tuple[str, str], list[Dependent]] = PrivateAttr(default_factory=dict)
    
    def generate_string(self) -> str:
        base = self.head
        for key in sorted(self.dependents.keys()):
            dependent = self.dependents[key]
            if dependent.value is None:
                raise ValueError(f"Dependent value is not set for: {dependent}")
            base += dependent.value + dependent.tail
        return base
    
    @staticmethod
    def create_dependent_string(syntax_string: str) -> "DependentString":
        splits = syntax_string.split("${{")
        if len(splits) <= 1:
            return DependentString(head=syntax_string, dependents={})

        dependent_string = DependentString(head=splits[0], dependents={})

        for order, split in enumerate(splits[1:]):
            if "}}" not in split:
                raise ValueError(f"Invalid syntax string placeholder {split} for: {syntax_string} '${{' not closed")
            placeholder_content, tail = split.split("}}", 1)

            parts = [p.strip() for p in placeholder_content.split(".")]

            if len(parts) == 3 and parts[1] == "outputs":
                dependent_string.dependents[order] = Dependent(identifier=parts[0], field=parts[2], tail=tail)
            elif len(parts) == 2 and parts[0] == "store":
                dependent_string.dependents[order] = Dependent(identifier=parts[0], field=parts[1], tail=tail)
            else:
                raise ValueError(f"Invalid syntax string placeholder {placeholder_content} for: {syntax_string}")
            
        return dependent_string

    def _build_mapping_key_to_dependent(self):
        if self._mapping_key_to_dependent != {}:
            return
        
        for dependent in self.dependents.values():
            mapping_key = (dependent.identifier, dependent.field)
            if mapping_key not in self._mapping_key_to_dependent:
                self._mapping_key_to_dependent[mapping_key] = []
            self._mapping_key_to_dependent[mapping_key].append(dependent)

    def set_value(self, identifier: str, field: str, value: str):
        self._build_mapping_key_to_dependent()
        mapping_key = (identifier, field)
        for dependent in self._mapping_key_to_dependent[mapping_key]:
            dependent.value = value

    def get_identifier_field(self) -> list[tuple[str, str]]:
        self._build_mapping_key_to_dependent()
        return list(self._mapping_key_to_dependent.keys())