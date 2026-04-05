<script setup lang="ts">
// Placeholder student results/progress.
</script>

<template>
  <div class="page">
    <div>
      <h1 class="page-title">Результаты</h1>
      <p class="muted" style="margin: 8px 0 0 0;">
        Прогресс по заданиям и оценки (будет обновляться автоматически после проверки).
      </p>
    </div>

    <div class="grid grid-cols-2">
      <div class="card">
        <div class="card-title">Средний балл (пример)</div>
        <div style="font-size: 34px; font-weight: 900;">8.6</div>
        <div class="muted" style="margin-top: 6px;">за последние 30 дней</div>
      </div>
      <div class="card">
        <div class="card-title">Выполнено работ</div>
        <div style="height: 140px; border: 1px dashed var(--border); border-radius: 12px; padding: 12px;">
          График прогресса
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">Последние проверки</div>
      <div style="overflow-x: auto;">
        <table class="table">
          <thead>
            <tr>
              <th>Задание</th>
              <th>Оценка</th>
              <th>Комментарий</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Тест по алгебре №1</td>
              <td><span class="chip chip-success">9/10</span></td>
              <td class="muted">Хорошо! Есть небольшие пробелы</td>
            </tr>
            <tr>
              <td>Упражнения по русскому</td>
              <td><span class="chip">Проверяется</span></td>
              <td class="muted">Скоро будет ответ</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

