# 안전 관리 시스템 - 백엔드 서버

## 프로젝트 소개

안전 관리 시스템은 현장 작업자의 건강 및 안전 상태를 실시간으로 모니터링하는 웹/앱 기반 시스템입니다. 이 프로젝트는 온열질환 및 낙상 사고와 같은 안전 위험 요소를 사전에 감지하고 관리할 수 있도록 설계되었습니다.

## 프로젝트 구조

```
safety_management_system/
├── app.py                  # 메인 애플리케이션 진입점
├── config.py               # 설정 파일
├── requirements.txt        # 프로젝트 의존성
├── .gitignore              # Git 무시 파일
├── README.md               # 프로젝트 문서
├── migrations/             # 데이터베이스 마이그레이션
├── tests/                  # 테스트 케이스
│   ├── __init__.py
│   ├── test_auth.py        # 인증 엔드포인트 테스트
│   ├── test_main.py        # 메인 엔드포인트 테스트
│   ├── test_device.py      # 기기 관련 테스트
│   └── test_health.py      # 건강 데이터 테스트
└── app/                    # 애플리케이션 패키지
    ├── __init__.py         # Flask 앱 초기화
    ├── models/             # 데이터베이스 모델
    │   ├── __init__.py
    │   ├── employee.py     # 직원 및 관리자 모델
    │   ├── health.py       # 건강정보, 비상연락처, 이상징후 모델
    │   ├── device.py       # 기기, 기기관리, 고장 모델
    │   └── measurement.py  # 측정 데이터 모델
    ├── routes/             # API 라우트
    │   ├── auth.py         # 인증 라우트
    │   ├── employee.py     # 직원 정보 관리 라우트
    │   ├── dashboard.py    # 대시보드 라우트
    │   ├── device.py       # 기기 관리 라우트
    │   ├── health.py       # 건강 데이터 라우트
    │   └── anomaly.py      # 이상 징후 라우트
    ├── route_mobile/       # API(앱) 라우트
    │   ├── __init__.py
    │   └── auth.py         # 인증 라우트
    ├── utils/              # 유틸리티 함수
    │   ├── __init__.py
    │   ├── auth.py         # 인증 헬퍼
    │   ├── validators.py   # 입력 검증
    │   └── risk_calculator.py  # 위험도 계산 유틸리티
    └── schemas/            # 요청/응답 스키마
        ├── __init__.py
        ├── auth.py         # 인증 스키마
        ├── employee.py     # 직원 정보 스키마
        ├── device.py       # 기기 관련 스키마
        └── measurement.py  # 측정 데이터 스키마;
```

## 모듈 설명

### 핵심 모듈

* **app/models/** : 데이터베이스 모델을 정의합니다.
* `user.py`: 직원 정보 및 계정 관리
* `device.py`: 웨어러블 디바이스 정보
* `health_data.py`: 건강/생체 데이터
* `incident.py`: 사고 및 이상 징후 정보
* **app/routes/** : API 엔드포인트 정의
* `auth.py`: 회원가입, 로그인 등 인증 관련
* `mypage.py`: 개인 정보 관리
* `main.py`: 대시보드 데이터
* `bio.py`: 생체 데이터 API
* `worker.py`: 작업자 관리 API
* **app/utils/** : 유틸리티 함수
* `auth.py`: JWT 토큰 관리 등
* `validators.py`: 입력 데이터 검증
* **app/schemas/** : 요청/응답 데이터 형식 정의

### 핵심 파일

* **app.py** : 서버 실행 진입점
* **config.py** : 환경별 설정 관리
* **requirements.txt** : 필요 패키지 목록

## 기술 스택

* **백엔드** : Flask 2.2.3, Python 3.8+
* **데이터베이스** : SQLAlchemy, MySQL
* **인증** : JWT (Flask-JWT-Extended)
* **API 문서화** : Swagger/Flask-RESTful
* **개발 도구** : Docker, Git

## 설치 및 실행 방법

### 필수 요구사항

* Python 3.8 이상
* pip
* 가상 환경 (권장)

### 설치 과정

1. 저장소 클론

```bash
git clone https://github.com/사용자명/안전관리시스템.git
cd 안전관리시스템
```

2. 가상 환경 설정

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치

```bash
pip install -r requirements.txt
```

4. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 열어 필요한 환경 변수 설정
```

5. 데이터베이스 초기화

```bash
flask db init
flask db migrate -m "초기 마이그레이션"
flask db upgrade
```

6. 서버 실행

```bash
python app.py
```

## API 엔드포인트

### 인증 관련

* `POST /signup` - 새로운 직원(사용자) 등록
* `POST /login` - 로그인 처리

### 마이페이지

* `GET /mypage` - 직원 개인 정보 및 보호자 정보 조회
* `PUT /mypage` - 직원 개인 정보 및 보호자 정보 수정

### 메인 대시보드

* `GET /main/header` - 대시보드 헤더 정보
* `GET /main/heat_incident` - 온열질환 이상자 정보
* `GET /main/fall_incident` - 낙상 이상자 정보
* `GET /main/incident_total` - 이상자 총 인원
* `GET /main/device_status` - 기기 상태 정보
* `GET /main/weekly_heat_stats` - 주간 온열질환자 통계

### 작업자 현황

* `GET /bio/profile` - 작업자 프로필 정보
* `GET /bio/vital` - 작업자 생체 정보

## 개발자 정보

* 홍길동 - 백엔드 개발 (이메일@도메인.com)
* 김철수 - 프론트엔드 개발 (이메일@도메인.com)

## 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다. 자세한 내용은 LICENSE 파일을 참조하세요.
