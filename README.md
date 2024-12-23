# 작업자 안전 모니터링 시스템 - 하드웨어 기반 구현

## 프로젝트 소개  
이 프로젝트는 작업자의 안전 모니터링 시스템을 하드웨어 기반으로 구현하기 위해 설계된 코드와 연결 방식을 포함합니다. MLX90614 온도 센서, DHT-22 습도 센서, GSR 센서, SZH-HWS0001 센서 등을 활용하여 작업자의 신체 상태를 실시간으로 모니터링하고 데이터를 처리하는 시스템입니다.  

## 파일 구성  
1. **arduino.ino**  
   - 아두이노에서 센서를 제어하고 데이터를 수집하는 코드.  
   - 주요 기능:  
     - MLX90614 적외선 온도 센서를 사용한 주변 및 객체 온도 측정.  
     - DHT-22 센서를 사용한 습도 및 온도 데이터 수집.  
     - GSR 및 SZH-HWS0001 센서를 사용한 전도율 및 스트레스 지표 데이터 측정.  
     - 시리얼 통신을 통해 데이터를 송신.  

2. **parsing.py**  
   - 시리얼 데이터를 수신하고 파싱하여 처리하는 Python 스크립트.  
   - 주요 기능:  
     - 시리얼 통신으로 수신된 데이터를 딕셔너리 형태로 변환.  
     - 각 데이터 수집 회차에 타임스탬프 추가.  
     - 수집된 데이터를 출력 및 저장 가능.  

## 사용 방법  
1. **하드웨어 설정**  
   - MLX90614, DHT-22, GSR 센서, SZH-HWS0001 센서를 아두이노 우노에 연결합니다.  
   - 각 센서는 아두이노 코드에서 정의된 핀에 연결해야 합니다(A0, A1, A2 등).  

2. **소프트웨어 설정**  
   - 아두이노 IDE를 사용하여 `arduino.ino` 파일을 업로드합니다.  
   - Python 환경에서 `serial_parsing.py` 스크립트를 실행합니다.  
   - 아두이노가 데이터를 송신하면 Python 스크립트가 데이터를 수신 및 처리합니다.  

3. **실시간 데이터 모니터링**  
   - 시리얼 모니터 또는 Python 스크립트를 통해 실시간으로 수집된 데이터를 확인합니다.  
   - 데이터는 타임스탬프와 함께 저장되어 후속 분석에 활용 가능합니다.  

## 시스템 요구사항  
- 하드웨어: 아두이노 우노, MLX90614, DHT-22, GSR 센서, SZH-HWS0001.  
- 소프트웨어:  
  - 아두이노 IDE  
  - Python 3.10 이상  
  - 주요 라이브러리: pyserial, datetime  

## 기여 방법  
이 프로젝트에 기여하고 싶으신 경우, 센서 추가 제안 또는 데이터 처리 방식 개선을 포함한 Pull Request를 보내주시거나 이슈를 등록해주세요.  

이 시스템은 데이터 기반 분석 및 작업자 안전 모니터링에 실질적인 도움을 제공할 수 있는 하드웨어와 소프트웨어의 융합 솔루션입니다.
