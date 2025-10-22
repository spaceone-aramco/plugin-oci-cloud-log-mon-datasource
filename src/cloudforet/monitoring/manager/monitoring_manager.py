import logging
from typing import Any, Dict

from spaceone.core.manager import BaseManager

from cloudforet.monitoring.connector.oci_logging_connector import OCILoggingConnector
from cloudforet.monitoring.model.event_model import OCILogEvent
from cloudforet.monitoring.model.log_model import Log

_LOGGER = logging.getLogger(__name__)


class MonitoringManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def list_logs(self, params):
        query = params.get("query", {})
        if not query or not query.get("filters"):
            return Log({"results": []})

        oci_logging_conn: OCILoggingConnector = self.locator.get_connector(
            "OCILoggingConnector", **params
        )

        for logs in oci_logging_conn.search_logs(params):
            event_vos = []

            for log in logs:
                try:
                    converted_log = self._convert_log_entry(log)
                    if not converted_log or not converted_log.get("log_content"):
                        continue

                    event_vo = OCILogEvent(converted_log, strict=False)
                    event_vos.append(event_vo)

                except Exception as e:
                    _LOGGER.warning(f"Failed to process log entry: {str(e)}")
                    continue

            if not event_vos:
                continue

            yield Log({"results": event_vos})

        _LOGGER.debug("list_logs method ended!")

    def _convert_log_entry(self, raw_log: Any) -> Dict[str, Any]:
        try:
            if not raw_log:
                return None

            log_data = raw_log.data if hasattr(raw_log, "data") else raw_log
            datetime_value = log_data.get("datetime")
            log_content = log_data.get("logContent", {}) or {}

            status_text = self._convert_status_code(log_content)

            converted_entry = {
                "datetime": datetime_value,
                "log_content": log_content,
                "status_text": status_text,
            }

            return converted_entry

        except Exception as e:
            _LOGGER.warning(f"Failed to convert log entry: {str(e)}")
            return None

    def _convert_status_code(self, log_content: Dict[str, Any]) -> str:
        """HTTP status code to text conversion"""
        try:
            status = log_content.get("data", {}).get("response", {}).get("status")
            if not status:
                return None

            status_map = {
                "200": "OK",
                "201": "Created",
                "202": "Accepted",
                "204": "No Content",
                "400": "Bad Request",
                "401": "Unauthorized",
                "403": "Forbidden",
                "404": "Not Found",
                "409": "Conflict",
                "412": "Precondition Failed",
                "422": "Unprocessable Entity",
                "429": "Too Many Requests",
                "500": "Internal Server Error",
                "502": "Bad Gateway",
                "503": "Service Unavailable",
                "504": "Gateway Timeout",
                "507": "Insufficient Storage",
            }

            return status_map.get(str(status), "")

        except Exception:
            return None
