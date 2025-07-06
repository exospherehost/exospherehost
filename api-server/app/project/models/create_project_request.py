from pydantic import BaseModel

class CreateProjectRequest(BaseModel):
    name: str
