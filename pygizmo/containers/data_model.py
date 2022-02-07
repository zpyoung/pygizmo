# Installed Packages
from typing import Union

from datetime import datetime

import orjson as orjson
from pydantic import BaseModel

# Redo this so the from_trusted_source simply checks if a field is a DataModel and then call from_trusted_source from it.
from pydantic.typing import AbstractSetIntStr, DictStrAny, MappingIntStrAny


class DataModel(BaseModel):
    """An enhanced Pydantic BaseModel class"""

    def dict(
        self,
        *,
        include: Union[AbstractSetIntStr, MappingIntStrAny] = None,
        exclude: Union[AbstractSetIntStr, MappingIntStrAny] = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
        json_format: bool = False,
    ) -> DictStrAny:
        if json_format:
            return self.json(
                include=include,
                exclude=exclude,
                by_alias=by_alias,
                skip_defaults=skip_defaults,
                exclude_unset=exclude_unset,
                exclude_defaults=exclude_defaults,
                exclude_none=exclude_none,
            )

    class Config:
        """Pydantic Config"""

        use_enum_values = True
        force_validate = False
        validate_assignment = True
        arbitrary_types_allowed = True
        orm_mode = True
        nones_to_default = True
        allow_population_by_field_name = True
        json_loads = orjson.loads
        json_dumps = orjson.dumps
