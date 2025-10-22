# SpaceONE OCI Logging 모니터링 플러그인 PRD

## 1. 개요

### 1.1 목적
기존 Google Cloud Logging 모니터링 플러그인을 Oracle Cloud Infrastructure (OCI) Logging 서비스로 전환하여 SpaceONE 플랫폼에서 OCI 로그 데이터를 수집하고 모니터링할 수 있도록 합니다.

### 1.2 범위
- OCI Logging 서비스에서 로그 엔트리 수집
- SpaceONE 콘솔에서 OCI 로그 데이터 표시 및 모니터링
- 기존 GCP 플러그인 구조를 최대한 활용한 효율적 전환

### 1.3 복잡도 분류
**SIMPLE_COLLECTOR** - 단일 OCI Logging 리소스 타입, 기본 list/get API 사용, 리전별 수집

## 2. 비즈니스 요구사항

### 2.1 사용자 스토리
**As a** SpaceONE 관리자  
**I want to** OCI 환경의 로그 데이터를 SpaceONE에서 모니터링하고  
**So that** OCI 인프라의 운영 상태와 보안 이벤트를 통합적으로 관리할 수 있습니다.

### 2.2 핵심 기능
- **로그 수집**: OCI Logging 서비스에서 감사 로그 및 애플리케이션 로그 수집
- **실시간 모니터링**: 수집된 로그를 SpaceONE 콘솔에서 실시간 조회
- **상세 정보 표시**: 로그 엔트리의 상세 정보를 팝업으로 표시
- **필터링**: 시간 범위, 리소스 타입, 로그 레벨별 필터링

## 3. 기술 요구사항

### 3.1 OCI API 연동

#### 3.1.1 사용 API 목록
- `logging_search_client.search_logs` - 로그 엔트리 검색 및 조회
- https://docs.oracle.com/en-us/iaas/api/#/en/logging-search/20190909/SearchResult/SearchLogs

#### 3.1.2 인증 방식
- **API 키 기반 인증**: OCI Config 파일 또는 환경변수 사용
- **인스턴스 프린시플**: OCI 인스턴스에서 실행 시 자동 인증
- **필요 IAM 정책**:
  - `LOG_CONTENT_READ`

### 3.2 SpaceONE 플러그인 아키텍처

#### 3.2.1 Service → Manager → Connector 3계층 구조
```
cloudforet.monitoring
├── service/
│   ├── data_source_service.py     # DataSource 비즈니스 로직
│   └── monitoring_service.py      # Log 비즈니스 로직
├── manager/
│   ├── data_source_manager.py     # DataSource 관리
│   ├── monitoring_manager.py      # Log 데이터 처리
│   └── metadata_manager.py        # UI 메타데이터 관리
├── connector/
│   └── oci_logging_connector.py   # OCI Logging API 연동
└── model/
    ├── event_model.py             # 로그 이벤트 모델
    └── log_model.py               # 로그 모델
```

#### 3.2.2 데이터 모델 (Schematics 기반)
```python
# 실제 OCI 로그 응답 구조 기반 데이터 모델
class OCILogEvent(Model):
    # 최상위 필드
    datetime = IntType()                 # Unix timestamp (밀리초)
    
    # logContent 전체 구조 (BaseType으로 유연하게 처리)
    log_content = BaseType(deserialize_from='logContent')  # 전체 로그 내용
    
    # 가공된 필드 (log_content에서 추출하여 변환)
    status_text = StringType(serialize_when_none=False)  # HTTP 상태 코드 → 텍스트 변환
    
    class Options:
        serialize_when_none = False

class OCILog(Model):
    results = ListType(ModelType(OCILogEvent), default=[])
```

