from schematics import Model
from schematics.types import (
    BaseType,
    IntType,
    StringType,
)


class OCILogEvent(Model):
    datetime = IntType()
    log_content = BaseType()
    status_text = StringType(serialize_when_none=False)

    class Options:
        serialize_when_none = False
