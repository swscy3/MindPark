#include <Wire.h>
#include <Adafruit_MLX90614.h>    // MLX90614 적외선 온도 센서 라이브러리
#include "DHT.h"                  // DHT-22 센서 라이브러리
#include <Arduino.h>

// 핀 정의
#define DHT_PIN A2        // DHT-22 센서의 연결된 아날로그 핀
#define GSR_PIN A0        // Grove-GSR 센서의 연결된 아날로그 핀
#define HWS_PIN A1        // SZH-HWS0001 센서의 연결된 아날로그 핀
#define DHT_TYPE DHT22    // DHT 센서의 모델 정의 (DHT-22)


// 센서 객체 초기화
Adafruit_MLX90614 mlx = Adafruit_MLX90614();  // MLX90614 온도 센서 객체
DHT dht(DHT_PIN, DHT_TYPE);                   // DHT-22 온도 및 습도 센서 객체

void setup() {
  Serial.begin(9600);      // 시리얼 통신 시작 (속도: 9600 bps)
  Wire.begin();            // I2C 통신 시작

  // MLX90614 적외선 온도 센서 초기화
  if (!mlx.begin()) {
    Serial.println("MLX90614 초기화 실패!");  // 센서 초기화 실패 시 출력
  } else {
    Serial.println("MLX90614 초기화 성공!");  // 센서 초기화 성공 시 출력
  }

  // DHT-22 센서 초기화
  dht.begin();             // DHT 센서 초기화
}

void loop() {
  // MLX90614 온도 센서로부터 주변 온도 및 객체 온도 읽기
  float mlxAmbientTemp = mlx.readAmbientTempC();  // 주변 온도 (섭씨)
  float mlxObjectTemp = mlx.readObjectTempC();   // 객체 온도 (섭씨)
  Serial.print("MLX90614 주변 온도: ");
  Serial.print(mlxAmbientTemp);  // 주변 온도 출력
  Serial.println(" °C");
  Serial.print("MLX90614 객체 온도: ");
  Serial.print(mlxObjectTemp);   // 객체 온도 출력
  Serial.println(" °C");

  // GSR (전기 피부 반응) 센서 값 읽기
  int gsrValue = analogRead(GSR_PIN);  // 아날로그 핀에서 GSR 값 읽기
  Serial.print("GSR 값: ");
  Serial.println(gsrValue);   // GSR 값 출력

  // SZH-HWS0001 센서 값 읽기
  int hwsValue = analogRead(HWS_PIN);  // 아날로그 핀에서 HWS 값 읽기
  Serial.print("HWS 값: ");
  Serial.println(hwsValue);   // HWS 값 출력

  // DHT-22 센서로부터 온도와 습도 읽기
  float dhtTemp = dht.readTemperature();  // DHT 온도 읽기
  float dhtHumidity = dht.readHumidity(); // DHT 습도 읽기
  if (isnan(dhtTemp) || isnan(dhtHumidity)) {
    Serial.println("DHT 센서에서 데이터를 읽는 중 오류 발생!");  // 센서에서 값 읽을 때 오류 발생 시 출력
  } else {
    Serial.print("DHT 온도: ");
    Serial.print(dhtTemp);  // DHT 온도 출력
    Serial.println(" °C");
    Serial.print("DHT 습도: ");
    Serial.print(dhtHumidity);  // DHT 습도 출력
    Serial.println(" %");
  }

  Serial.println("");  // 데이터 구분을 위한 빈 줄 추가
  delay(5000);          // 5초 대기 후 반복
}
