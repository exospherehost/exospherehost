from pydantic import BaseModel, Field, field_validator

class StoreConfig(BaseModel):
    required_keys: list[str] = Field(default_factory=list, description="Required keys of the store")
    default_values: dict[str, str] = Field(default_factory=dict, description="Default values of the store")

    @field_validator("required_keys")
    def validate_required_keys(cls, v: list[str]) -> list[str]:
        errors = []
        keys = set()
        trimmed_keys = []
        
        for key in v:
            trimmed_key = key.strip() if key is not None else ""
            
            if trimmed_key == "":
                errors.append("Key cannot be empty or contain only whitespace")
                continue
                
            if '.' in trimmed_key:
                errors.append(f"Key '{trimmed_key}' cannot contain '.' character")
                continue
                
            if trimmed_key in keys:
                errors.append(f"Key '{trimmed_key}' is duplicated")
                continue
                
            keys.add(trimmed_key)
            trimmed_keys.append(trimmed_key)
        
        if len(errors) > 0:
            raise ValueError("\n".join(errors))
        return trimmed_keys

    @field_validator("default_values")
    def validate_default_values(cls, v: dict[str, str]) -> dict[str, str]:
        errors = []
        keys = set()
        normalized_dict = {}
        
        for key, value in v.items():
            trimmed_key = key.strip() if key is not None else ""
            
            if trimmed_key == "":
                errors.append("Key cannot be empty or contain only whitespace")
                continue
                
            if '.' in trimmed_key:
                errors.append(f"Key '{trimmed_key}' cannot contain '.' character")
                continue
                
            if trimmed_key in keys:
                errors.append(f"Key '{trimmed_key}' is duplicated")
                continue
                
            keys.add(trimmed_key)
            normalized_dict[trimmed_key] = str(value)
        
        if len(errors) > 0:
            raise ValueError("\n".join(errors))
        return normalized_dict