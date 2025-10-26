import logging

from spaceone.core.manager import BaseManager

from cloudforet.monitoring.model.metadata.metadata import LogMetadata
from cloudforet.monitoring.model.metadata.metadata_dynamic_field import (
    DateTimeDyField,
    EnumDyField,
    MoreField,
    SearchField,
    TextDyField,
)

_LOGGER = logging.getLogger(__name__)


class MetadataManager(BaseManager):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @staticmethod
    def get_data_source_metadata():
        metadata = LogMetadata.set_meta(
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
            search=[
                SearchField.set(name="Event Name", key="log_content.data.eventName"),
                SearchField.set(
                    name="Status",
                    key="log_content.data.response.status",
                    enums={
                        "200": {"label": "OK"},
                        "201": {"label": "Created"},
                        "202": {"label": "Accepted"},
                        "204": {"label": "No Content"},
                        "400": {"label": "Bad Request"},
                        "401": {"label": "Unauthorized"},
                        "403": {"label": "Forbidden"},
                        "404": {"label": "Not Found"},
                        "409": {"label": "Conflict"},
                        "412": {"label": "Precondition Failed"},
                        "422": {"label": "Unprocessable Entity"},
                        "429": {"label": "Too Many Requests"},
                        "500": {"label": "Internal Server Error"},
                        "502": {"label": "Bad Gateway"},
                        "503": {"label": "Service Unavailable"},
                        "504": {"label": "Gateway Timeout"},
                        "507": {"label": "Insufficient Storage"},
                    },
                ),
                SearchField.set(
                    name="User Name", key="log_content.data.identity.principalName"
                ),
                SearchField.set(
                    name="Event Time",
                    key="log_content.time",
                    data_type="datetime",
                ),
                SearchField.set(
                    name="Action",
                    key="log_content.data.request.action",
                    enums={
                        "GET": {"label": "GET"},
                        "POST": {"label": "POST"},
                        "PUT": {"label": "PUT"},
                        "PATCH": {"label": "PATCH"},
                        "DELETE": {"label": "DELETE"},
                    },
                ),
                SearchField.set(
                    name="Message",
                    key="log_content.data.message",
                ),
            ],
        )
        return metadata
