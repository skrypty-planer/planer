<template>
  <header class="app-bar">
    <div class="container app-bar__inner">
      <div class="app-bar__titles">
        <h1 class="title">Budżet Planner</h1>
        <p class="subtitle">Twój codzienny pomocnik w wydatkach</p>
      </div>

      <div v-if="user" class="user-section">
        <div class="user-tile">
          <img :src="user.avatarUrl" alt="avatar" class="avatar" />
          <div class="user-info">
            <span class="nickname">{{ user.username }}</span>
          </div>
        </div>
        <button 
          v-if="user && user.id !== 'guest-user'"
          class="btn btn-secondary" 
          @click="$emit('edit-profile')" 
          title="Edytuj profil"
        >
          ✏️ Edytuj Profil
        </button>
        <button class="btn btn-danger" @click="$emit('logout')" title="Wyloguj">
          🚪 Wyloguj
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
defineProps({
  user: {
    type: Object,
    default: null
  }
})

defineEmits(['edit-profile', 'logout'])
</script>

<style scoped>
.app-bar {
  background: var(--card);
  border-bottom: 2px solid var(--border);
  box-shadow: 0 2px 4px var(--shadow);
}
.app-bar__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 0;
  gap: 1rem;
}
.app-bar__titles {
  text-align: center;
  flex: 1;
}
.title {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  margin: 0;
  font-weight: 700;
  color: var(--primary);
  letter-spacing: 0.5px;
}
.subtitle {
  margin: .25rem 0 0;
  font-size: 1rem;
  color: var(--text-muted);
  font-weight: 400;
}
.user-section {
  display: flex;
  gap: 1rem;
  align-items: center;
  margin-right: 2rem; /* Add spacing from right edge */
}
.user-tile {
  display: flex;
  gap: .6rem;
  align-items: center;
  border: 2px solid var(--border);
  border-radius: 10px;
  padding: .5rem .8rem;
  background: var(--card);
  height: 50px; /* Fixed height for alignment */
}
.avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid var(--primary);
}
.nickname {
  font-weight: 600;
  color: var(--text);
}
.btn {
  height: 50px; /* Match user-tile height */
  display: flex;
  align-items: center;
  padding: 0 1.2rem;
}

@media (max-width: 768px) {
  .app-bar__inner {
    flex-direction: column;
    gap: 1rem;
  }
  .user-section {
    margin-right: 0;
    flex-wrap: wrap;
    justify-content: center;
  }
  .title {
    font-size: 1.5rem;
  }
  .subtitle {
    font-size: 0.9rem;
  }
}
</style>
