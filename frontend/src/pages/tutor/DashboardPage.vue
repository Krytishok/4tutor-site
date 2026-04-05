<script setup lang="ts">
// Placeholder dashboard for tutor CRM.
</script>

<template>
  <div class="page">
    <div>
      <h1 class="page-title">Дашборд</h1>
      <p class="muted" style="margin: 8px 0 0 0;">
        Обзор учеников, заданий и прогресса (пока что заглушка).
      </p>
    </div>

    <div class="grid grid-cols-3">
      <div class="card">
        <div class="card-title">Ученики</div>
        <div style="font-size: 26px; font-weight: 900;">3</div>
        <div class="muted" style="margin-top: 6px;">Активных учеников</div>
      </div>
      <div class="card">
        <div class="card-title">Активные задания</div>
        <div style="font-size: 26px; font-weight: 900;">7</div>
        <div class="muted" style="margin-top: 6px;">Сроки в ближайшие дни</div>
      </div>
      <div class="card">
        <div class="card-title">Просрочки</div>
        <div style="font-size: 26px; font-weight: 900;">1</div>
        <div class="muted" style="margin-top: 6px;">Требуют внимания</div>
      </div>
    </div>

    <div class="card">
      <div class="row">
        <div>
          <div class="card-title">Напоминания и просрочки</div>
          <div class="muted">Скоро подключим API и отправку уведомлений</div>
        </div>
        <button class="btn btn-primary" type="button" disabled>
          Открыть центр
        </button>
      </div>

      <div class="muted" style="margin-top: 12px;">
        Пример: «Просрочено задание по русскому»
      </div>
    </div>
  </div>
</template>

