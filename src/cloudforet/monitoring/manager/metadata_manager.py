import logging

from spaceone.core.manager import BaseManager

from cloudforet.monitoring.model.metadata.metadata import LogMetadata
from cloudforet.monitoring.model.metadata.metadata_dynamic_field import (
    DateTimeDyField,
    EnumDyField,
    MoreField,
    TextDyField,
)

_LOGGER = logging.getLogger(__name__)


class MetadataManager(BaseManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def get_data_source_metadata():
        metadata = LogMetadata.set_fields(
            name="oci-logging-table",
            fields=[
                MoreField.data_source(
                    "Event Name",
                    "log_content.data.eventName",
                    options={
                        "layout": {
                            "name": "Event Details",
                            "type": "popup",
                            "options": {"layout": {"type": "raw"}},
                        }
                    },
                ),
                EnumDyField.data_source(
                    "Status code",
                    "log_content.data.response.status",
                    default_badge={
                        "green.500": ["200", "201", "202", "204"],
                        "coral.500": [
                            "400",
                            "401",
                            "403",
                            "404",
                            "409",
                            "412",
                            "422",
                            "429",
                        ],
                        "red.500": ["500", "502", "503", "504", "507"],
                    },
                ),
                TextDyField.data_source("Status Text", "status_text"),
                TextDyField.data_source(
                    "User Name", "log_content.data.identity.principalName"
                ),
                DateTimeDyField.data_source("Event Time", "log_content.time"),
                EnumDyField.data_source(
                    "Action",
                    "log_content.data.request.action",
                    default_badge={
                        "indigo.500": ["GET"],
                        "green.500": ["POST"],
                        "yellow.500": ["PUT", "PATCH"],
                        "red.500": ["DELETE"],
                        "gray.500": [
                            "HEAD",
                            "OPTIONS",
                            "TRACE",
                            "CONNECT",
                        ],
                    },
                ),
                TextDyField.data_source("Message", "log_content.data.message"),
            ],
        )
        return metadata
