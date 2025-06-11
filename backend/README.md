# 안전 관리 시스템 - 백엔드 서버

## 프로젝트 소개

안전 관리 시스템은 현장 작업자의 건강 및 안전 상태를 실시간으로 모니터링하는 웹/앱 기반 시스템입니다. 웨어러블 디바이스와 헬스커넥트 API를 통해 수집된 생체정보를 바탕으로 온열질환 및 낙상 사고와 같은 안전 위험 요소를 사전에 감지하고 관리할 수 있도록 설계되었습니다.

## 프로젝트 구조

```
backend/
├── app.py                  # 메인 애플리케이션 진입점
├── config.py               # 설정 파일
├── requirements.txt        # 프로젝트 의존성
├── .env                    # 환경 변수 파일
├── .gitignore              # Git 무시 파일
├── database/               # 데이터베이스 관련
│   ├── datafile/           # 데이터베이스 초기 데이터 저장 폴더
│   │   ├── admin.csv       # 관리자 목록
│   │   ├── device_measurement.csv  # 스마트 워치 측정 데이터
│   │   ├── device.csv      # 스마트 워치 목록
│   │   ├── emergency_contact.csv   # 비상 연락망 정보
│   │   ├── employee_attendance.csv # 직원 출퇴근 기록
│   │   ├── employee_health.csv     # 직원 건강 정보
│   │   ├── employee.csv    # 직원 인적 사항
│   │   ├── health_anomaly.csv      # 이상 징후 발생 기록
│   │   └── picture/        # 사진 파일
│   ├── create_schema.py    # MySQL 테이블 생성
│   └── create_table.py     # CSV 파일 테이블에 삽입
└── app/                    # 애플리케이션 패키지
    ├── __init__.py         # Flask 앱 초기화
    ├── model.py            # 데이터베이스 모델 (통합)
    ├── schema.py           # 공통 스키마 정의
    ├── web/                # 웹 관리자 인터페이스
    │   ├── views/          # 웹 컨트롤러 (블루프린트)
    │   │   ├── __init__.py         # 웹 블루프린트 통합
    │   │   ├── auth.py             # 웹 인증 컨트롤러
    │   │   ├── alert.py            # 알림로그 컨트롤러
    │   │   ├── employees.py        # 근로자현황 컨트롤러
    │   │   ├── safety.py           # 위험 근로자 현황 컨트롤러
    │   │   └── monitoring.py       # 대시보드 컨트롤러
    │   └── service/        # 비즈니스 로직 서비스 계층
    │       ├── __init__.py         # 웹 서비스 통합
    │       ├── auth_service.py     # 웹 인증 서비스
    │       ├── alert_service.py    # 알림로그 비즈니스 로직
    │       ├── employee_service.py # 근로자현황 비즈니스 로직
    │       ├── monitoring_service.py # 대시보드 비즈니스 로직
    │       └── safety_service.py   # 위험 근로자 비즈니스 로직
    ├── util/               # 공통 유틸리티
    │   ├── __init__.py             # 유틸 블루프린트 통합
    │   ├── util.py                 # 날씨 정보
    │   ├── auth.py                 # 토큰 쿼리 검증 및 계정 정보 변경 함수
    │   ├── time_utils.py           # 한국시간 변환 공용 유틸리티
    │   └── debug.py                # 디버깅용 개발자 함수
    └── mobile/             # 모바일 근로자 인터페이스
        ├── views/          # 모바일 컨트롤러 (블루프린트)
        │   ├── __init__.py         # 모바일 블루프린트 통합
        │   ├── auth.py             # 모바일 인증 컨트롤러
        │   ├── device.py           # 모바일 측정 컨트롤러
        │   └── profile.py          # 개인정보 수정 컨트롤러
        └── service/        # 비즈니스 로직 서비스 계층
            ├── __init__.py         # 모바일 서비스 통합
            └── auth_service.py     # 모바일 인증 서비스
```

## 아키텍처 설계

### MVC 패턴 적용

본 프로젝트는 **Model-View-Controller(MVC) 패턴**을 기반으로 한 **서비스 계층 아키텍처**를 적용하여 개발되었습니다:

#### 📁 Model Layer (`app/model.py`)
- 데이터베이스 모델 정의 (SQLAlchemy ORM)
- 데이터 구조 및 관계 정의

#### 🎯 Controller Layer (`app/web/views/`, `app/mobile/views/`)
- HTTP 요청/응답 처리
- 라우팅 및 인증 처리
- 서비스 계층 호출

