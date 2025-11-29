<template>
  <nav class="card nav-card">
    <div class="grid cols-3">
      <router-link
        to="/"
        class="kafel"
        :class="{ 'kafel--active': isActive('home') }"
      >1. Strona główna</router-link>

      <router-link
        to="/transactions"
        class="kafel"
        :class="{ 'kafel--active': isActive('transactions') }"
      >2. Transakcje</router-link>

      <router-link
        to="/analytics"
        class="kafel"
        :class="{ 'kafel--active': isActive('analytics') }"
      >3. Analityka</router-link>
    </div>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
const isActive = (name) => route.name === name
</script>

<style scoped>
.nav-card {
  margin-bottom: 1rem;
}
.kafel {
  text-align: center;
  font-weight: 500;
}
.kafel--active {
  /* lokalny test – wyróżnienie aktywnego kafelka */
  outline: 2px solid var(--primary);
}
</style>
