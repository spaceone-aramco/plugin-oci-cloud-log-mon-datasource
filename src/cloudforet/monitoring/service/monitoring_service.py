import logging

from spaceone.core.service import *

from cloudforet.monitoring.manager.monitoring_manager import MonitoringManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@event_handler
class MonitoringService(BaseService):
    def __init__(self, metadata):
        super().__init__(metadata)

    @transaction
    @check_required(["options", "secret_data", "query", "start", "end"])
    @change_timestamp_value(["start", "end"], timestamp_format="iso8601")
    def list_logs(self, params):
        """Get quick list of resources

        Args:
            params (dict) {
                'options': 'dict',
                'secret_data': 'dict',
                'query': 'dict',
                'start': 'timestamp',
                'end': 'timestamp',
            }

        Returns: list of resources
        """
        monitoring_manager: MonitoringManager = self.locator.get_manager(
            MonitoringManager
        )

        for logs in monitoring_manager.list_logs(params):
            yield logs
