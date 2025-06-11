<template>
  <div class="heat-map-container" ref="mapContainer">
    <v-card class="map-card">
      <v-card-title class="map-title">
        <h2>현장 지도</h2>
        <div class="legend">
          <div class="legend-item">
            <div class="legend-marker danger"></div>
            <span>위험</span>
          </div>
          <div class="legend-item">
            <div class="legend-marker caution"></div>
            <span>주의</span>
          </div>
        </div>
      </v-card-title>
      
      <v-card-text class="map-content">
        <div id="map" class="map-container"></div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/leaflet.markercluster.js';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';

// 기본 마커 아이콘 설정
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

export default {
  name: 'HeatMap',
  props: {
    heatRiskWorkers: {
      type: Array,
      default: () => []
    },
    fallRiskWorkers: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      map: null,
      markersCluster: null,
      resizeObserver: null,
      lastTableHeight: 0, // 마지막으로 확인한 테이블 높이
      heightSyncInterval: null // 인터벌 ID 저장
    };
  },
  computed: {
    // 모든 위험자 데이터를 합쳐서 지도용 데이터로 변환
    allRiskWorkers() {
      const allWorkers = [];
      
      // 온열질환 위험자 추가
      this.heatRiskWorkers.forEach(worker => {
        if (worker.location && worker.location.latitude && worker.location.longitude) {
          allWorkers.push({
            emp_id: worker.emp_id,
            name: worker.name,
            temperature: worker.vitals?.temperature || 0,
            heart_rate: worker.vitals?.heart_rate || 0,
            risk_level: worker.risk_level,
            latitude: worker.location.latitude,
            longitude: worker.location.longitude,
            type: 'heat' // 온열질환 타입
          });
        }
      });
      
      // 낙상 위험자 추가
      this.fallRiskWorkers.forEach(worker => {
        if (worker.location && worker.location.latitude && worker.location.longitude) {
          allWorkers.push({
            emp_id: worker.emp_id,
            name: worker.name,
            temperature: worker.vitals?.temperature || 0,
            heart_rate: worker.vitals?.heart_rate || 0,
            risk_level: worker.risk_level,
            latitude: worker.location.latitude,
            longitude: worker.location.longitude,
            type: 'fall' // 낙상 타입
          });
        }
      });
      
      return allWorkers;
    }
  },
  mounted() {
    this.initMap();
    this.addMarkersToMap();
    
    // 높이 동기화는 지도 초기화 후에 설정
    this.$nextTick(() => {
      setTimeout(() => {
        this.setupHeightSyncing();
      }, 1000);
    });
  },
  watch: {
    // props가 변경될 때마다 마커 업데이트
    allRiskWorkers: {
      handler() {
        this.addMarkersToMap();
      },
      deep: true
    }
  },
  methods: {
    initMap() {
      // DOM 엘리먼트 확인
      const mapElement = document.getElementById('map');
      if (!mapElement) {
        console.error('지도 DOM 엘리먼트가 존재하지 않습니다.');
        return;
      }
      
      // 기존 지도가 있다면 제거
      if (this.map) {
        this.map.remove();
      }
      
      try {
        // 지도 초기화 (목포 중심, 적당한 줌 레벨)
        this.map = L.map('map').setView([34.912787, 126.437601], 17);
        
        // 최소/최대 줌 레벨 제한 설정
        this.map.setMinZoom(15); // 최소 줌
        this.map.setMaxZoom(19); // 최대 줌
        
        // OpenStreetMap 타일 레이어 추가
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
          attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
        
        // 마커 클러스터 그룹 생성
        this.markersCluster = L.markerClusterGroup({
          chunkedLoading: true,
          maxClusterRadius: 50
        });
        
        this.map.addLayer(this.markersCluster);
        
        console.log('지도 초기화 완료');
      } catch (error) {
        console.error('지도 초기화 중 오류:', error);
      }
    },
    
    // 테이블과 지도 높이 동기화 설정
    setupHeightSyncing() {
      // 테이블 컨테이너 찾기
      const tablesContainer = document.querySelector('.tables-container');
      if (!tablesContainer) {
        console.log('테이블 컨테이너를 찾을 수 없습니다.');
        return;
      }
      
      // ResizeObserver로 테이블 높이 변화 감지
      if (typeof ResizeObserver !== 'undefined') {
        this.resizeObserver = new ResizeObserver(() => {
          this.syncMapHeight();
        });
        this.resizeObserver.observe(tablesContainer);
      }
      
      // 초기 높이 동기화
      this.syncMapHeight();
      
      // 주기적 체크 (5초마다, 더 긴 간격으로)
      this.heightSyncInterval = setInterval(() => {
        this.syncMapHeight();
      }, 5000);
    },
    
    // 지도 높이를 테이블 높이와 맞춤
    syncMapHeight() {
      const tablesContainer = document.querySelector('.tables-container');
      const mapContainer = this.$refs.mapContainer;
      
      if (tablesContainer && mapContainer) {
        const tableHeight = tablesContainer.offsetHeight;
        
        // 높이가 변경되지 않았으면 실행하지 않음
        if (this.lastTableHeight === tableHeight) {
          return;
        }
        
        // 최소 높이 560px 보장
        const newHeight = Math.max(560, tableHeight);
        
        // 지도 컨테이너 높이 동적 조정
        mapContainer.style.height = `${newHeight}px`;
        
        // 마지막 높이 업데이트
        this.lastTableHeight = tableHeight;
        
        // Leaflet 지도 리사이즈
        if (this.map) {
          this.$nextTick(() => {
            setTimeout(() => {
              this.map.invalidateSize();
            }, 100);
          });
        }
        
        console.log(`지도 높이 조정: ${newHeight}px (테이블: ${tableHeight}px)`);
      }
    },
    
    addMarkersToMap() {
      if (!this.map || !this.markersCluster) return;
      
      // 기존 마커들 제거
      this.markersCluster.clearLayers();
      
      // 데이터가 없으면 종료
      if (this.allRiskWorkers.length === 0) {
        console.log('표시할 위험자 데이터가 없습니다.');
        return;
      }
      
      console.log('지도에 마커 추가:', this.allRiskWorkers);
      
      this.allRiskWorkers.forEach(worker => {
        const lat = parseFloat(worker.latitude);
        const lng = parseFloat(worker.longitude);
        
        // 유효한 좌표인지 확인
        if (isNaN(lat) || isNaN(lng)) {
          console.warn(`유효하지 않은 좌표: ${worker.name} (${worker.latitude}, ${worker.longitude})`);
          return;
        }
        
        // 위험도에 따른 마커 색상 결정
        const markerColor = this.getMarkerColor(worker.risk_level);
        const customIcon = this.createCustomIcon(markerColor);
        
        // 마커 생성
        const marker = L.marker([lat, lng], { icon: customIcon });
        
        // 팝업 내용 생성
        const popupContent = `
          <div class="marker-popup">
            <h3>${worker.name} (${worker.emp_id})</h3>
            <div class="popup-info">
              <p><strong>타입:</strong> ${worker.type === 'heat' ? '온열질환' : '낙상'}</p>
              <p><strong>체온:</strong> ${worker.temperature}°C</p>
              <p><strong>심박수:</strong> ${worker.heart_rate} BPM</p>
              <p><strong>위험도:</strong> <span class="risk-${worker.risk_level === '위험' ? 'danger' : 'caution'}">${worker.risk_level}</span></p>
            </div>
          </div>
        `;
        
        marker.bindPopup(popupContent);
        
        // 클러스터에 마커 추가
        this.markersCluster.addLayer(marker);
      });
      
      // 모든 마커가 추가된 후, 마커들이 모두 보이도록 지도 범위 조정
      if (this.markersCluster.getLayers().length > 0) {
        // 마커들의 경계를 계산하여 지도 범위 설정
        const group = new L.featureGroup(this.markersCluster.getLayers());
        const bounds = group.getBounds();
        
        // 패딩을 추가하여 마커들이 화면 가장자리에 붙지 않도록 함
        this.map.fitBounds(bounds, {
          padding: [30, 30], // 상하좌우 30px 여백
          maxZoom: 17 // 최대 줌 레벨 제한
        });
      }
    },
    
    getMarkerColor(risk) {
      return risk === '위험' ? '#ff4444' : '#ffaa00';
    },
    
    createCustomIcon(color) {
      return L.divIcon({
        className: 'custom-marker',
        html: `
          <div class="marker-circle" style="background-color: ${color};">
            <div class="marker-inner"></div>
          </div>
        `,
        iconSize: [20, 20],
        iconAnchor: [10, 10],
        popupAnchor: [0, -10]
      });
    },
    
    // 데이터 새로고침 메서드 (외부에서 호출 가능)
    refreshData() {
      this.addMarkersToMap();
      this.syncMapHeight();
    }
  },
  
  beforeUnmount() {
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
    if (this.heightSyncInterval) {
      clearInterval(this.heightSyncInterval);
    }
    if (this.map) {
      this.map.remove();
    }
  }
};
</script>

<style src="../css/MapSection.css"></style>