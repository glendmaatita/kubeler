from pydantic import BaseModel
from pydantic.fields import Field
from typing import List

class Init(BaseModel):
    cmd: List[str] | None = Field(default=None, title="Initial Command")

class Variable(BaseModel):
    name: str = Field(title="Name of the variable", min_length=3, max_length=255)
    value: str | bool | int = Field(title="Value of the variable")

class Step(BaseModel):
    name: str = Field(title="Name of the steps", min_length=3, max_length=255)
    dir: str = Field(title="Directory of the step", min_length=3, max_length=255)
    files: List[str] | None = Field(default=None, title="Files to be processed in order")
    vars: List[Variable] | None = Field(default=None,title="Variables to be passed to the step")

class Group(BaseModel):
    name: str = Field(title="Initial Command")
    steps: List[Step] = Field(title="List of steps to be executed")

class Kubeler(BaseModel):
    init: Init | None = Field(default=None,title="Initial Command")
    group: Group | None = Field(default=None,title="List of groups")


