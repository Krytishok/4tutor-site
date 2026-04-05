<template>
  <div class="container">
    <div class="page">
      <h1 class="page-title">Страница не найдена</h1>
      <div class="card">
        <p class="muted" style="margin: 0 0 12px 0;">
          Проверьте ссылку или вернитесь на главную.
        </p>
        <button class="btn btn-primary" type="button" @click="$router.push('/login')">
          На вход
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// Uses $router from Vue Router.
</script>

