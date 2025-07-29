from .base import BaseDatabaseModel
from pydantic import Field
from beanie import Indexed


class Namespace(BaseDatabaseModel):

    name: Indexed(str, unique=True) = Field(..., description="Name of the namespace")