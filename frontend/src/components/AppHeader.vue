<template>
  <header class="app-bar">
    <div class="container app-bar__inner">
      <div class="app-bar__titles">
        <h1 class="title">Budżet Planner</h1>
        <p class="subtitle">Twój codzienny pomocnik w wydatkach</p>
      </div>

      <div class="user-tile">
        <img :src="user.avatarUrl" alt="avatar" class="avatar" />
        <div class="user-info">
          <span class="nickname">{{ user.nickname }}</span>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
defineProps({
  user: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.app-bar {
  background: #fff;
  border-bottom: 1px solid var(--border);
}
.app-bar__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: .75rem 0;
}
.app-bar__titles {
  text-align: center;
  flex: 1;
}
.title {
  font-size: 1.6rem;
  margin: 0;
  font-weight: 600;
}
.subtitle {
  margin: .15rem 0 0;
  font-size: .95rem;
  color: var(--muted);
}
.user-tile {
  display: flex;
  gap: .5rem;
  align-items: center;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: .4rem .6rem;
  background: #fff;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
}
.nickname {
  font-weight: 500;
}
</style>