### 3.3 수집 패턴
- **리전별 순차 수집**: OCI 리전별로 순차적 로그 수집
- **부분 실패 허용**: 개별 리소스 실패가 전체 수집에 영향 없음
- **페이징 처리**: 
  - **고정 페이지 크기**: 1000개 로그 엔트리/페이지 (고정)
  - **반복 횟수 제어**: `query.size`로 페이지 반복 횟수 지정
  - **최대 수집량**: `1000 × size` (예: 1000 × 5 = 5000개)
- **시간 범위 제한**: 최대 2주 범위 내 로그 수집

### 3.4 데이터 변환
- **HTTP 상태 코드 변환**: `log_content.data.response.status` → `status_text`
  - **200**: "OK"
  - **201**: "Created"
  - **202**: "Accepted"
  - **204**: "No Content"
  - **400**: "Bad Request"
  - **401**: "Unauthorized"
  - **403**: "Forbidden"
  - **404**: "Not Found"
  - **409**: "Conflict"
  - **412**: "Precondition Failed"
  - **422**: "Unprocessable Entity"
  - **429**: "Too Many Requests"
  - **500**: "Internal Server Error"
  - **502**: "Bad Gateway"
  - **503**: "Service Unavailable"
  - **504**: "Gateway Timeout"
  - **507**: "Insufficient Storage"
  - **기타**: "Unknown Status"

## 4. API 명세

### 4.1 DataSource 서비스

#### 4.1.1 init (플러그인 초기화)
```json
{
  "method": "DataSource.init",
  "parameters": {
    "options": {}
  },
  "response": {
    "metadata": {
      "view": {
        "table": {
          "layout": {
            "name": "oci-logging-table",
            "fields": [
              {
                "key": "event_name",
                "name": "Event Name",
                "type": "more",
                "options": {
                  "layout": {
                    "name": "Event Details",
                    "type": "popup",
                    "options": {
                      "layout": {
                        "type": "raw"
                      }
                    }
                  }
                }
              },
              {
                "key": "response_status", 
                "name": "Status code",
                "type": "enum"
              },
              {
                "key": "response_reason_phease", 
                "name": "Reason phrase",
                "type": "text"
              },
              {
                "key": "principal_name",
                "name": "User Name",
                "type": "text"
              },
              {
                "key": "time",
                "name": "Event Time",
                "type": "datetime"
              },
              {
                "key": "request_action",
                "name": "Action",
                "type": "Enum"
              },
              {
                "key": "message",
                "name": "Message",
                "type": "text"
              }
            ]
          }
        }
      },
      "required_keys": ["data.oci_logging"],
      "supported_providers": ["oci"]
    }
  }
}
```

#### 4.1.2 verify (인증 검증)
- secret_data 하위에 compartment_id 존재 시 compartment_id 사용 (부재 시 tenancy 사용)
```json
{
  "method": "DataSource.verify",
  "parameters": {
    "options": {},
    "secret_data": {
      "user": "ocid1.user.oc1...",
      "fingerprint": "aa:bb:cc:dd:ee:ff:...",
      "key_content": "-----BEGIN PRIVATE KEY-----\n...",
      "tenancy": "ocid1.tenancy.oc1...",
      "region": "us-ashburn-1",
      "compartment_id": "ocid1.compartment..." 
    }
  },
  "response": {}
}
```

### 4.2 Log 서비스

#### 4.2.1 list (로그 조회)
1.compartment_id 선택 규칙
  - secret_data 하위에 compartment_id가 존재하면 이를 사용
  - 없으면 secret_data 하위에 tenancy 값을 사용

2.region 선택 규칙
  - 요청(request) 값의 query 필드 안에 region이 존재하면 이를 사용
  - 없으면 secret_data 필드 안의 region 값을 사용

3.페이지 처리 규칙
  - 요청(request) 값의 query 필드 안에 size가 존재하면 해당 값만큼 페이지 반복
  - 없으면 기본 1회 조회

4.Search Logs 쿼리 변환 규칙
  - filters 리스트는 OR 조건으로 변환
  - 각 filter 내부 labels는 AND 조건으로 변환

