<script setup lang="ts">
// Placeholder analytics/summary.
</script>

<template>
  <div class="page">
    <div>
      <h1 class="page-title">Аналитика</h1>
      <p class="muted" style="margin: 8px 0 0 0;">
        Прогресс учеников: средний балл, процент выполненных работ, динамика по заданиям.
      </p>
    </div>

    <div class="grid grid-cols-2">
      <div class="card">
        <div class="card-title">Средний балл (пример)</div>
        <div style="height: 180px; border: 1px dashed var(--border); border-radius: 12px; padding: 12px;">
          График будет здесь
        </div>
      </div>
      <div class="card">
        <div class="card-title">Выполнение заданий (пример)</div>
        <div style="height: 180px; border: 1px dashed var(--border); border-radius: 12px; padding: 12px;">
          Диаграмма/таблица будет здесь
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-title">Сводка по ученикам</div>
      <div style="overflow-x: auto;">
        <table class="table">
          <thead>
            <tr>
              <th>Ученик</th>
              <th>Средний балл</th>
              <th>Выполнено</th>
              <th>Прогресс</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Анна</td>
              <td>8.7</td>
              <td><span class="chip chip-success">86%</span></td>
              <td class="muted">В росте</td>
            </tr>
            <tr>
              <td>Илья</td>
              <td>7.4</td>
              <td><span class="chip">74%</span></td>
              <td class="muted">Без изменений</td>
            </tr>
            <tr>
              <td>Маша</td>
              <td>9.1</td>
              <td><span class="chip chip-success">91%</span></td>
              <td class="muted">Стабильно</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

