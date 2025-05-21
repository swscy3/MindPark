<template>
    <div class="device-info">
      <h3>장비 현황</h3>
      <div class="device-stats">
        <div class="stat-item">
          <div class="stat-label">총 장비</div>
          <div class="stat-value">{{ deviceStats.total || 0 }}개</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">활성디바이스</div>
          <div class="stat-value success">{{ deviceStats.active || 0 }}개</div>
        </div>
        <div class="stat-item">
          <div class="stat-label">비활성디바이스</div>
          <div class="stat-value warning">{{ deviceStats.inactive || 0 }}개</div>
        </div>
      </div>
      <button @click="$emit('navigate', 'devicemanagement')" class="btn-primary">장비 관리</button>
    </div>
  </template>
  
  <script>
  export default {
    name: 'DeviceInfo',
    props: {
      deviceStats: {
        type: Object,
        default: () => ({
          total: 0,
          active: 0,
          inactive: 0
        })
      }
    }
  }
  </script>
  
  <style src="../css/DeviceInfo.css"></style>