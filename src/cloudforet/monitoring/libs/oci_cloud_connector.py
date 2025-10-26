import logging

import oci
from spaceone.core.connector import BaseConnector

_LOGGER = logging.getLogger(__name__)


class OCIConnector(BaseConnector):
    """OCI 인증 및 기본 설정을 위한 베이스 커넥터"""

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.secret_data = kwargs.get("secret_data") or {}
        query = kwargs.get("query") or {}

        self.region = query.get("region") or self.secret_data.get("region")
        self.compartment_id = (
            query.get("compartment_id")
            or self.secret_data.get("compartment_id")
            or self.secret_data.get("tenancy")
        )
        _LOGGER.debug(f"OCI Connector - compartment_id: {self.compartment_id}")

    def get_config(self):
        """OCI 설정 딕셔너리 생성"""
        try:
            config = {
                "user": self.secret_data["user"],
                "fingerprint": self.secret_data["fingerprint"],
                "key_content": self.secret_data["key_content"],
                "tenancy": self.secret_data["tenancy"],
                "region": self.region,
            }

            # if pass_phrase is in secret_data, add it to config
            if "pass_phrase" in self.secret_data:
                config["pass_phrase"] = self.secret_data["pass_phrase"]

            # validate OCI config
            oci.config.validate_config(config)
            return config

        except Exception as e:
            _LOGGER.error(f"Invalid OCI authentication configuration: {e}")
            return {}

    def verify(self):
        """verify OCI authentication (using Identity Client)"""
        try:
            config = self.get_config()

            # 빈 설정인 경우 검증 실패 메시지 반환
            if not config:
                error_msg = "Invalid OCI authentication configuration"
                _LOGGER.error(error_msg)

            identity_client = oci.identity.IdentityClient(config)

            # verify authentication by checking the current user information
            user_response = identity_client.get_user(self.secret_data["user"])
            _LOGGER.info(
                f"OCI authentication verified for user: {user_response.data.name}"
            )
            return {"success": True, "message": "OCI authentication verified"}

        except oci.exceptions.ServiceError as e:
            error_msg = (
                "OCI authentication failed"
                if e.status == 401
                else f"OCI API error during verification: {e.message}"
            )
            _LOGGER.error(error_msg)

        except Exception as e:
            error_msg = f"Failed to verify OCI connection: {str(e)}"
            _LOGGER.error(error_msg)
