<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

function goLogin() {
  router.push('/login')
}

function goRegister() {
  router.push('/register')
}
</script>

<template>
  <div class="landing">
    <header class="topbar">
      <div class="topbar-inner">
        <div class="brand">
          <div class="brand-title">4tutor</div>
          <div class="brand-subtitle">Репетиторы и ученики</div>
        </div>

        <div style="display: flex; gap: 12px; align-items: center;">
          <button class="btn" type="button" @click="goLogin">Вход</button>
          <button class="btn btn-primary" type="button" @click="goRegister">
            Регистрация
          </button>
        </div>
      </div>
    </header>

    <div class="container">
      <div class="hero">
        <div class="hero-left">
          <div class="logo-mark" aria-hidden="true">
            <div class="logo-mark-inner">4</div>
          </div>

          <h1 class="page-title hero-title">
            Всё для репетитора:
            <span style="color: var(--primary);">ученики</span>, задания и календарь
          </h1>
          <p class="muted hero-subtitle" style="margin: 0;">
            4tutor помогает вести учеников, назначать домашние задания и автоматически напоминать о дедлайнах.
            Удобно на десктопе и мобилке.
          </p>

          <div class="hero-ctas">
            <button class="btn btn-primary" type="button" @click="goRegister">
              Регистрация для репетитора
            </button>
            <button class="btn" type="button" @click="goLogin">Вход</button>
          </div>

          <div class="hero-chips">
            <span class="chip chip-success">Группы учеников</span>
            <span class="chip chip-warning">Напоминания по дедлайнам</span>
            <span class="chip">Календарь занятий</span>
          </div>

          <div class="hero-mini">
            <div class="mini-item">
              <div class="mini-num">1</div>
              <div class="mini-text">
                Добавляйте учеников и распределяйте на индивидуальные/групповые
              </div>
            </div>
            <div class="mini-item">
              <div class="mini-num">2</div>
              <div class="mini-text">Создавайте задания и контролируйте статусы сдачи</div>
            </div>
            <div class="mini-item">
              <div class="mini-num">3</div>
              <div class="mini-text">Расписание и напоминания — без ручной рутины</div>
            </div>
          </div>
        </div>

        <div class="hero-right">
          <div class="hero-visual card">
            <div class="visual-top">
              <div class="chip chip-success">MVP UI</div>
              <div class="chip chip-warning">Нейтральные цвета</div>
            </div>

            <div class="visual-grid">
              <div class="visual-panel">
                <div class="card-title">Задания</div>
                <div class="visual-line" />
                <div class="visual-line" style="width: 86%;" />
                <div class="visual-badges">
                  <span class="chip chip-success">Выполнено</span>
                  <span class="chip chip-warning">Срок скоро</span>
                </div>
              </div>

              <div class="visual-calendar">
                <div class="card-title">Расписание</div>
                <div class="calendar-sim">
                  <div class="axis" />
                  <div class="cols">
                    <div class="col" v-for="i in 7" :key="i">
                      <div class="tick" />
                      <div class="tick" />
                      <div class="tick" />
                    </div>
                  </div>
                </div>
                <div class="visual-note muted">
                  Блоки занятий с подсказками типа занятия
                </div>
              </div>
            </div>

            <div class="visual-bottom">
              <div class="muted" style="font-weight: 700;">Соберите свой процесс за 10 минут</div>
              <div class="muted">дальше — только польза</div>
            </div>
          </div>
        </div>
      </div>

      <div class="features">
        <div class="feature-card card">
          <div class="feature-icon" aria-hidden="true">✓</div>
          <div>
            <div class="card-title">Управление учениками</div>
            <div class="muted">Индивидуальные и групповые занятия. Добавление и редактирование списка.</div>
          </div>
        </div>
        <div class="feature-card card">
          <div class="feature-icon" aria-hidden="true">⌁</div>
          <div>
            <div class="card-title">Расписание в стиле Google</div>
            <div class="muted">Время слева, дни сверху. Блоки занятий с подробностями по клику.</div>
          </div>
        </div>
        <div class="feature-card card">
          <div class="feature-icon" aria-hidden="true">⏰</div>
          <div>
            <div class="card-title">Напоминания по дедлайнам</div>
            <div class="muted">Предупреждения о “скоро” и “просрочено” без лишней тревоги.</div>
          </div>
        </div>
      </div>

      <div class="cta-bar card">
        <div>
          <div class="card-title" style="font-size: 18px;">Готовы начать?</div>
          <div class="muted">Подключайте учеников и ведите задания прямо в одном интерфейсе.</div>
        </div>
        <div class="hero-ctas" style="margin: 0;">
          <button class="btn" type="button" @click="goLogin">Вход</button>
          <button class="btn btn-primary" type="button" @click="goRegister">
            Регистрация
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.landing {
  position: relative;
}

