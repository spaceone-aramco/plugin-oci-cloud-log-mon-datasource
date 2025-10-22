import logging
from datetime import timedelta

import oci

from cloudforet.monitoring.libs.oci_cloud_connector import OCIConnector

_LOGGER = logging.getLogger(__name__)


class OCILoggingConnector(OCIConnector):
    """OCI Logging Search API specific connector"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def make_client(self):
        """create OCI Logging Search Client"""
        config = self.get_config()
        if not config:
            return None
        return oci.loggingsearch.LogSearchClient(config)

    def search_logs(self, params):
        """OCI Search Logs API call"""
        try:
            # create Logging Search Client
            logging_search_client = self.make_client()
            if not logging_search_client:
                yield []
                return

            start_time = params.get("start")
            end_time = params.get("end")

            if start_time > end_time:
                _LOGGER.debug("Start time must be before end time.")
                yield []
                return

            if end_time.date() - start_time.date() > timedelta(days=14):
                _LOGGER.debug(
                    "OCI Search Logs API only allows up to 14 days per request."
                )
                yield []
                return

            start_time_formatted = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_time_formatted = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            query = params.get("query", {})
            query_filters = query.get("filters", [])
            size = query.get("size", 1)

            # generate search query
            search_query = self._generate_search_query(query_filters)

            search_request = oci.loggingsearch.models.SearchLogsDetails(
                time_start=start_time_formatted,
                time_end=end_time_formatted,
                search_query=search_query,
                is_return_field_info=False,
            )

            # paging processing
            page_token = None
            count = 0

            while True:
                if count >= size:
                    break

                # API call
                if page_token:
                    response = logging_search_client.search_logs(
                        search_logs_details=search_request, limit=1000, page=page_token
                    )
                else:
                    response = logging_search_client.search_logs(
                        search_logs_details=search_request, limit=1000
                    )

                # process results
                logs = response.data.results if response.data else []
                if logs:
                    yield logs

                # check next page token
                page_token = (
                    response.headers.get("opc-next-page")
                    if hasattr(response, "headers")
                    else None
                )

                # if there is no next page token, stop
                if not page_token:
                    break

                count += 1

        except Exception as e:
            _LOGGER.debug(f"Failed to list log entries: {e}")
            yield []

    def _generate_search_query(self, filters):
        # default search target
        base_query = f'search "{self.compartment_id}/_Audit"'

        # process filters list (combined with OR conditions)
        filter_groups = []

        for filter_item in filters:
            labels = filter_item.get("labels", [])
            if labels:
                # combine labels within each filter with AND conditions
                label_conditions = []
                for label in labels:
                    key = label.get("key")
                    value = label.get("value")
                    if key and value:
                        label_conditions.append(f"{key}='{value}'")

                # create one filter group (combined with AND conditions)
                if label_conditions:
                    filter_group = f"({' and '.join(label_conditions)})"
                    filter_groups.append(filter_group)

        # combine conditions
        if filter_groups:
            # combine filter groups with OR conditions
            filter_clause = f" | where {' or '.join(filter_groups)}"
            query = base_query + filter_clause
        else:
            query = base_query

        # add sorting
        query += " | sort by datetime desc"

        return query
