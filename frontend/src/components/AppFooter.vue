<template>
  <footer class="footer">
    <div class="container footer__inner">
      <div>
        <span class="material-icons" style="font-size:1rem; vertical-align:middle;">info</span>
        <span class="caption"> Demo tylko Frontend • Wersja: 0.0.1 </span>
      </div>
      <div class="caption">
        © {{ new Date().getFullYear() }} Budżet Planner
      </div>
    </div>
  </footer>
</template>

<script setup>
</script>

<style scoped>
.footer__inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
