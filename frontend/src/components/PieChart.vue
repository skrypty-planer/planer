<template>
  <div class="pie-chart-container">
    <svg :width="size" :height="size" viewBox="-1.25 -1.25 2.5 2.5" style="transform: rotate(-90deg)">
      <circle
        v-for="(segment, index) in segments"
        :key="index"
        r="1"
        :stroke="segment.color"
        :stroke-width="strokeWidth"
        fill="none"
        :stroke-dasharray="`${segment.percentage / 100 * circumference} ${circumference}`"
        :stroke-dashoffset="-segment.offset / 100 * circumference"
        opacity="0.9"
      />
    </svg>
    <div class="pie-legend">
      <div v-for="(item, index) in data" :key="item.category" class="legend-item">
        <span class="legend-color" :style="{ backgroundColor: colors[index % colors.length] }"></span>
        <span class="legend-label">{{ item.category }}</span>
        <span class="legend-value">{{ item.amount }} zł ({{ item.percentage }}%)</span>
      </div>
    </div>
    <div v-if="data.length === 0" class="pie-empty">
      Brak danych
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CategoryBreakdown } from '../services/api'

const props = defineProps<{
  data: CategoryBreakdown[]
  size?: number
}>()

const size = props.size || 300
const strokeWidth = 0.5
const circumference = Math.PI * 2

const colors = [
  '#3E68A3', // primary
  '#A1C63A', // accent
  '#5a6c7d', // muted
  '#2d5080', // hover
  '#8bad31', // success variant
  '#6b8cc4', // lighter primary
  '#b8d158', // lighter accent
  '#4a566a', // darker muted
]

const segments = computed(() => {
  let currentOffset = 0
  // Calculate total value to normalize
  const totalValue = props.data.reduce((sum, item) => sum + item.percentage, 0)
  
  return props.data.map(item => {
    // Normalize percentage if total is not 100 (avoid division by zero)
    const normalizedPercentage = totalValue > 0 ? (item.percentage / totalValue) * 100 : 0
    const segment = {
      ...item,
      percentage: normalizedPercentage,
      offset: currentOffset,
      color: colors[props.data.indexOf(item) % colors.length]
    }
    currentOffset += normalizedPercentage
    return segment
  })
})
</script>

<style scoped>
.pie-chart-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

svg {
  max-width: 100%;
  height: auto;
}

.pie-legend {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-size: 0.9rem;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  font-weight: 500;
}

.legend-value {
  color: var(--text-muted);
  font-size: 0.85rem;
}

.pie-empty {
  text-align: center;
  padding: 2rem;
  color: var(--text-muted);
  font-size: 1rem;
}
</style>