```json
{
  "method": "Log.list",
  "parameters": {
    "options": {},
    "secret_data": {
      "user": "ocid1.user.oc1...",
      "fingerprint": "aa:bb:cc:dd:ee:ff:...",
      "key_content": "-----BEGIN PRIVATE KEY-----\n...",
      "tenancy": "ocid1.tenancy.oc1...",
      "region": "us-ashburn-1",
      "compartment_id": "ocid1.compartment..." 
    },
    "query": {
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
    "start": "2023-10-16T00:00:00Z",
    "end": "2023-10-16T23:59:59Z"
  },
  "response": {
    "results": [
      {
        "datetime": 1760956873812,
        "status_text": "Not Found",
        "log_content": {
          "data": {
            "additionalDetails": {
              "X-Real-Port": 00000
            },
            "availabilityDomain": "AD1",
            "compartmentId": "ocid1.compartment.oc1..aaaaaaaaxxxxx",
            "compartmentName": "aramco-dev",
            "definedTags": {
              "Oracle-Tags": {
                "CreatedBy": "faas",
                "CreatedOn": "2025-10-20T10:41:06.042Z"
              }
            },
            "eventGroupingId": "6276a4cde6acc.../B246174ED544E5B3C.../C021845A2CCE...",
            "eventName": "UpdateVnic",
            "freeformTags": {},
            "identity": {
              "authType": "resource",
              "callerId": null,
              "callerName": null,
              "consoleSessionId": null,
              "credentials": "ST$...",
              "ipAddress": "10.0.14.207",
              "principalId": "ocid1.fnapp.oc1.ap-seoul-1.amaaaaaae4qxxxxx",
              "principalName": null,
              "tenantId": "ocid1.tenancy.oc1..aaaaaaaauezddhh22xxxxx",
              "userAgent": "Oracle-GoSDK/65.84.0 (linux/arm64; go/go1.23.0 4493 X:boringcrypto)"
            },
            "message": "UpdateVnic failed",
            "request": {
              "action": "PUT",
              "headers": {
                "Accept": ["*/*"],
                "Accept-Encoding": ["gzip"],
                "Authorization": ["Signature version=\"1\",..."],
                "Content-Length": ["105"],
                "Content-Type": ["application/json"],
                "Date": ["Mon, 20 Oct 2025 10:41:13 GMT"]
              },
              "id": "6276a4cde6acc66e4f3....",
              "parameters": {},
              "path": "/20160918/vnics/ocid1.vnic.oc1.ap-seoul-1.abuw..."
            },
            "resourceId": "ocid1.vnic.oc1.ap-seoul-1.abuw...",
            "response": {
              "headers": {
                "Connection": ["close"],
                "Content-Length": ["111"],
                "Content-Type": ["application/json"],
                "Date": ["Mon, 20 Oct 2025 10:41:13 GMT"]
              },
              "message": null,
              "payload": {},
              "responseTime": "2025-10-20T10:41:13.814Z",
              "status": "404"
            },
            "securityAttributes": {},
            "stateChange": {
              "current": null,
              "previous": null
            },
            "systemTags": {}
          },
          "dataschema": "2.0",
          "id": "a632-c2a-495-a38d-4dfxxx",
          "oracle": {
            "compartmentid": "ocid1.compartment.oc1..aaaaaaaaxxxxx",
            "ingestedtime": "2025-10-20T10:41:21.464Z",
            "loggroupid": "_Audit",
            "tenantid": "ocid1.tenancy.oc1..aaaaaaaauezddhh22xxxxx"
          },
          "source": "",
          "specversion": "1.0",
          "time": "2025-10-20T10:41:13.812Z",
          "type": "com.oraclecloud.virtualNetwork.UpdateVnic"
        }
      }
    ]
  }
}
```

## 5. UI 메타데이터 정의