#### 🔧 Service Layer (`app/web/service/`, `app/mobile/service/`)
- **핵심 비즈니스 로직 처리**
- 데이터베이스 쿼리 및 조작
- 복잡한 데이터 변환 로직
- 에러 처리 및 유효성 검증

#### 🛠 Utility Layer (`app/util/`)
- 공통 유틸리티 함수
- 시간 변환, 인증, 디버깅 등

### 서비스 계층 상세

#### 웹 관리자 서비스 (`app/web/service/`)

- **AuthService**: 관리자 인증 및 권한 관리
- **AlertService**: 건강 이상징후 데이터 처리 및 상태 관리
- **EmployeeService**: 직원 정보 조회 및 출근 상태 관리
- **MonitoringService**: 대시보드 모니터링 데이터 통합 처리
- **SafetyService**: 위험도별 직원 분류 및 안전 관리

#### 모바일 앱 서비스 (`app/mobile/service/`)

- **AuthService**: 모바일 근로자 인증 관리

### 장점

1. **코드 재사용성**: 비즈니스 로직을 서비스 계층으로 분리하여 여러 컨트롤러에서 재사용 가능
2. **유지보수성**: 각 계층의 책임이 명확히 분리되어 수정 및 확장이 용이
3. **테스트 용이성**: 서비스 계층을 독립적으로 테스트 가능
4. **확장성**: 새로운 기능 추가 시 기존 코드에 미치는 영향 최소화

## 모듈 설명

### 핵심 모듈

**app/model.py**: 통합 데이터베이스 모델

- `Employee`: 직원 기본정보 및 계정 관리
- `Admin`: 관리자 권한 설정
- `Device`: 웨어러블 디바이스 관리
- `DeviceManagement`: 직원 출입 기록 (EMPLOYEE_ATTENDANCE)
- `DeviceMeasurement`: 센서 측정 데이터 (생체정보, 위치, 가속도 등)
- `EmployeeHealth`: 직원 건강 상태 정보
- `EmergencyContact`: 비상연락처
- `HealthAnomaly`: 건강 이상 징후 기록 및 처리 상태 관리
- `TokenBlocklist`: JWT 토큰 블랙리스트

