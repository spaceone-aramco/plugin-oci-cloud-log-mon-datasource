import logging

from spaceone.core.manager import BaseManager

from cloudforet.monitoring.connector.oci_logging_connector import OCILoggingConnector
from cloudforet.monitoring.manager.metadata_manager import MetadataManager
from cloudforet.monitoring.model.data_source_response_model import DataSourceMetadata

_LOGGER = logging.getLogger(__name__)


class DataSourceManager(BaseManager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def init(params):
        options = params.get("options")
        meta_manager = MetadataManager()
        response_model = DataSourceMetadata(
            {"_metadata": meta_manager.get_data_source_metadata()}, strict=False
        )
        return response_model.to_primitive()

    def verify(self, params):
        oci_logging_connector: OCILoggingConnector = self.locator.get_connector(
            OCILoggingConnector, **params
        )
        oci_logging_connector.verify()