### 5.1 테이블 필드 구성
```python
# OCI 로그 구조 기반 메타데이터 (logContent 중심)
metadata_fields = [
    MoreField.data_source('Event Name', 'log_content.data.eventName', options={
        'layout': {
            'name': 'Event Details',
            'type': 'popup',
            'options': {
                'layout': {
                    'type': 'raw'  # log_content 전체를 JSON 형태로 표시
                }
            }
        }
    }),
    EnumDyField.data_source('Status code', 'log_content.data.response.status', default_badge={
        'green.500': ['200', '201', '202', '204'],           # 성공 응답 (2xx)
        'coral.500': ['400', '401', '403', '404', '409', '412', '422', '429'],  # 클라이언트 오류 (4xx)
        'red.500': ['500', '502', '503', '504', '507']       # 서버 오류 (5xx)
    }),
    TextDyField.data_source('Status Text', 'status_text'),
    TextDyField.data_source('User Name', 'log_content.data.identity.principalName'),
    DateTimeDyField.data_source('Event Time', 'log_content.time'),
    EnumDyField.data_source('Action', 'log_content.data.request.action', default_badge={
         'indigo.500': ['GET'],                               # 조회 (파란색)
         'green.500': ['POST'],                               # 생성 (초록색)
         'yellow.500': ['PUT', 'PATCH'],                      # 수정 (노란색)
         'red.500': ['DELETE'],                               # 삭제 (빨간색)
         'gray.500': ['HEAD', 'OPTIONS', 'TRACE', 'CONNECT']  # 기타 (회색)
     }),
    TextDyField.data_source('Message', 'log_content.data.message')
]
```

### 5.2 팝업 상세 정보
- **팝업 제목**: "Event Details"
- **표시 방식**: Raw JSON 형태 (`type: "raw"`)
- **포함 데이터**: 로그 엔트리의 전체 `log_content` 객체를 JSON 형식으로 표시
- **구현 방식**: GCP 플러그인과 동일하게 `MoreField`의 `layout.type: "raw"` 사용

```python
MoreField.data_source('Event Name', 'log_content.data.eventName', options={
    'layout': {
        'name': 'Event Details',
        'type': 'popup',
        'options': {
            'layout': {
                'type': 'raw'  # JSON 형태로 log_content 전체 표시
            }
        }
    }
})
```

- **표시 내용**: `log_content` 전체 객체가 JSON 형태로 팝업에 표시됨
  - `data`: 이벤트 상세 정보 (eventName, compartmentId, identity, request, response 등)
  - `oracle`: Oracle 메타데이터 (tenantid, loggroupid, ingestedtime 등)  
  - `time`: 이벤트 발생 시간 (ISO 8601)
  - `type`: 이벤트 타입 (예: com.oraclecloud.virtualNetwork.UpdateVnic)
  - 기타 모든 필드들이 원본 구조 그대로 표시

## 6. 에러 처리

### 6.1 OCI API 오류 처리
- **401 Unauthorized**: 인증 정보 오류 → 사용자에게 인증 정보 재확인 요청
- **403 Forbidden**: 권한 부족 → 필요한 IAM 정책 안내
- **404 Not Found**: 리소스 없음 → 정상 처리 (빈 결과 반환)
- **429 Too Many Requests**: API 할당량 초과 → 재시도 로직 적용
- **500 Internal Server Error**: OCI 서비스 오류 → 재시도 후 실패 시 에러 로깅

### 6.2 SpaceONE Core 예외 사용
```python
# 개념적 에러 처리 구조
from spaceone.core.error import *

class OCILoggingError(ERROR_BASE):
    _message = 'OCI Logging API Error: {error_message}'

class OCIAuthenticationError(ERROR_AUTHENTICATION_FAILURE):
    _message = 'OCI Authentication Failed: {details}'
```

## 7. 성능 요구사항

### 7.1 성능 목표
- **로그 수집 완료 시간**: 리전당 평균 30초 이내
- **처리량**: 1,000개 로그 엔트리/분
- **응답 시간**: API 호출당 평균 2초 이내
- **메모리 사용량**: 최대 512MB

