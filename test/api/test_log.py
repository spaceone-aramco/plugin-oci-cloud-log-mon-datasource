import json
import os
import unittest

from spaceone.core.unittest.runner import RichTestRunner
from spaceone.tester import TestCase, print_json

OCI_CONFIG_PATH = os.environ.get("OCI_CONFIG_PATH", None)

if OCI_CONFIG_PATH is None:
    print("""
        ##################################################
        # INFO 
        #
        # Configure your OCI credential for test
        # https://docs.oracle.com/en-us/iaas/Content/API/Concepts/apisigningkey.htm

        ##################################################
        example)

        export OCI_CONFIG_PATH="<PATH_TO_OCI_CONFIG_JSON>" 
        
        OCI Config JSON format:
        {
            "user": "ocid1.user.oc1...",
            "fingerprint": "aa:bb:cc:dd:ee:ff:...",
            "key_content": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----",
            "tenancy": "ocid1.tenancy.oc1...",
            "region": "us-ashburn-1",
            "compartment_id": "ocid1.compartment.oc1..."
        }
    """)


def _get_credentials():
    if OCI_CONFIG_PATH and os.path.exists(OCI_CONFIG_PATH):
        with open(OCI_CONFIG_PATH) as json_file:
            json_data = json.load(json_file)
            return json_data
    else:
        # 테스트용 더미 데이터
        return {
            "user": "ocid1.user.oc1..test",
            "fingerprint": "aa:bb:cc:dd:ee:ff:test",
            "key_content": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----",
            "tenancy": "ocid1.tenancy.oc1..test",
            "region": "us-ashburn-1",
            "compartment_id": "ocid1.compartment.oc1..test",
        }


class TestOCILog(TestCase):
    def test_init(self):
        """OCI Logging 플러그인 초기화 테스트"""
        v_info = self.monitoring.DataSource.init({"options": {}})
        print_json(v_info)

    def test_verify(self):
        """OCI 연결 검증 테스트"""
        schema = ""
        options = {}
        secret_data = _get_credentials()
        self.monitoring.DataSource.verify(
            {"schema": schema, "options": options, "secret_data": secret_data}
        )

    def test_log_list(self):
        """OCI 로그 조회 테스트"""
        secret_data = _get_credentials()

        params = {
            "options": {},
            "secret_data": secret_data,
            "query": {
                "filters": [
                    {
                        "compartment_id": secret_data.get("compartment_id"),
                        "log_type": "SERVICE",
                    }
                ]
            },
            "start": "2025-10-20T00:00:00Z",
            "end": "2025-10-20T23:59:59Z",
            "region": secret_data.get("region", "us-ashburn-1"),
            "size": 3,
        }

        # 빈 쿼리 테스트용
        # empty_params = {
        #     'options': {},
        #     'secret_data': secret_data,
        #     'query': {},
        #     'start': '2025-10-20T00:00:00Z',
        #     'end': '2025-10-20T23:59:59Z'
        # }

        resource_stream = self.monitoring.Log.list(params)

        for res in resource_stream:
            print_json(res)


if __name__ == "__main__":
    unittest.main(testRunner=RichTestRunner)
