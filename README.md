**Language**: [English](README.md) | [한국어](README_KR.md)

<h1 align="center">OCI Logging Monitoring Plugin</h1>   

<br/>  
  <img width="245" src="https://spaceone-custom-assets.s3.ap-northeast-2.amazonaws.com/console-assets/icons/cloud-services/oci/oci-observability-and-management-logging.svg">
<br/>
<div>
    <p> 
        <br>
        <img alt="Version"  src="https://img.shields.io/badge/version-2.160.0-blue.svg?cacheSeconds=2592000"  />    
        <a href="https://www.apache.org/licenses/LICENSE-2.0"  target="_blank"><img alt="License: Apache 2.0"  src="https://img.shields.io/badge/License-Apache 2.0-yellow.svg" /></a> 
    </p> 
</div>

**SpaceONE Logging Monitoring Plugin for Oracle Cloud Infrastructure**

The plugin-oci-cloud-log-mon-datasource provides comprehensive log monitoring and collection capabilities for Oracle Cloud Infrastructure (OCI) Logging service in SpaceONE. 

---

## Table of Contents

- [Monitoring Contents](#monitoring-contents)
- [OCI Service Endpoints](#oci-service-endpoint-in-use)
- [Supported Regions](#region-list)
- [Authentication Overview](#authentication-overview)
- [Required IAM Permissions](#required-iam-permissions)
- [Secret Data Configuration](#secret-data-configuration)
- [Plugin Architecture](#plugin-architecture)
- [Input Parameters](#input-parameters)

---

## Monitoring Contents

### OCI Logging Service
- **Audit Logs** - OCI audit trail logs for security and compliance monitoring
- **Application Logs** - Custom application logs from OCI services
- **Service Logs** - System and service-level logs from OCI infrastructure
- **Search & Filter** - Advanced log search with time-based and content-based filtering
- **Real-time Monitoring** - Live log streaming and monitoring capabilities

---

## OCI Service Endpoint (in use)

The endpoint used to collect OCI log data.
OCI Logging endpoint is a URL consisting of a region and the logging service code.
<pre>
[https://logging.[region-code].oci.oraclecloud.com](https://docs.oracle.com/en-us/iaas/api/#/en/logging-search/20190909/)
</pre>

We use region-specific endpoints for log collection across different OCI regions.

---

### Region List

Below is the OCI region information.
The regions we support are all regions supported by OCI. We target the regions returned
by [ListRegions()](https://docs.oracle.com/en-us/iaas/api/#/en/identity/20160918/Region/ListRegions)

| No. | Region name                    | Region Code     | No.| Region name                    | Region Code            |
|-----|--------------------------------|-----------------|----|--------------------------------|------------------------|
| 1   | Australia East (Sydney)        | ap-sydney-1     | 21 | Netherlands Northwest (Amsterdam)   | eu-amsterdam-1    |
| 2   | Australia Southeast (Melbourne)| ap-melbourne-1  | 22 | Saudi Arabia Central (Riyadh)       | me-riyadh-1       |
| 3   | Brazil East (Sao Paulo)        | sa-saopaulo-1   | 23 | Saudi Arabia West (Jeddah)	        | me-jeddah-1       |
| 4   | Brazil Southeast (Vinhedo)     | sa-vinhedo-1    | 24 | Serbia Central (Jovanovac)          | eu-jovanovac-1    |
| 5   | Canada Southeast (Montreal)    | ca-montreal-1   | 25 | Singapore (Singapore)               | ap-singapore-1	  |
| 6   | Canada Southeast (Toronto)     | ca-toronto-1    | 26 | Singapore West (Singapore)          | ap-singapore-2    |
| 7   | Chile Central (Santiago)       | sa-santiago-1   | 27 | South Africa Central (Johannesburg) | af-johannesburg-1 |
| 8   | Chile West (Valparaiso)        | sa-valparaiso-1 | 28 | South Korea Central (Seoul)         | ap-seoul-1        |
| 9   | Colombia Central (Bogota)      | sa-bogota-1     | 29 | South Korea North (Chuncheon)       | ap-chuncheon-1    |
| 10  | France Central (Paris)         | eu-paris-1      | 30 | Spain Central (Madrid)              | eu-madrid-1       |
| 11  | France South (Marseille)       | eu-marseille-1  | 31 | Sweden Central (Stockholm)          | eu-stockholm-1    |
| 12  | Germany Central (Frankfurt)	   | eu-frankfurt-1  | 32 | Switzerland North (Zurich)	        | eu-zurich-1       |
| 13  | India South (Hyderabad)        | ap-hyderabad-1	 | 33 | UAE Central (Abu Dhabi)             | me-abudhabi-1     |
| 14  | India West (Mumbai)            | ap-mumbai-1     | 34 | UAE East (Dubai)                    | me-dubai-1        |
| 15  | Israel Central (Jerusalem)     | il-jerusalem-1  | 35 | UK South (London)                   | uk-london-1       |
| 16  | Italy Northwest (Milan)        | eu-milan-1      | 36 | UK West (Newport)                   | uk-cardiff-1      |
| 17  | Japan Central (Osaka)          | ap-osaka-1      | 37 | US East (Ashburn)                   | us-ashburn-1      |
| 18  | Japan East (Tokyo)             | ap-tokyo-1      | 38 | US Midwest (Chicago)                | us-chicago-1      |
| 19  | Mexico Central (Queretaro)     | mx-queretaro-1  | 39 | US West (Phoenix)                   | us-phoenix-1      |
| 20  | Mexico Northeast (Monterrey)   | mx-monterrey-1  | 40 | US West (San Jose)                  | us-sanjose-1      |

---

## Authentication Overview

The registered service account on SpaceONE must have certain permissions to collect log data. Please set
authentication privileges as follows:

### IAM Group: `SpaceONELogMonitors`

This group must be created in Oracle Cloud Infrastructure (OCI) Identity service.  
It is designed to hold the service accounts (IAM users) used by SpaceONE log monitoring.  
These monitors will query OCI Logging APIs to gather log data from your OCI resources.

### How to Set Up (Using OCI CLI)

#### Step 1. Create IAM Group
```bash
oci iam group create \
  --name "SpaceONELogMonitors" \
  --description "Group for SpaceONE Log Monitor service accounts with log read permissions"
```

#### Step 2. Create IAM User
```bash
oci iam user create \
  --name "spaceONELogUser" \
  --description "Service account for SpaceONE log monitoring"
```

#### Step 3. Add User to Group
```bash
oci iam group add-user \
  --group-id $(oci iam group get --group-name "SpaceONELogMonitors" --query 'data.id' --raw-output) \
  --user-id $(oci iam user get --user-name "spaceONELogUser" --query 'data.id' --raw-output)
```

Policy Type: IAM Policy (Console or CLI)
Target: Group (e.g., SpaceONELogMonitors)

Format:
Allow group <group_name> to <verb> <resource-type> in <scope>

## Required IAM Permissions
- LOG_CONTENT_READ

### 🔒 Permission Scope Selection Guide

#### **Option 1: Tenancy Scope (Convenience Priority)**
```bash
# Collect logs from entire tenancy (Recommended: Development/Test environments)
Allow group SpaceONELogMonitors to read log-content in tenancy
```

#### **Option 2: Compartment Scope (Security Priority)**  
```bash
# Collect logs only from specific compartment (Recommended: Production environments)
Allow group SpaceONELogMonitors to read log-content in compartment <compartment-name>
```

> **💡 Recommendations**: 
> - **Development/Test**: Use `in tenancy` for operational convenience
> - **Production**: Use `in compartment` for enhanced security

---

### Logging Services
```bash
# OCI Logging Service - Core Permissions
Allow group SpaceONELogMonitors to read log-content in tenancy
Allow group SpaceONELogMonitors to inspect log-groups in tenancy
Allow group SpaceONELogMonitors to inspect logs in tenancy
```

### Common Permissions
```bash
# Identity & Global Information
Allow group SpaceONELogMonitors to inspect compartments in tenancy
Allow group SpaceONELogMonitors to inspect tenancies in tenancy
Allow group SpaceONELogMonitors to inspect regions in tenancy
```

---

## Secret Data Configuration

To monitor OCI logs in SpaceONE, you need to register OCI API authentication information as Secret Data.

### Required Authentication Information

The following information is required for OCI API key-based authentication:

| Field Name | Description | Example |
|------------|-------------|---------|
| `user` | OCI user OCID | `ocid1.user.oc1..aaaaaaaa...` |
| `tenancy` | OCI tenancy OCID | `ocid1.tenancy.oc1..aaaaaaaa...` |
| `region` | Default region code | `us-ashburn-1` |
| `fingerprint` | API key fingerprint | `aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99` |
| `key_content` | Private Key content (PEM format) | `-----BEGIN PRIVATE KEY-----\n...` |

### API Key Generation Methods

#### 1. **Generation via OCI Console**

1. **Login to OCI Console** → Identity & Security → Users
2. **Select User** (e.g., `spaceone-log-monitor`)
3. **API Keys** → **Add API Key**
4. **Select Generate API Key Pair**
5. **Download Private Key** and **Download Public Key**
6. **Review information in Configuration File Preview**

#### 2. **Generation via OCI CLI**

```bash
# Generate API key pair
openssl genrsa -out ~/.oci/oci_api_key.pem 2048
openssl rsa -pubout -in ~/.oci/oci_api_key.pem -out ~/.oci/oci_api_key_public.pem

# Add public key to user
oci iam user api-key upload \
  --user-id $(oci iam user list --name "spaceone-log-monitor" --query 'data[0].id' --raw-output) \
  --key-file ~/.oci/oci_api_key_public.pem

# Check fingerprint
openssl rsa -pubout -outform DER -in ~/.oci/oci_api_key.pem | openssl md5 -c
```

### Secret Data Examples

#### **JSON Format**
```json
{
  "user": "ocid1.user.oc1..aaaaaaaa7n2sclkuqj5ozc3dqm2vwqv7qpwxyz123456789abcdef",
  "tenancy": "ocid1.tenancy.oc1..aaaaaaaa7n2sclkuqj5ozc3dqm2vwqv7qpwxyz123456789abcdef",
  "region": "us-ashburn-1",
  "fingerprint": "aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99",
  "key_content": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----"
}
```

## Plugin Architecture

### Service-Manager-Connector Pattern

This plugin follows the SpaceONE standard 3-tier architecture:

```
Service Layer (monitoring_service.py)
├── MonitoringService.list_logs - Log query entry point
└── DataSourceService.verify - Authentication verification

Manager Layer (manager/)
├── MonitoringManager - Log processing and conversion
├── DataSourceManager - Data source management
└── MetadataManager - UI metadata management

Connector Layer (connector/)
├── OCILoggingConnector - OCI Logging Search API client
└── OCIConnector (base) - OCI authentication and configuration
```

### Data Flow

```mermaid
graph TD
    A[SpaceONE Core] --> B[monitoring_service.py]
    B --> C[MonitoringManager]
    C --> D[OCILoggingConnector]
    D --> E[OCI Logging Search API]
    E --> F[OCI Log Data]
    
    F --> G[Raw Log Entries]
    G --> D
    D --> H[Processed Logs]
    H --> C
    C --> I[Log Event Objects]
    I --> B
    B --> J[SpaceONE Response]
    J --> A
```

### Core Features

#### **Real-time Log Monitoring**
- **Live Log Streaming**: Real-time log collection from OCI Logging service
- **Time-based Queries**: Flexible time range queries with up to 14-day windows
- **Advanced Filtering**: Content-based and metadata-based log filtering

#### **Flexible Query Capabilities**
- **Search Query Generation**: Automatic query generation from filter parameters
- **Pagination Support**: Efficient handling of large log datasets
- **Multiple Log Types**: Support for audit logs, application logs, and service logs

#### **Security and Stability**
- **Read-Only Permissions**: Safe monitoring with principle of least privilege
- **Error Handling**: Graceful handling of API errors and timeouts
- **Authentication Verification**: Built-in connection testing and validation

#### **Standardized Data**
- **SpaceONE Schema**: Consistent log data structure for SpaceONE integration
- **Status Code Mapping**: HTTP status code to text conversion
- **Metadata Enrichment**: Enhanced log entries with additional context

### Project Structure

```
plugin-oci-cloud-log-mon-datasource/
├── README.md                    # Project overview and usage
├── pkg/pip_requirements.txt     # Python dependencies
├── Dockerfile                   # Container image build
├── docs/ko/                     # Korean documentation
│   ├── development/             # Development guides
│   └── prd/                     # Product Requirements Documents
├── src/cloudforet/monitoring/   # Plugin source code
│   ├── api/plugin/              # gRPC API definitions
│   ├── service/                 # Business logic layer
│   ├── manager/                 # Resource management layer
│   ├── connector/               # OCI API connection layer
│   ├── model/                   # Data models and schemas
│   └── libs/                    # Shared libraries
└── test/                        # Test code
    └── api/                     # API tests
```

---

## Input Parameters

This plugin can control log monitoring behavior through various input parameters.

### **Query Parameters**

Parameters used in log query requests.

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `start` | `timestamp` | Start time for log search (ISO8601 format) | `2024-01-01T00:00:00Z` |
| `end` | `timestamp` | End time for log search (ISO8601 format, max 14 days from start) | `2024-01-02T00:00:00Z` |
| `query` | `object` | Query filters and options | See below |

#### **Query Object Structure**
```json
{
  "query": {
    "filters": [
      {
        "key": "data.resourceId",
        "value": "ocid1.vnic.oc1.ap-seoul-1.abuwgxxxxxx"
      }
    ],
    "region": "ap-seoul-1",
    "size": 1
  }
}
```

### **Secret Data Parameters**

Required information for OCI API authentication.

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `user` | `string` | OCI user OCID | `ocid1.user.oc1..aaaaaaaa...` |
| `tenancy` | `string` | OCI tenancy OCID | `ocid1.tenancy.oc1..aaaaaaaa...` |
| `region` | `string` | Default region code | `us-ashburn-1` |
| `fingerprint` | `string` | API key fingerprint | `aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99` |
| `key_content` | `string` | Private Key content (PEM format) | `-----BEGIN PRIVATE KEY-----\n...` |

### **Query Options**

Available query options for log queries:

| Query | Description | Example Values |
|-------|-------------|----------------|
| `filters.key` | Search key | `data.resourceId`, `data.eventName` |
| `filters.value` | Search value for the key | `ocid1.vnic.oc1.ap-seoul-1.abuwgxxxxxx`, `ListSubscriptions` |
| `region` | Region | `ap-seoul-1`, `us-ashburn-1` |
| `size` | Page size | `1`, `10` |

### **Time Range Limitations**

- **Maximum Range**: 14 days per query
- **Format**: ISO8601 format (e.g., `2024-01-01T00:00:00Z`)
- **Timezone**: UTC timezone recommended

### **Usage Examples**

#### **Log Query**
```json
{
  "start": "2024-01-01T00:00:00Z",
  "end": "2024-01-01T01:00:00Z",
  "query": {
    "filters": [
      {
        "key": "data.resourceId",
        "value": "ocid1.vnic.oc1.ap-seoul-1.abuwgxxxxxx"
      }
    ],
    "region": "ap-seoul-1",
    "size": 1
  }
}
```

### **Parameter Validation**

The plugin performs the following validation on input parameters:

#### **Time Range Validation**
- Start time must be before end time
- Time range cannot exceed 14 days
- Times must be in valid ISO8601 format

#### **Query Validation**
- Filter keys must be valid log content paths
- Size parameter must be positive integer

#### **Secret Data Validation**
- Required fields: `user`, `tenancy`, `region`, `fingerprint`, `key_content`
- OCID format check: Must start with `ocid1.` prefix
- Private Key format check: Must be in PEM format

---

## Options

The plugin supports various configuration options for customizing log monitoring behavior. These options can be set during data source creation or updated as needed.

---
