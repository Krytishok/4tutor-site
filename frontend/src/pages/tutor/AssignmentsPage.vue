<script setup lang="ts">
// Placeholder assignments management.
</script>

<template>
  <div class="page">
    <div>
      <h1 class="page-title">Задания</h1>
      <p class="muted" style="margin: 8px 0 0 0;">
        Создавайте домашние задания для учеников и отслеживайте сдачу/проверку.
      </p>
    </div>

    <div class="card">
      <div class="row">
        <div>
          <div class="card-title">Создание задания</div>
          <div class="muted">MVP: интерфейс, позже подключим типы проверок и файлы</div>
        </div>
        <button class="btn btn-primary" type="button" disabled>
          Создать задание
        </button>
      </div>
    </div>

    <div class="card">
      <div class="card-title">Список заданий</div>
      <div style="overflow-x: auto;">
        <table class="table">
          <thead>
            <tr>
              <th>Название</th>
              <th>Ученик</th>
              <th>Срок</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Тест по алгебре №1</td>
              <td>Анна</td>
              <td>сегодня</td>
              <td><span class="chip chip-success">Сдано</span></td>
            </tr>
            <tr>
              <td>Упражнения по русскому</td>
              <td>Илья</td>
              <td>завтра</td>
              <td><span class="chip">Не сдано</span></td>
            </tr>
            <tr>
              <td>Сочинение (план)</td>
              <td>Маша</td>
              <td>вчера</td>
              <td><span class="chip chip-danger">Просрочено</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

