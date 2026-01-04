<template>
  <footer class="footer">
    <div class="container footer__inner">
      <div class="footer-left">
        <span class="material-icons" style="font-size:1rem; vertical-align:middle;">info</span>
        <span class="caption"> Demo tylko Frontend • Wersja: 0.0.2 </span>
      </div>
      <div class="caption footer-right">
        © {{ new Date().getFullYear() }} Budżet Planner
      </div>
    </div>
  </footer>
</template>

<script setup>
</script>

<style scoped>
.footer {
  padding: 2rem 0; /* Increased padding */
}
.footer__inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem; /* Add side padding */
}
</style>
