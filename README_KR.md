**Language**: [English](README.md) | [한국어](README_KR.md)

<h1 align="center">OCI 로깅 모니터링 플러그인</h1>  

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

**Oracle Cloud Infrastructure용 SpaceONE 로깅 모니터링 플러그인**

plugin-oci-cloud-log-mon-datasource는 SpaceONE에서 Oracle Cloud Infrastructure (OCI) 로깅 서비스에 대한 포괄적인 로그 모니터링 및 수집 기능을 제공합니다.

---

## 목차 (Table of Contents)

- [모니터링 대상](#모니터링-대상)
- [OCI 서비스 엔드포인트](#oci-service-endpoint-in-use)
- [지원 리전 목록](#region-list)
- [인증 개요](#authentication-overview)
- [IAM 권한 설정](#필요-IAM-권한-목록)
- [Secret Data 구성](#Secret-Data-구성)
- [플러그인 아키텍처](#플러그인-아키텍처)
- [입력 파라미터](#입력-파라미터-input-parameters)

---

## 모니터링 대상

### OCI 로깅 서비스
- **감사 로그** - 보안 및 컴플라이언스 모니터링을 위한 OCI 감사 추적 로그
- **애플리케이션 로그** - OCI 서비스의 사용자 정의 애플리케이션 로그
- **서비스 로그** - OCI 인프라의 시스템 및 서비스 수준 로그
- **검색 및 필터링** - 시간 기반 및 내용 기반 필터링을 통한 고급 로그 검색
- **실시간 모니터링** - 실시간 로그 스트리밍 및 모니터링 기능

---

## OCI Service Endpoint (in use)

OCI 로그 데이터를 수집하는 데 사용되는 엔드포인트입니다.
OCI 로깅 엔드포인트는 리전과 로깅 서비스 코드로 구성된 URL입니다.
<pre>
[https://logging.[region-code].oci.oraclecloud.com](https://docs.oracle.com/en-us/iaas/api/#/en/logging-search/20190909/)
</pre>

다양한 OCI 리전에서 로그 수집을 위해 리전별 엔드포인트를 사용합니다.

---

### Region list

아래는 OCI 리전 정보입니다.
지원하는 리전은 OCI에서 지원하는 모든 리전입니다. [ListRegions()](https://docs.oracle.com/en-us/iaas/api/#/en/identity/20160918/Region/ListRegions)에서 반환되는 리전을 대상으로 합니다.

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

SpaceONE에 등록된 서비스 계정은 로그 데이터를 수집하기 위해 특정 권한을 가져야 합니다. 다음과 같이 인증 권한을 설정하세요:

### IAM Group: `SpaceONELogMonitors`

이 그룹은 Oracle Cloud Infrastructure (OCI) Identity 서비스에서 생성되어야 합니다.  
SpaceONE 로그 모니터링에서 사용하는 서비스 계정(IAM 사용자)을 보관하도록 설계되었습니다.  
이러한 모니터는 OCI 로깅 API를 쿼리하여 OCI 리소스에서 로그 데이터를 수집합니다.

### 설정 방법 (OCI CLI 사용)

#### Step 1. IAM Group 생성
```bash
oci iam group create \
  --name "SpaceONELogMonitors" \
  --description "SpaceONE 로그 모니터 서비스 계정을 위한 그룹 (로그 읽기 권한)"
```

#### Step 2. IAM User 생성
```bash
oci iam user create \
  --name "spaceONELogUser" \
  --description "SpaceONE 로그 모니터링을 위한 서비스 계정"
```

#### Step 3. 그룹에 사용자 추가
```bash
oci iam group add-user \
  --group-id $(oci iam group get --group-name "SpaceONELogMonitors" --query 'data.id' --raw-output) \
  --user-id $(oci iam user get --user-name "spaceONELogUser" --query 'data.id' --raw-output)
```

Policy Type: IAM Policy (Console or CLI)
Target: Group (e.g., SpaceONELogMonitors)

Format:
Allow group <group_name> to <verb> <resource-type> in <scope>

## 필요 IAM 권한 목록
- LOG_CONTENT_READ

### 🔒 권한 범위 선택 가이드

#### **Option 1: Tenancy 범위 (간편함 우선)**
```bash
# 전체 테넌시에서 로그 수집 (권장: 개발/테스트 환경)
Allow group SpaceONELogMonitors to read log-content in tenancy
```

#### **Option 2: Compartment 범위 (보안 우선)**  
```bash
# 특정 구획에서만 로그 수집 (권장: 프로덕션 환경)
Allow group SpaceONELogMonitors to read log-content in compartment <compartment-name>
```

> **💡 권장사항**: 
> - **개발/테스트**: `in tenancy` 사용으로 운영 편의성 확보
> - **프로덕션**: `in compartment` 사용으로 보안 강화

---

### 로깅 서비스
```bash
# OCI 로깅 서비스 - 핵심 권한
Allow group SpaceONELogMonitors to read log-content in tenancy
Allow group SpaceONELogMonitors to inspect log-groups in tenancy
Allow group SpaceONELogMonitors to inspect logs in tenancy
```

### 공통 권한
```bash
# Identity & Global Information
Allow group SpaceONELogMonitors to inspect compartments in tenancy
Allow group SpaceONELogMonitors to inspect tenancies in tenancy
Allow group SpaceONELogMonitors to inspect regions in tenancy
```

---

## Secret Data 구성

SpaceONE에서 OCI 로그를 모니터링하기 위해서는 OCI API 인증 정보를 Secret Data로 등록해야 합니다.

### 필수 인증 정보

OCI API 키 기반 인증을 위해 다음 정보가 필요합니다:

| 필드명 | 설명 | 예시 |
|--------|------|------|
| `user` | OCI 사용자 OCID | `ocid1.user.oc1..aaaaaaaa...` |
| `tenancy` | OCI 테넌시 OCID | `ocid1.tenancy.oc1..aaaaaaaa...` |
| `region` | 기본 리전 코드 | `us-ashburn-1` |
| `fingerprint` | API 키 지문 | `aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99` |
| `key_content` | Private Key 내용 (PEM 형식) | `-----BEGIN PRIVATE KEY-----\n...` |

### API 키 생성 방법

#### 1. **OCI Console을 통한 생성**

1. **OCI Console 로그인** → Identity & Security → Users
2. **사용자 선택** (예: `spaceone-log-monitor`)
3. **API Keys** → **Add API Key**
4. **Generate API Key Pair** 선택
5. **Download Private Key** 및 **Download Public Key**
6. **Configuration File Preview**에서 정보 확인

#### 2. **OCI CLI를 통한 생성**

```bash
# API 키 쌍 생성
openssl genrsa -out ~/.oci/oci_api_key.pem 2048
openssl rsa -pubout -in ~/.oci/oci_api_key.pem -out ~/.oci/oci_api_key_public.pem

# 공개 키를 사용자에게 추가
oci iam user api-key upload \
  --user-id $(oci iam user list --name "spaceone-log-monitor" --query 'data[0].id' --raw-output) \
  --key-file ~/.oci/oci_api_key_public.pem

# 지문 확인
openssl rsa -pubout -outform DER -in ~/.oci/oci_api_key.pem | openssl md5 -c
```

### Secret Data 예시

#### **JSON 형식**
```json
{
  "user": "ocid1.user.oc1..aaaaaaaa7n2sclkuqj5ozc3dqm2vwqv7qpwxyz123456789abcdef",
  "tenancy": "ocid1.tenancy.oc1..aaaaaaaa7n2sclkuqj5ozc3dqm2vwqv7qpwxyz123456789abcdef",
  "region": "us-ashburn-1",
  "fingerprint": "aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99",
  "key_content": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----"
}
```

## 플러그인 아키텍처

### Service-Manager-Connector 패턴

본 플러그인은 SpaceONE 표준 3계층 아키텍처를 따릅니다:

```
Service Layer (monitoring_service.py)
├── MonitoringService.list_logs - 로그 쿼리 진입점
└── DataSourceService.verify - 인증 검증

Manager Layer (manager/)
├── MonitoringManager - 로그 처리 및 변환
├── DataSourceManager - 데이터 소스 관리
└── MetadataManager - UI 메타데이터 관리

Connector Layer (connector/)
├── OCILoggingConnector - OCI 로깅 검색 API 클라이언트
└── OCIConnector (base) - OCI 인증 및 구성
```

### 데이터 플로우

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

### 핵심 기능

#### **실시간 로그 모니터링**
- **실시간 로그 스트리밍**: OCI 로깅 서비스에서 실시간 로그 수집
- **시간 기반 쿼리**: 최대 14일 창으로 유연한 시간 범위 쿼리
- **고급 필터링**: 내용 기반 및 메타데이터 기반 로그 필터링

#### **유연한 쿼리 기능**
- **검색 쿼리 생성**: 필터 파라미터에서 자동 쿼리 생성
- **페이지네이션 지원**: 대용량 로그 데이터셋의 효율적 처리
- **다중 로그 타입**: 감사 로그, 애플리케이션 로그, 서비스 로그 지원

#### **보안 및 안정성**
- **읽기 전용 권한**: 최소 권한 원칙으로 안전한 모니터링
- **에러 처리**: API 오류 및 타임아웃의 우아한 처리
- **인증 검증**: 내장된 연결 테스트 및 검증

#### **표준화된 데이터**
- **SpaceONE 스키마**: SpaceONE 통합을 위한 일관된 로그 데이터 구조
- **상태 코드 매핑**: HTTP 상태 코드를 텍스트로 변환
- **메타데이터 강화**: 추가 컨텍스트로 로그 항목 강화

### 프로젝트 구조

```
plugin-oci-cloud-log-mon-datasource/
├── README.md                    # 프로젝트 개요 및 사용법
├── pkg/pip_requirements.txt     # Python 의존성
├── Dockerfile                   # 컨테이너 이미지 빌드
├── docs/ko/                     # 한국어 문서
│   ├── development/             # 개발 가이드
│   └── prd/                     # 제품 요구사항 정의서
├── src/cloudforet/monitoring/   # 플러그인 소스 코드
│   ├── api/plugin/              # gRPC API 정의
│   ├── service/                 # 비즈니스 로직 계층
│   ├── manager/                 # 리소스 관리 계층
│   ├── connector/               # OCI API 연결 계층
│   ├── model/                   # 데이터 모델 및 스키마
│   └── libs/                    # 공유 라이브러리
└── test/                        # 테스트 코드
    └── api/                     # API 테스트
```

---

## 입력 파라미터 (Input Parameters)

본 플러그인은 다양한 입력 파라미터를 통해 로그 모니터링 동작을 제어할 수 있습니다.

### **쿼리 파라미터**

로그 쿼리 요청에서 사용되는 파라미터입니다.

| 파라미터 | 타입 | 설명 | 예시 |
|----------|------|------|------|
| `start` | `timestamp` | 로그 검색 시작 시간 (ISO8601 형식) | `2024-01-01T00:00:00Z` |
| `end` | `timestamp` | 로그 검색 종료 시간 (ISO8601 형식, 시작에서 최대 14일) | `2024-01-02T00:00:00Z` |
| `query` | `object` | 쿼리 필터 및 옵션 | 아래 참조 |

#### **쿼리 객체 구조**
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

### **Secret Data 파라미터**

OCI API 인증을 위한 필수 정보입니다.

| 파라미터 | 타입 | 설명 | 예시 |
|----------|------|------|------|
| `user` | `string` | OCI 사용자 OCID | `ocid1.user.oc1..aaaaaaaa...` |
| `tenancy` | `string` | OCI 테넌시 OCID | `ocid1.tenancy.oc1..aaaaaaaa...` |
| `region` | `string` | 기본 리전 코드 | `us-ashburn-1` |
| `fingerprint` | `string` | API 키 지문 | `aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99` |
| `key_content` | `string` | Private Key 내용 (PEM 형식) | `-----BEGIN PRIVATE KEY-----\n...` |

### **query 옵션**

로그 쿼리에 사용할 수 있는 query 옵션 설명 입니다:

| query                             | 설명        | 예시 값                                                         |
|-----------------------------------|-----------|--------------------------------------------------------------|
| `filters.key`                     | 검색 키      | `data.resourceId`, `data.evnetName`                          |
| `filters.value`                   | 검색 키에 대한 값 | `ocid1.vnic.oc1.ap-seoul-1.abuwgxxxxxx`, `ListSubscriptions` |
| `region`                          | 지역        | `ap-seoul-1`, `us-ashburn-1`                                 |
| `size`                            | 페이지 수     | `1`, `10`                                                    |

### **시간 범위 제한**

- **최대 범위**: 쿼리당 14일
- **형식**: ISO8601 형식 (예: `2024-01-01T00:00:00Z`)
- **시간대**: UTC 시간대 권장

### **사용 예시**

#### **로그 쿼리**
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

### **파라미터 검증**

플러그인은 입력 파라미터에 대해 다음과 같은 검증을 수행합니다:

#### **시간 범위 검증**
- 시작 시간이 종료 시간보다 이전이어야 함
- 시간 범위가 14일을 초과할 수 없음
- 시간이 유효한 ISO8601 형식이어야 함

#### **쿼리 검증**
- 필터 키가 유효한 로그 내용 경로여야 함
- Size 파라미터는 양의 정수여야 함

#### **Secret Data 검증**
- 필수 필드: `user`, `tenancy`, `region`, `fingerprint`, `key_content`
- OCID 형식 검사: `ocid1.` 접두사로 시작해야 함
- Private Key 형식 검사: PEM 형식이어야 함

---

## Options

플러그인은 로그 모니터링 동작을 사용자 정의하기 위한 다양한 구성 옵션을 지원합니다. 이러한 옵션은 데이터 소스 생성 시 설정하거나 필요에 따라 업데이트할 수 있습니다.

---
