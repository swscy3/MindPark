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
  </div>
</template>

<script>
import { employeeData } from '../utils/eventBus.js'
import { watch } from 'vue'

export default {
  name: 'DeviceInfo',
  data() {
    return {
      deviceStats: {
        total: 0,
        active: 0,
        inactive: 0
      }
    }
  },
  mounted() {
    console.log('DeviceInfo 컴포넌트 마운트됨')
    console.log('초기 employeeData:', employeeData.value)
    
    // 초기 데이터 계산
    this.calculateStats()
    
    // 데이터 변경 감지
    watch(employeeData, (newData) => {
      console.log('employeeData 변경 감지:', newData)
      this.calculateStats()
    }, { deep: true })
  },
  methods: {
    calculateStats() {
      console.log('calculateStats 호출됨')
      const employees = employeeData.value
      console.log('현재 employees 데이터:', employees)
      
      if (employees && employees.length > 0) {
        const attendedCount = employees.filter(emp => emp.attendance_status === '출근중').length
        const absentCount = employees.filter(emp => emp.attendance_status === '미출근').length
        const totalCount = employees.length
        
        this.deviceStats = {
          total: totalCount,
          active: attendedCount,
          inactive: absentCount
        }
        
        console.log('장비 현황 업데이트:', {
          총직원: totalCount,
          출근중: attendedCount,
          미출근: absentCount
        })
      } else {
        console.log('직원 데이터가 없거나 빈 배열입니다.')
      }
    }
  }
}
</script>

<style src="../css/DeviceInfo.css"></style>