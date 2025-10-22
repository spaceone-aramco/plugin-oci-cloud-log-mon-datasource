# plugin-oci-cloud-log-mon-datasource

![Oracle Cloud Infrastructure](https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/oci/oci-observability-and-management-logging.svg)

**Plugin to collect Oracle Cloud Infrastructure (OCI) Logging**

> SpaceONE's [plugin-oci-cloud-log-mon-datasource](https://github.com/cloudforet-io/plugin-oci-cloud-log-mon-datasource) is a convenient tool to 
get cloud log data from Oracle Cloud Infrastructure platform. 

Find us also at [Dockerhub](https://hub.docker.com/repository/docker/spaceone/plugin-oci-cloud-log-mon-datasource)
> Latest stable version : 1.0.0

Please contact us if you need any further information. (<support@spaceone.dev>)

---

## Authentication Overview
Registered service account on SpaceONE must have certain permissions to collect cloud service data 
Please, set authentication privilege for followings:

### OCI Service Endpoint
```
https://logging.{region}.oci.oraclecloud.com
```

### Required IAM Policies
```
- LOG_CONTENT_READ
```

### Logging API used
```
- Logging Search API
```

### Authentication Methods
- **API Key Authentication**: Using OCI Config file or environment variables
- **Instance Principal**: Automatic authentication when running on OCI instances

### Required OCI Configuration
```json
{
  "user": "ocid1.user.oc1...",
  "fingerprint": "aa:bb:cc:dd:ee:ff:...",
  "key_content": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----",
  "tenancy": "ocid1.tenancy.oc1...",
  "region": "us-ashburn-1",
  "compartment_id": "ocid1.compartment.oc1..."
}
```

---
## Features
- **Audit Log Collection**: Collect OCI audit logs and application logs
- **Real-time Monitoring**: Real-time log viewing in SpaceONE console
- **Detailed Information**: Display detailed log entry information via popup
- **Filtering**: Filter by time range, resource type
- **Flexible Querying**: Advanced search capabilities with OCI Logging Search API
---

### OCI Config secret_data
```json
{
  "user": "ocid1.user.oc1..aaaaaaaabcdefghijklmnopqrstuvwxyz",
  "fingerprint": "aa:bb:cc:dd:ee:ff:gg:hh:ii:jj:kk:ll:mm:nn:oo:pp",
  "key_content": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC...\n-----END PRIVATE KEY-----",
  "tenancy": "ocid1.tenancy.oc1..aaaaaaaabcdefghijklmnopqrstuvwxyz",
  "region": "us-ashburn-1",
  "compartment_id": "ocid1.compartment.oc1..aaaaaaaabcdefghijklmnopqrstuvwxyz"
}
```
---

## Usage

### DataSource Initialization
```python
from cloudforet.monitoring.api.plugin.data_source import DataSource

# Initialize plugin
result = DataSource().init({'options': {}})
```

### Log Collection
```python
from cloudforet.monitoring.api.plugin.log import Log

params = {
    'options': {},
    'secret_data': {
        'user': 'ocid1.user.oc1...',
        'fingerprint': 'aa:bb:cc:dd:ee:ff:...',
        'key_content': '-----BEGIN PRIVATE KEY-----\n...',
        'tenancy': 'ocid1.tenancy.oc1...',
        'region': 'us-ashburn-1',
        'compartment_id': 'ocid1.compartment.oc1...'
    },
    'query': {
        "filters": [
            {
                "labels": [
                    {
                        "key": "data.resourceId",
                        "value": "ocid1.vnic.oc1.ap-seoul-1.abuwgxxxxxx"
                    },
                    {
                        "key": "type",
                        "value": "io.k8s.coordination.v1.leases.update"
                    }
                ]
            },
            {
                "labels": [
                    {
                        "key": "data.resourceId",
                        "value": "ocid1.floatingip.oc1.ap-seoul-1.abuwgxxxxxx"
                    }
                ]
            }
        ],
        "region": "ap-seoul-1",
        "size": 3
    },
    'start': '2023-10-16T00:00:00Z',
    'end': '2023-10-16T23:59:59Z'
}

# Collect logs
log_stream = Log().list(params, {})
for logs in log_stream:
    print(logs)
```

---

## Release note

### Ver 1.0.0
- Initial release for OCI Logging integration
- Support for OCI Audit Logs
- Real-time log streaming
- Advanced filtering and search capabilities
- HTTP status code conversion
- System user filtering
- Comprehensive error handling