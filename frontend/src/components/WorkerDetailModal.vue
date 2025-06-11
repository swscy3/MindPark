<template>
  <div v-if="isVisible" class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <!-- 모달 헤더 -->
      <div class="modal-header">
        <div>
          <h2 class="modal-title">{{ worker?.name || '이름 없음' }}</h2>
          <p class="modal-subtitle">작업자 정보</p>
        </div>
        <!-- X 닫기 버튼 -->
        <button class="close-button" @click="closeModal">✕</button>
      </div>

      <!-- 모달 바디 -->
      <div class="modal-body">
        <!-- 프로필 섹션 -->
        <div class="profile-section">
          <div class="profile-image">
            <span>{{ (worker?.name || 'N').charAt(0) }}</span>
          </div>
          <div class="profile-info">
            <h3>{{ worker?.name || '이름 없음' }}</h3>
            <p><strong>성별:</strong> {{ worker?.gender || '미제공' }}</p>
            <p><strong>나이:</strong> {{ worker?.age || '미제공' }}</p>
          </div>
        </div>

        <!-- 정보 그리드 -->
        <div class="info-grid">
          <!-- 생체 정보 카드 -->
          <div class="info-card">
            <h4><span class="card-icon"></span>생체 정보</h4>
            <div class="info-item">
              <span class="info-label">심박수</span>
              <span class="info-value">
                <span v-if="worker?.heartRate && worker.heartRate !== '미측정'" class="status-good">
                  <span class="status-dot"></span>
                  {{ worker.heartRate }}bpm
                </span>
                <span v-else>미측정</span>
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">산소포화도</span>
              <span class="info-value">
                <span v-if="worker?.oxygenSaturation && worker.oxygenSaturation !== '미측정'" class="status-good">
                  <span class="status-dot"></span>
                  {{ worker.oxygenSaturation }}%
                </span>
                <span v-else>미측정</span>
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">체온</span>
              <span class="info-value">
                <span v-if="worker?.temperature && worker.temperature !== '미측정'" class="status-good">
                  <span class="status-dot"></span>
                  {{ worker.temperature }}°C
                </span>
                <span v-else>미측정</span>
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">걸음수</span>
              <span class="info-value">{{ worker?.steps && worker.steps !== '미측정' ? worker.steps + '보' : '미측정' }}</span>
            </div>
          </div>

          <!-- 디바이스 정보 카드 -->
          <div class="info-card">
            <h4><span class="card-icon"></span>디바이스 정보</h4>
            <div class="info-item">
              <span class="info-label">디바이스</span>
              <span class="info-value">{{ worker?.deviceLocation || '미연결' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">배터리</span>
              <span class="info-value">
                <span v-if="worker?.batteryLevel && worker.batteryLevel !== '미측정'" 
                      :class="getBatteryStatusClass(worker.batteryLevel)">
                  <span class="status-dot"></span>
                  {{ worker.batteryLevel }}%
                </span>
                <span v-else>미측정</span>
              </span>
            </div>
          </div>

          <!-- 위치 정보 카드 -->
          <div class="info-card">
            <h4><span class="card-icon"></span>위치 정보</h4>
            <div class="info-item">
              <span class="info-label">위도</span>
              <span class="info-value">{{ worker?.location?.latitude || '미측정' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">경도</span>
              <span class="info-value">{{ worker?.location?.longitude || '미측정' }}</span>
            </div>
          </div>

          <!-- 긴급연락처 카드 -->
          <div class="info-card">
            <h4><span class="card-icon"></span>긴급연락처</h4>
            <div class="info-item">
              <span class="info-label">이름</span>
              <span class="info-value">{{ worker?.emergencyContact?.name || '미제공' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">관계</span>
              <span class="info-value">{{ worker?.emergencyContact?.relation || '미제공' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">연락처</span>
              <span class="info-value">{{ worker?.emergencyContact?.phone || '미제공' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 모달 푸터 -->
      <div class="modal-footer">
        <button class="footer-button secondary" @click="closeModal">닫기</button>
        <button class="footer-button primary" @click="handleAction" 
                :disabled="!worker?.location?.latitude || !worker?.location?.longitude">위치 추적</button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false
  },
  worker: {
    type: Object,
    default: () => ({})
  }
});

const emit = defineEmits(['close']);

const closeModal = () => {
  emit('close');
};

const handleAction = () => {
  console.log('위치 추적 시작:', {
    latitude: props.worker?.location?.latitude,
    longitude: props.worker?.location?.longitude
  });
};

// 배터리 상태에 따른 CSS 클래스 반환
const getBatteryStatusClass = (batteryLevel) => {
  try {
    const level = parseInt(batteryLevel);
    if (level > 50) return 'status-good';
    if (level > 20) return 'status-warning';
    return 'status-danger';
  } catch (error) {
    return 'status-warning';
  }
};
</script>

<style src="../css/WorkerDetailModal.css"></style>