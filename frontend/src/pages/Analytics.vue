<template>
  <section>
    <!-- Unified Balance Chart -->
    <div class="card">
      <div class="chart-header">
        <h3 style="margin:0;">Bilans</h3>
        <div class="buttons">
            <button class="kafel" :class="{ active: currentPeriod === 'yearly' }" @click="currentPeriod = 'yearly'">Rok</button>
            <button class="kafel" :class="{ active: currentPeriod === 'halfYearly' }" @click="currentPeriod = 'halfYearly'">Pół roku</button>
            <button class="kafel" :class="{ active: currentPeriod === 'quarterly' }" @click="currentPeriod = 'quarterly'">Kwartał</button>
            <button class="kafel" :class="{ active: currentPeriod === 'monthly' }" @click="currentPeriod = 'monthly'">Miesiąc</button>
            <button class="kafel" :class="{ active: currentPeriod === 'weekly' }" @click="currentPeriod = 'weekly'">Tydzień</button>
        </div>
      </div>
      
      <div class="chart-container">
         <div class="y-axis">
            <span>Bilans (zł)</span>
        </div>
        <div class="chart-bars">
            <div v-for="(label, i) in currentChartData.labels" :key="label + i" class="bar-group-single" :title="`${label}: ${currentChartData.data[i]} zł`">
                <div class="bar-value" :class="currentChartData.data[i] >= 0 ? 'text-income' : 'text-expense'">
                    {{ formatValue(currentChartData.data[i]) }}
                </div>
                <div 
                    class="bar" 
                    :class="currentChartData.data[i] >= 0 ? 'bar--income' : 'bar--expense'" 
                    :style="{ height: toHeight(Math.abs(currentChartData.data[i])) }"
                ></div>
                <div class="x-label" v-if="shouldShowLabel(i, currentChartData.labels.length)">{{ formatLabel(label) }}</div>
            </div>
        </div>
      </div>
      <div class="caption" style="margin-top:2.5rem;">Oś X: Dni miesiąca • Oś Y: Wartość numeryczna w zł</div>
    </div>

    <!-- Średnie dzienne przychody i wydatki (linia) -->
    <div class="card" style="margin-top:1rem;">
      <h3 style="margin:0 0 .6rem;">Średnie dzienne: przychody i wydatki (Ostatni miesiąc)</h3>
      <div class="grid cols-2 daily-averages">
        <div class="kafel">
          <div class="caption">Średni dzienny przychód</div>
          <div class="stat__value stat__value--income">{{ charts.averages.avgDailyIncome }} zł</div>
        </div>
        <div class="kafel">
          <div class="caption">Średni dzienny wydatek</div>
          <div class="stat__value stat__value--expense">{{ charts.averages.avgDailyExpense }} zł</div>
        </div>
      </div>
    </div>

    <!-- Ranking kategorii z ostatnich 3 miesięcy -->
    <div class="card" style="margin-top:1rem;">
      <h3 style="margin:0 0 .6rem;">Ranking kategorii (wydatki, ostatnie 3 mies.)</h3>
      <div class="grid cols-3 ranking-grid">
        <div class="kafel" v-for="r in charts.ranking" :key="r.category">
          <div class="caption">{{ r.category }}</div>
          <div class="stat__value stat__value--expense">{{ r.amount }} zł</div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { getCharts } from '../services/api'
import type { ChartsResponse, ChartData } from '../services/api'

const props = defineProps<{
  user: { id: string; [key: string]: any }
}>()

const charts = ref<ChartsResponse>({
  daily: { labels: [], income: [], expense: [], balance: [] },
  weekly: { labels: [], balance: [] },
  monthly: { labels: [], balance: [] },
  unified: {
    yearly: { labels: [], data: [] },
    halfYearly: { labels: [], data: [] },
    quarterly: { labels: [], data: [] },
    monthly: { labels: [], data: [] },
    weekly: { labels: [], data: [] },
  },
  averages: { avgDailyIncome: 0, avgDailyExpense: 0 },
  ranking: []
})

const currentPeriod = ref<'yearly' | 'halfYearly' | 'quarterly' | 'monthly' | 'weekly'>('monthly')

const currentChartData = computed<ChartData>(() => {
    return charts.value.unified[currentPeriod.value]
})

onMounted(async () => {
  charts.value = await getCharts(props.user.id)
})

function toHeight(v: number) {
  // Dynamic scaling based on max value in current dataset would be better, but fixed for now
  const max = Math.max(...currentChartData.value.data.map(Math.abs), 1000)
  const h = Math.round((v / max) * 180)
  return `${Math.max(2, Math.min(h, 180))}px`
}

function shouldShowLabel(index: number, total: number) {
    if (total <= 12) return true;
    if (total <= 31) return index % 5 === 0;
    return index % Math.ceil(total / 10) === 0;
}

function formatLabel(label: string) {
    if (label.startsWith('Month')) return label.replace('Month ', 'M');
    if (label.length > 10) return label.slice(5); // Remove year from date
    return label;
}

function formatValue(v: number) {
    return v > 0 ? `+${v}` : `${v}`
}
</script>

<style scoped>
.chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: .6rem;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.buttons {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
}
.buttons button.active {
    background-color: var(--primary);
    color: white;
    border-color: var(--primary);
}

.chart-container {
    display: flex;
    align-items: flex-end;
    gap: 10px;
    padding-bottom: 20px; /* Space for x-labels */
}

.y-axis {
    writing-mode: vertical-rl;
    transform: rotate(180deg);
    text-align: center;
    font-size: 0.8rem;
    color: #666;
    height: 220px;
}

.chart-bars {
  display: flex;
  justify-content: space-around;
  align-items: end;
  height: 220px;
  width: 100%;
  border-bottom: 1px solid #eee;
  border-left: 1px solid #eee;
  padding-top: 20px;
}
.bar-group-single {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: center;
  height: 100%;
  position: relative;
  flex: 1;
  margin: 0 2px;
}
.bar {
  width: 100%;
  background: #ccc;
  border-radius: 3px 3px 0 0;
  min-width: 4px;
}
.bar-value {
    font-size: 0.6rem;
    margin-bottom: 2px;
    writing-mode: vertical-rl;
    transform: rotate(180deg);
}
.text-income { color: var(--success); }
.text-expense { color: var(--danger); }

.x-label {
    position: absolute;
    bottom: -25px;
    font-size: 0.7rem;
    color: #666;
    white-space: nowrap;
}
.bar--income { background: #c8e6c9; border: 1px solid #81c784; }
.bar--expense { background: #ffcdd2; border: 1px solid #e57373; }

.stat__value {
  font-size: 1.2rem;
  font-weight: 600;
}
.stat__value--income { color: var(--success); }
.stat__value--expense { color: var(--danger); }

/* RWD */
@media (max-width: 768px) {
    .chart-header {
        flex-direction: column;
        align-items: flex-start;
    }
    .daily-averages.grid.cols-2 {
        grid-template-columns: 1fr;
    }
    .ranking-grid.grid.cols-3 {
        grid-template-columns: 1fr;
    }
    .bar-value {
        display: none;
    }
}
</style>
