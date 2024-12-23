#include <Wire.h>
#include <Adafruit_MLX90614.h>    // MLX90614 적외선 온도 센서
#include "DHT.h"                  // DHT-22 센서
#include <Arduino.h>

// 핀 정의
#define DHT_PIN A2        // DHT-22 센서 핀
#define GSR_PIN A0        // Grove-GSR 핀
#define HWS_PIN A1        // SZH-HWS0001 핀
#define DHT_TYPE DHT22    // DHT 센서 유형

// 센서 객체 초기화
Adafruit_MLX90614 mlx = Adafruit_MLX90614();
DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(9600);
  Wire.begin();

  // MLX90614 초기화
  if (!mlx.begin()) {
    Serial.println("MLX90614 초기화 실패!");
  } else {
    Serial.println("MLX90614 초기화 성공!");
  }

  // DHT 센서 초기화
  dht.begin();
}

void loop() {
  // MLX90614 온도 읽기
  float mlxAmbientTemp = mlx.readAmbientTempC();
  float mlxObjectTemp = mlx.readObjectTempC();
  Serial.print("MLX90614 주변 온도: ");
  Serial.print(mlxAmbientTemp);
  Serial.println(" °C");
  Serial.print("MLX90614 객체 온도: ");
  Serial.print(mlxObjectTemp);
  Serial.println(" °C");

  // GSR 값 읽기
  int gsrValue = analogRead(GSR_PIN);
  Serial.print("GSR 값: ");
  Serial.println(gsrValue);

  // SZH-HWS0001 값 읽기
  int hwsValue = analogRead(HWS_PIN);
  Serial.print("HWS 값: ");
  Serial.println(hwsValue);

  // DHT 센서 데이터 읽기
  float dhtTemp = dht.readTemperature();
  float dhtHumidity = dht.readHumidity();
  if (isnan(dhtTemp) || isnan(dhtHumidity)) {
    Serial.println("DHT 센서에서 데이터를 읽는 중 오류 발생!");
  } else {
    Serial.print("DHT 온도: ");
    Serial.print(dhtTemp);
    Serial.println(" °C");
    Serial.print("DHT 습도: ");
    Serial.print(dhtHumidity);
    Serial.println(" %");
  }

  Serial.println("");
  delay(5000); // 5초 대기
}