### 7.2 최적화 전략
- **배치 처리**: 
  - **고정 배치 크기**: 1,000개 로그 엔트리/배치 (고정)
  - **반복 제어**: `query.size`로 배치 반복 횟수 조절
  - **메모리 효율성**: 배치별 처리로 메모리 사용량 제한
- **캐싱**: 메타데이터 정보 캐싱으로 반복 API 호출 최소화
- **스트리밍**: 대용량 로그 데이터 스트리밍 처리
- **타임아웃 관리**: API 호출별 적절한 타임아웃 설정

## 8. 보안 요구사항

### 8.1 인증 정보 보안
- **민감정보 로깅 금지**: API 키, 개인키 등 민감정보 로그 제외
- **암호화 저장**: 인증 정보는 SpaceONE Secret 서비스에 암호화 저장
- **권한 최소화**: 필요한 최소 권한만 부여

### 8.2 데이터 보안
- **전송 암호화**: HTTPS를 통한 안전한 데이터 전송
- **로그 마스킹**: 개인정보 포함 로그 필드 마스킹 처리

## 9. 테스트 전략

### 9.1 단위 테스트
```python
# 개념적 테스트 구조
import unittest.mock as mock

class TestOCILoggingConnector(unittest.TestCase):
    @mock.patch('oci.logging.LoggingManagementClient')
    def test_list_logs(self, mock_client):
        # OCI API 모킹
        mock_response = mock.Mock()
        mock_response.data = [...]
        mock_client.return_value.search_logs.return_value = mock_response
        
        # 테스트 실행
        connector = OCILoggingConnector(**test_params)
        result = connector.list_log_entries(test_query)
        
        # 검증
        self.assertIsNotNone(result)
```

### 9.2 통합 테스트
- **OCI API 연동 테스트**: 실제 OCI 환경에서 API 호출 테스트
- **SpaceONE 통합 테스트**: SpaceONE 플랫폼과의 연동 테스트
- **에러 시나리오 테스트**: 다양한 오류 상황 시뮬레이션

### 9.3 성능 테스트
- **부하 테스트**: 대용량 로그 데이터 처리 성능 측정
- **스트레스 테스트**: 시스템 한계 상황에서의 안정성 검증

## 10. 배포 및 운영

### 10.1 배포 전략
- **단계적 배포**: 개발 → 스테이징 → 프로덕션 순차 배포
- **롤백 계획**: 문제 발생 시 기존 GCP 플러그인으로 즉시 롤백 가능

### 10.2 모니터링
- **수집 성능 메트릭**: 로그 수집 속도, 성공률, 오류율 모니터링
- **시스템 리소스**: CPU, 메모리, 네트워크 사용량 모니터링
- **알림 설정**: 임계치 초과 시 자동 알림

## 11. 참고 자료

### 11.1 OCI 문서
- [OCI Logging Service Overview](https://docs.oracle.com/en-us/iaas/Content/Logging/Concepts/loggingoverview.htm)
- [OCI Logging API Reference](https://docs.oracle.com/en-us/iaas/api/#/en/logging-search/20190909/SearchResult/SearchLogs)

### 11.2 SpaceONE 문서
- [SpaceONE Plugin Development Guide](https://spaceone-dev.gitbook.io/spaceone-developer-guide/)
- [SpaceONE Monitoring Plugin Architecture](https://github.com/spaceone-dev/plugin-monitoring-template)

### 11.3 인증 및 권한
- [OCI Authentication Methods](https://docs.oracle.com/en-us/iaas/Content/API/Concepts/sdk_authentication_methods.htm)
- [OCI IAM Policies for Logging](https://docs.oracle.com/en-us/iaas/Content/Identity/Reference/loggingpolicyreference.htm)

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 1.0 | 2023-10-16 | 초기 PRD 작성 | SpaceONE Team |

-