**app/web/**: 웹 관리자 인터페이스

- **Views (Controllers)**:
  - `auth.py`: 웹 관리자 인증 (로그인, 로그아웃)
  - `monitoring.py`: 대시보드 및 실시간 모니터링
  - `employees.py`: 근로자 현황 및 생체정보 조회
  - `alert.py`: 알림로그 관리 (건강 이상징후 처리)
  - `safety.py`: 위험 근로자 현황 모니터링

- **Services (Business Logic)**:
  - `auth_service.py`: 관리자 인증 비즈니스 로직
  - `alert_service.py`: 건강 이상징후 데이터 처리 로직
  - `employee_service.py`: 직원 정보 및 출근 상태 처리 로직
  - `monitoring_service.py`: 대시보드 통합 데이터 처리 로직
  - `safety_service.py`: 위험도별 직원 분류 및 안전 관리 로직

**app/mobile/**: 모바일 앱 인터페이스

- **Views (Controllers)**:
  - `auth.py`: 모바일 근로자 인증 (로그인, 로그아웃)
  - `profile.py`: 개인정보 수정 (마이페이지 관리)
  - `device.py`: 디바이스 측정 데이터 처리 (센서 데이터 수집)

- **Services (Business Logic)**:
  - `auth_service.py`: 모바일 인증 비즈니스 로직

**app/schema.py**: 요청/응답 스키마 정의 (Marshmallow)

**app/util/**: 공통 유틸리티 함수들

- `auth.py`: JWT 토큰 검증 및 계정 관리
- `time_utils.py`: 한국시간 변환 및 시간대 처리 공용 함수
- `util.py`: 날씨 API 연동
- `debug.py`: 개발용 디버깅 도구

## 기술 스택

- **백엔드**: Flask 2.3+, Python 3.11+
- **아키텍처**: MVC 패턴 + 서비스 계층
- **데이터베이스**: SQLAlchemy, MariaDB
- **인증**: JWT (Flask-JWT-Extended)
- **검증**: Marshmallow
- **시간대 처리**: pytz (한국시간 KST 자동 변환)
- **개발 도구**: Docker, Git

## 설치 및 실행 방법

### 필수 요구사항

- Python 3.11.12
- MySQL 서버
- pip 및 가상환경

### 설치 과정

**1. 저장소 클론 및 이동**

```bash
git clone https://github.com/swscy3/MindPark.git
cd backend
```

**2. 가상 환경 설정**

```bash
python -m venv myenv
source myenv/bin/activate  # Windows: myenv\Scripts\activate
```

**3. 의존성 설치**

```bash
pip install -r requirements.txt
```

**4. 환경 변수 설정 (.env 파일 생성)**

```env
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_EXPIRES=3600
DEV_DATABASE_URL=mysql+pymysql://username:password@localhost:3306/database_name
FLASK_DEBUG=1

WHETHER_API_KEY=your-weather-api-key-here
WHETHER_API_URL=http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst

NX=51
NY=69
```

**5. 데이터베이스 초기화**

```bash
# MySQL 스키마 생성
python database/create_schema.py

# 초기 데이터 삽입
python database/create_table.py
```

**6. 서버 실행**

```bash
python app.py
```

서버는 `http://localhost:5000`에서 실행됩니다.

## API 엔드포인트

### 웹 관리자 인터페이스 (`/api/web`)

#### 인증

- `POST /auth/login` - 웹 관리자 로그인
- `POST /auth/logout` - 웹 관리자 로그아웃

#### 모니터링 대시보드

- `GET /monitoring/dashboard/stream` - 대시보드 실시간 스트림 (SSE)

#### 알림 관리

- `GET /alert/anomalies/stream` - 건강 이상징후 실시간 스트림 (SSE)
- `GET /alert/anomalies/detail` - 건강 이상징후 상세 조회
- `POST /alert/anomalies/update` - 건강 이상징후 상태 업데이트

#### 위험 직원 관리

- `GET /safety/danger-employees/stream` - 위험 직원 현황 스트림 (SSE)
- `GET /safety/caution-employees/stream` - 주의 직원 현황 스트림 (SSE)

#### 직원 관리

- `GET /emp/list/stream` - 직원 목록 스트림 (SSE)
- `GET /emp/<emp_id>/detail` - 특정 직원 상세 정보

### 모바일 앱 인터페이스 (`/api/mobile`)

#### 인증

- `POST /auth/login` - 모바일 근로자 로그인
- `POST /auth/logout` - 모바일 근로자 로그아웃

#### 프로필 관리

- `GET /profile/mypage` - 마이페이지 조회
- `PUT /profile/mypage` - 마이페이지 수정
- `POST /profile/mypage` - 마이페이지 업데이트

#### 디바이스 데이터

- `POST /device/measurement` - 센서 측정 데이터 전송

### 유틸리티 (`/api/util`)

- `GET /weather` - 날씨 정보 조회
- `POST /change-password` - 비밀번호 변경

### 기타

- **디버그 엔드포인트**: `/api/debug/*` - 개발용 디버깅 도구들
- **정적 파일**: `/static/*`, `/uploads/pictures/*` - 파일 서빙
- **프론트엔드**: `/`, `/<path>` - Vue.js SPA 라우팅

## 주요 기능

### 1. 실시간 모니터링

- 웨어러블 디바이스를 통한 생체정보 수집
- 헬스커넥트 API 연동
- 온열질환 및 낙상 위험도 실시간 계산

### 2. 관리자 대시보드

- 현장 작업자 현황 실시간 확인
- 사고 발생 현황 및 통계
- 디바이스 상태 모니터링

### 3. 모바일 앱 연동

- 작업자 개인정보 관리
- 실시간 알림 시스템
- 생체정보 전송 및 모니터링

### 4. 보안 및 안정성

- JWT 기반 인증 시스템
- 토큰 블랙리스트 관리
- 관리자-사용자 권한 분리
- 한국시간(KST) 자동 변환으로 일관된 시간 데이터 제공

## 개발 환경

### 디버그 도구

개발 시 다음 엔드포인트를 활용할 수 있습니다:

```bash
# 디버그용 토큰 발급
curl http://localhost:5000/api/debug/get-token

# JWT 테스트
curl -H "Authorization: Bearer <token>" http://localhost:5000/api/debug/jwt-test

# 등록된 라우트 확인
curl http://localhost:5000/api/debug/routes
```

## 배포 시 주의사항

1. **디버그 엔드포인트 제거**: `/api/debug/*` 경로 비활성화
2. **환경 변수 보안**: 운영 환경에서 적절한 시크릿 키 사용
3. **HTTPS 적용**: JWT 토큰 보안을 위한 HTTPS 필수
4. **데이터베이스 백업**: 정기적인 백업 및 복구 계획

## 라이센스

이 프로젝트는 MIT License 하에 배포됩니다.

## 프로젝트 정보

이 프로젝트는 캡스톤 디자인 프로젝트로 개발되었습니다.