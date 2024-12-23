# 작업자 안전 모니터링 시스템 - 데이터 처리 및 모델링

## 프로젝트 소개
이 프로젝트는 작업자의 안전 모니터링 시스템 개발을 위해 다양한 데이터 처리 및 모델링 기법을 실험한 Jupyter Notebook 파일들을 포함합니다. 각각의 노트북은 특정한 문제를 해결하거나 모델 성능을 개선하기 위한 방법론을 다룹니다.

## 파일 구성
1. **MLP_based_Binary_Classification.ipynb**
   - 데이터 전처리와 다층 퍼셉트론(Multi-Layer Perceptron)을 활용한 이진 분류 실험.
   - 주요 기능:
     - 데이터 전처리(공백 및 불필요한 문자열 제거).
     - MLP 모델 학습 및 평가.

2. **Binary_Classification.ipynb**
   - 은닉층 추가를 통한 이진 분류 정확도 향상.
   - 주요 기능:
     - 모델 구조 변경.
     - 모델 학습 및 성능 평가.

3. **LSTM.ipynb**
   - LSTM(Long Short-Term Memory) 모델을 활용한 실험.
   - 주요 기능:
     - 시계열 데이터를 다룰 수 있는 LSTM 모델 실험.

4. **Missing_Data_Handling.ipynb**
   - 결측 데이터 처리 기법을 다룸.
   - 주요 기능:
     - 결측 데이터 식별.
     - 결측치 처리 방법(평균, 중앙값 대체 등).

## 사용 방법
1. 각 Jupyter Notebook 파일을 다운로드하거나 클론합니다.
2. Python 3 및 Jupyter Notebook 환경을 설정합니다.
3. 노트북을 실행하여 각 실험을 재현하거나 사용자 데이터로 테스트합니다.

## 시스템 요구사항
- Python 3.10
- 주요 라이브러리: TensorFlow, NumPy, pandas, Matplotlib 등.

## 기여 방법
이 프로젝트에 기여하고 싶으신 경우, Pull Request를 보내주시거나 이슈를 등록해주세요.
