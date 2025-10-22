from schematics import Model
from schematics.types import ListType, ModelType

from cloudforet.monitoring.model.event_model import OCILogEvent


class Log(Model):
    results = ListType(ModelType(OCILogEvent), default=[])
