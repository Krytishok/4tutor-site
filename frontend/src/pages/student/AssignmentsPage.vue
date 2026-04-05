<script setup lang="ts">
// Placeholder student view of assignments.
</script>

<template>
  <div class="page">
    <div>
      <h1 class="page-title">Мои задания</h1>
      <p class="muted" style="margin: 8px 0 0 0;">
        Получайте задания от репетитора и отправляйте ответы.
      </p>
    </div>

    <div class="card">
      <div class="card-title">Активные задания</div>
      <div style="overflow-x: auto; margin-top: 10px;">
        <table class="table">
          <thead>
            <tr>
              <th>Задание</th>
              <th>Предмет</th>
              <th>Срок</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Тест по алгебре №1</td>
              <td>Алгебра</td>
              <td>сегодня</td>
              <td><span class="chip chip-success">Сдано</span></td>
            </tr>
            <tr>
              <td>Упражнения по русскому</td>
              <td>Русский</td>
              <td>завтра</td>
              <td><span class="chip">Ожидает</span></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="muted" style="margin-top: 12px;">
        Скоро добавим загрузку файлов и отправку ответов.
      </div>
    </div>
  </div>
</template>

