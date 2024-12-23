import serial
from datetime import datetime

# 시리얼 포트와 속도 설정
ser = serial.Serial('COM3', 9600)

def parse_data(data):
    """시리얼 데이터를 파싱하여 딕셔너리로 변환"""
    parsed_data = {}
    for line in data.split("\n"):  # 여러 줄 데이터를 개별 라인으로 분리
        if ": " in line:  # ':' 구분자를 기준으로 키와 값 분리
            key, value = line.split(": ", 1)
            parsed_data[key.strip()] = value.strip()
    return parsed_data

collected_data = []  # 각 회차 데이터를 저장할 리스트
current_data = {}  # 현재 회차의 데이터를 저장할 딕셔너리

while True:
    raw_data = ser.readline().decode('utf-8').strip()  # 아두이노 데이터 읽기
    parsed = parse_data(raw_data)  # 데이터 파싱

    if parsed:  # 유효한 데이터인 경우
        current_data.update(parsed)  # 현재 회차 데이터에 추가
    else:  # 빈 줄을 만나면 회차 종료로 간주
        if current_data:  # 현재 회차 데이터가 비어있지 않으면
            # 현재 시각 추가
            current_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            collected_data.append(current_data)  # 리스트에 추가
            print(current_data)  # 추가된 데이터를 출력
        current_data = {}  # 새로운 회차를 위한 초기화
