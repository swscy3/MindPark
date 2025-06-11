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
│   ├── datafile/                           # 데이터베이스 초기 데이터 저장 폴더
│   │   ├── admin.csv                       # 관리자 목록
│   │   ├── device_measurement.csv          # 스마트 워치 측정 데이터
│   │   ├── device.csv                      # 스마트 워치 목록
│   │   ├── emergency_contact.csv           # 비상 연락망 정보
│   │   ├── employee_attendance.csv         # 직원 출퇴근 기록
│   │   ├── employee_health.csv             # 직원 건강 정보
│   │   ├── employee.csv                    # 직원 인적 사항
│   │   ├── health_anomaly.csv              # 이상 징후 발생 기록
│   │   └── picture/        # 사진 파일
│   ├── create_schema.py       # MySQL 테이블 생성
│   └── create_table.py        # CSV 파일 테이블에 삽입
└── app/                    # 애플리케이션 패키지
    ├── __init__.py         # Flask 앱 초기화
    ├── model.py            # 데이터베이스 모델 (통합)
    ├── schema.py           # 공통 스키마 정의
    ├── web/                # 웹 관리자 인터페이스
    │   ├── views/          # 웹 블루프린트
    │   │   ├── __init__.py # 웹 블루프린트 통합
    │   │   ├── auth.py     # 웹 인증 블루프린트
    │   │   ├── bio.py      # 생체정보 블루프린트
    │   │   └── dashboard.py # 대시보드 블루프린트
    │   ├── schemas/        # 웹 스키마
    │   │   ├── __init__.py # 웹 스키마 통합
    │   │   ├── auth_schema.py # 웹 인증 스키마
    │   │   ├── bio_schema.py  # 생체정보 스키마
    │   │   └── dashboard_schema.py # 대시보드 스키마
    │   └── services/       # 비즈니스 로직
    │       ├── __init__.py # 웹 서비스 통합
    │       ├── auth_service.py    # 웹 인증 서비스
    │       ├── dashboard_service.py # 대시보드 서비스
    │       └── bio_service.py     # 생체정보 관련 서비스
    ├── util/               # 공통 유틸리티 라우트
    │   ├── __init__.py     # 유틸 블루프린트 통합
    │   ├── util.py         # 날씨 정보
    │   └── debug.py        # 디버깅용 개발자 함수
    └── mobile/             # 모바일 앱 인터페이스
        └── mobile.py       # 모바일 통합 라우트 (리팩토링 예정)
```

## 모듈 설명

### 핵심 모듈

* **app/model.py** : 통합 데이터베이스 모델

  * `Employee`: 직원 정보 및 계정 관리
  * `Admin`: 관리자 권한 관리
  * `Device`, `DeviceManagement`, `DeviceMeasurement`: 웨어러블 디바이스 관리 및 측정 데이터
  * `EmployeeHealth`, `EmergencyContact`: 건강 정보 및 비상연락처
  * `HealthAnomaly`: 건강 이상 징후 기록
  * `TokenBlocklist`: JWT 토큰 블랙리스트
* **app/web/** : 웹 관리자 인터페이스

  * `auth.py`: 관리자 로그인, 로그아웃, 직원 등록
  * `dashboard.py`: 대시보드 헤더, 온열질환 현황, 통계
  * `bio.py`: 작업자 프로필 및 생체정보 조회
  * `services/`: 비즈니스 로직 분리 (MVC 패턴)
* **app/mobile/** : 모바일 앱 인터페이스

  * `mobile.py`: 모바일 로그인, 마이페이지 관리
  * `mobile_health.py`: 기기 정보, 헬스커넥트 데이터, 알림
* **app/schema.py** : 요청/응답 스키마 정의 (Marshmallow)

## 기술 스택

* **백엔드** : Flask 2.3+, Python 3.11+
* **데이터베이스** : SQLAlchemy, MySQL
* **인증** : JWT (Flask-JWT-Extended)
* **검증** : Marshmallow
* **개발 도구** : Docker, Git

## 설치 및 실행 방법

### 필수 요구사항

* Python 3.11 이상
* MySQL 서버
* pip 및 가상환경

### 설치 과정

1. 저장소 클론 및 이동

```bash
git clone <repository-url>
cd backend
```

2. 가상 환경 설정

```bash
python -m venv myenv
source myenv/bin/activate  # Windows: myenv\Scripts\activate
```

3. 의존성 설치

```bash
pip install -r requirements.txt
```

4. 환경 변수 설정 (.env 파일 생성)

```bash
FLASK_DEBUG=1
JWT_SECRET_KEY=your-secret-key
DATABASE_URL=mysql://user:password@localhost/safety_db
WEATHER_API_URL=https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst
WEATHER_API_KEY=your-weather-api-key
NX=60
NY=127
```

5. 데이터베이스 초기화

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

6. 서버 실행

```bash
python app.py
```

서버는 `http://localhost:5000`에서 실행됩니다.

## API 엔드포인트

### 웹 관리자 인터페이스 (`/api/web`)

#### 인증

* `POST /auth/login` - 관리자 로그인
* `POST /auth/logout` - 관리자 로그아웃
* `POST /auth/signup` - 직원 등록 (관리자만)

#### 대시보드

* `GET /header` - 대시보드 헤더 정보
* `GET /heat_incident` - 온열질환 사고 정보
* `GET /heat_stats` - 온열질환 주간 통계
* `GET /incident_total` - 사고 총 인원
* `GET /device_status` - 디바이스 상태 현황
* `GET /workers` - 작업자 목록 (페이징, 검색, 정렬)

#### 생체정보

* `GET /bio/profile` - 작업자 프로필 조회
* `GET /bio/vital` - 작업자 생체정보 조회

### 모바일 앱 인터페이스 (`/api/mobile`)

#### 인증 및 정보 관리

* `POST /login` - 모바일 로그인
* `GET /mypage` - 마이페이지 조회
* `PUT /mypage` - 마이페이지 수정

#### 기기 및 건강 데이터

* `POST /device-info` - 기기 정보 전송
* `POST /health-data` - 헬스커넥트 생체정보 전송
* `POST /nearby-alert` - 주변 근로자 알림
* `GET /monitoring/today` - 오늘의 모니터링 데이터

### 유틸리티 (`/api/util`)

* `GET /weather` - 날씨 정보 조회

### 디버그 (`/api/debug`)

* `GET /test` - 서버 상태 테스트
* `GET /jwt-test` - JWT 토큰 테스트
* `GET /routes` - 등록된 라우트 목록
* `GET /get-token` - 디버그용 토큰 발급

## 주요 기능

### 1. 실시간 모니터링

* 웨어러블 디바이스를 통한 생체정보 수집
* 헬스커넥트 API 연동
* 온열질환 및 낙상 위험도 실시간 계산

### 2. 관리자 대시보드

* 현장 작업자 현황 실시간 확인
* 사고 발생 현황 및 통계
* 디바이스 상태 모니터링

### 3. 모바일 앱 연동

* 작업자 개인정보 관리
* 실시간 알림 시스템
* 생체정보 전송 및 모니터링

### 4. 보안

* JWT 기반 인증 시스템
* 토큰 블랙리스트 관리
* 관리자-사용자 권한 분리

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

이 프로젝트는 [라이센스명] 하에 배포됩니다.

---

## 문의

프로젝트 관련 문의사항이 있으시면 이슈를 등록하거나 아래 연락처로 문의해주세요.

* 개발팀: [이메일 주소]
* 프로젝트 이슈: [GitHub 이슈 링크]
