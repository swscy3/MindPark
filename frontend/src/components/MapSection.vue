<template>
    <div class="map-section">
      <h3>현장 지도</h3>
      <div class="map-container">
        <!-- 지도 컨테이너 -->
        <div class="construction-map">
          <!-- 건설 현장 지도 레이아웃 -->
          <div class="map-grid">
            <!-- 구역 표시 -->
            <div class="map-area area-a">A 구역</div>
            <div class="map-area area-b">B 구역</div>
            <div class="map-area area-c">C 구역</div>
            <div class="map-area area-d">D 구역</div>
            
            <!-- 작업자 위치 표시 (나중에 동적으로 변경) -->
            <div class="worker-marker" style="top: 30%; left: 25%;" title="신정우">W1</div>
            <div class="worker-marker" style="top: 45%; left: 65%;" title="박지은">W2</div>
            <div class="worker-marker" style="top: 70%; left: 40%;" title="김준호">W3</div>
            
            <!-- 위험 지역 표시 -->
            <div class="danger-zone" style="top: 40%; left: 60%; width: 15%; height: 15%;"></div>
          </div>
          
          <!-- 지도 범례 -->
          <div class="map-legend">
            <div class="legend-item">
              <span class="worker-dot"></span> 작업자
            </div>
            <div class="legend-item">
              <span class="danger-dot"></span> 위험 지역
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'MapSection',
    data() {
      return {
        workers: [
          { id: 'W1', name: '신정우', position: { top: 30, left: 25 } },
          { id: 'W2', name: '박지은', position: { top: 45, left: 65 } },
          { id: 'W3', name: '김준호', position: { top: 70, left: 40 } }
        ],
        dangerZones: [
          { id: 'D1', position: { top: 40, left: 60, width: 15, height: 15 } }
        ]
      };
    },
    methods: {
      loadMap() {
        console.log('지도 로딩 완료');
        // 실제 프로젝트에서는 여기서 지도 초기화 및 데이터 로딩 작업을 수행
      },
      updateWorkerPositions(workers) {
        console.log('작업자 위치 업데이트:', workers);
        // 실제 프로젝트에서는 작업자 위치를 업데이트하는 로직
      }
    }
  }
  </script>
  
  <style src="../css/MapSection.css"></style>