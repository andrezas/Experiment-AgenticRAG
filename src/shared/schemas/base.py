from typing import TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, from_attributes=True, validate_by_name=True, validate_by_alias=True
    )
