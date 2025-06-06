<template>
  <div class="heat-map-container">
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
import axios from 'axios';

// 기본 마커 아이콘 설정
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

export default {
  name: 'HeatMap',
  data() {
    return {
      map: null,
      markersCluster: null,
      heatData: {
        heat_name: [],
        heat_temp: [],
        heat_hr: [],
        heat_risk: [],
        heat_incident_lat: [],
        heat_incident_lng: []
      }
    };
  },
  mounted() {
    this.initMap();
    this.loadHeatData();
  },
  methods: {
    initMap() {
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
    },
    
    async loadHeatData() {
      try {
        // 실제 API 호출 시 사용
        // const response = await axios.get('/api/heat-data');
        // this.heatData = response.data;
        
        // 테스트 데이터 - 적당한 거리로 배치
        this.heatData = {
          heat_name: ["김철수", "이영희", "박민수", "최순자"],
          heat_temp: ["38.2", "37.9", "39.1", "37.5"],
          heat_hr: ["120", "115", "130", "110"],
          heat_risk: ["위험", "주의", "위험", "주의"],
          heat_incident_lat: [34.912787, 34.913500, 34.912200, 34.913200],
          heat_incident_lng: [126.437601, 126.438200, 126.437000, 126.438500]
        };
        
        this.addMarkersToMap();
      } catch (error) {
        console.error('데이터 로딩 실패:', error);
      }
    },
    
    addMarkersToMap() {
      // 기존 마커들 제거
      this.markersCluster.clearLayers();
      
      const dataLength = this.heatData.heat_name.length;
      
      for (let i = 0; i < dataLength; i++) {
        const lat = parseFloat(this.heatData.heat_incident_lat[i]);
        const lng = parseFloat(this.heatData.heat_incident_lng[i]);
        const name = this.heatData.heat_name[i];
        const temp = this.heatData.heat_temp[i];
        const hr = this.heatData.heat_hr[i];
        const risk = this.heatData.heat_risk[i];
        
        // 위험도에 따른 마커 색상 결정
        const markerColor = this.getMarkerColor(risk);
        const customIcon = this.createCustomIcon(markerColor);
        
        // 마커 생성
        const marker = L.marker([lat, lng], { icon: customIcon });
        
        // 팝업 내용 생성
        const popupContent = `
          <div class="marker-popup">
            <h3>${name}</h3>
            <div class="popup-info">
              <p><strong>체온:</strong> ${temp}°C</p>
              <p><strong>심박수:</strong> ${hr} BPM</p>
              <p><strong>위험도:</strong> <span class="risk-${risk === '위험' ? 'danger' : 'caution'}">${risk}</span></p>
            </div>
          </div>
        `;
        
        marker.bindPopup(popupContent);
        
        // 클러스터에 마커 추가
        this.markersCluster.addLayer(marker);
      }
      
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
    
    // 데이터 새로고침 메서드
    refreshData() {
      this.loadHeatData();
    }
  },
  
  beforeUnmount() {
    if (this.map) {
      this.map.remove();
    }
  }
};
</script>

<style src="../css/MapSection.css"></style>