<template>
  <div class="app">
    <AppHeader :user="user" />

    <main class="container">
      <MenuNav />
      <router-view :user="user" />
    </main>

    <AppFooter />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppHeader from './components/AppHeader.vue'
import AppFooter from './components/AppFooter.vue'
import MenuNav from './components/MenuNav.vue'

// Symulacja zalogowanego użytkownika (docelowo dostarczane przez backend lub auth)
const user = ref({
  id: 'user-123',
  nickname: 'jan.kowalski',
  avatarUrl: 'https://i.pravatar.cc/80?img=12'
})
</script>

<style>
/***** Page-level minimal tweaks *****/
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.container {
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 1rem;
}
</style>