.landing:before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 10% 20%, rgba(30, 58, 138, 0.14), transparent 45%),
    radial-gradient(circle at 80% 10%, rgba(245, 158, 11, 0.14), transparent 40%),
    radial-gradient(circle at 70% 70%, rgba(16, 185, 129, 0.12), transparent 40%),
    linear-gradient(180deg, rgba(249, 250, 251, 0.9), rgba(249, 250, 251, 1));
  pointer-events: none;
  z-index: -1;
}

.hero {
  position: relative;
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 18px;
  padding: 18px 0 4px 0;
}

.hero-left {
  padding: 8px 0;
}

.logo-mark {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(30, 58, 138, 0.15), rgba(16, 185, 129, 0.15));
  border: 1px solid rgba(30, 58, 138, 0.2);
  display: grid;
  place-items: center;
  margin-bottom: 12px;
}

.logo-mark-inner {
  font-weight: 900;
  color: var(--primary);
  font-size: 22px;
}

.hero-title {
  font-size: 44px;
  margin-bottom: 10px;
  letter-spacing: -0.03em;
}

.hero-subtitle {
  font-size: 16px;
  line-height: 1.6;
}

.hero-ctas {
  display: flex;
  gap: 12px;
  margin-top: 18px;
  flex-wrap: wrap;
}

.hero-chips {
  display: flex;
  gap: 10px;
  margin-top: 14px;
  flex-wrap: wrap;
}

.hero-mini {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 18px;
  max-width: 620px;
}

.mini-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.mini-num {
  width: 30px;
  height: 30px;
  border-radius: 12px;
  background: rgba(30, 58, 138, 0.08);
  border: 1px solid rgba(30, 58, 138, 0.18);
  color: var(--primary);
  font-weight: 900;
  display: grid;
  place-items: center;
}

.mini-text {
  color: var(--muted);
  font-weight: 700;
}

.hero-right {
  display: flex;
}

.hero-visual {
  width: 100%;
  border-radius: 20px;
  padding: 16px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 1));
}

.visual-top {
  display: flex;
  gap: 10px;
  justify-content: flex-start;
  margin-bottom: 14px;
}

.visual-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.visual-panel {
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 12px;
}

.visual-line {
  height: 10px;
  border-radius: 999px;
  background: rgba(229, 231, 235, 0.85);
  margin-top: 10px;
  width: 100%;
}

.visual-badges {
  display: flex;
  gap: 10px;
  margin-top: 12px;
  flex-wrap: wrap;
}

.visual-calendar {
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 12px;
}

.calendar-sim {
  display: grid;
  grid-template-columns: 48px 1fr;
  gap: 12px;
  align-items: start;
  margin-top: 8px;
}

.axis {
  width: 48px;
  border-right: 1px solid rgba(229, 231, 235, 0.8);
}

.cols {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 6px;
}

.col {
  border: 1px dashed rgba(229, 231, 235, 0.9);
  border-radius: 10px;
  padding: 8px;
  height: 150px;
  position: relative;
  overflow: hidden;
}

.tick {
  height: 12px;
  border-radius: 8px;
  background: rgba(30, 58, 138, 0.12);
  margin-top: 10px;
}

.visual-note {
  margin-top: 10px;
  font-weight: 700;
}

.visual-bottom {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.features {
  margin-top: 18px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.feature-card {
  padding: 16px;
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.feature-icon {
  width: 42px;
  height: 42px;
  border-radius: 16px;
  background: rgba(30, 58, 138, 0.08);
  border: 1px solid rgba(30, 58, 138, 0.18);
  color: var(--primary);
  display: grid;
  place-items: center;
  font-weight: 900;
  flex: 0 0 auto;
}

.cta-bar {
  margin-top: 14px;
  padding: 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

@media (max-width: 1100px) {
  .hero {
    grid-template-columns: 1fr;
  }
  .features {
    grid-template-columns: 1fr;
  }
}
</style>

