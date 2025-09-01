from pydantic import BaseModel, Field, field_validator

class StoreConfig(BaseModel):
    required_keys: list[str] = Field(default_factory=list, description="Required keys of the store")
    default_values: dict[str, str] = Field(default_factory=dict, description="Default values of the store")

    @field_validator("required_keys")
    def validate_required_keys(cls, v: list[str]) -> list[str]:
        errors = []
        keys = set()
        for key in v:
            if key == "" or key is None:
                errors.append("Key cannot be empty")
            elif key in keys:
                errors.append(f"Key {key} is duplicated")
            else:
                keys.add(key)
        if len(errors) > 0:
            raise ValueError("\n".join(errors))
        return v