import { ref } from 'vue'

export const employeeData = ref([])

export const updateEmployeeData = (data) => {
  employeeData.value = data
}