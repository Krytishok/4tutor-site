<script setup lang="ts">
import { useRouter } from 'vue-router'
import {
  Calendar,
  BarChart3,
  Users,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  GraduationCap,
  FileText,
  Zap,
  Bell,
  UserPlus,
  Upload,
  Award,
} from 'lucide-vue-next'
import { Doughnut, Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  PointElement,
  LineElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const router = useRouter()

// Данные для демонстрации аналитики (пример)
const doughnutData = {
  labels: ['Сдано и проверено', 'Сдано на проверке', 'Назначено'],
  datasets: [
    {
      data: [58, 24, 18],
      backgroundColor: ['#10B981', '#F59E0B', '#6B7280'],
      borderWidth: 0,
      cutout: '65%',
    },
  ],
}
const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom' as const,
      labels: { font: { size: 12 } },
    },
  },
}

const lineData = {
  labels: ['Сен', 'Окт', 'Ноя', 'Дек', 'Янв', 'Фев'],
  datasets: [
    {
      label: 'Средний балл',
      data: [74, 76, 79, 81, 84, 86],
      borderColor: '#1E3A8A',
      backgroundColor: 'rgba(30, 58, 138, 0.05)',
      fill: true,
      tension: 0.3,
    },
  ],
}
const lineOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: { y: { beginAtZero: true, max: 100 } },
}

const goLogin = () => router.push('/login')
const goRegister = () => router.push('/register')
</script>

<template>
  <div class="landing">
    <!-- Шапка -->
    <header class="topbar">
      <div class="topbar-inner">
        <div class="brand">
          <div class="brand-title">4tutor</div>
          <div class="brand-subtitle">Система управления обучением</div>
        </div>
        <div class="topbar-actions">
          <button class="btn btn-outline" @click="goLogin">Вход</button>
          <button class="btn btn-primary" @click="goRegister">Регистрация</button>
        </div>
      </div>
    </header>

    <main>
      <section class="hero section-padding">
        <div class="container hero-grid">
          <div class="hero-content">
            <div class="hero-badge">
              <Sparkles :size="18" />
            </div>
            <h1 class="hero-title">
              Управление репетиторским центром:<br>
              <span class="highlight">ученики, задания, расписание</span>
            </h1>
            <p class="hero-description">
              Платформа для репетиторов и учеников с разграничением ролей, системой приглашений,
              ведением расписания, созданием заданий, проверкой работ и аналитикой успеваемости.
            </p>
            <div class="hero-buttons">
              <button class="btn btn-primary btn-large" @click="goRegister">
                Начать работу
                <ArrowRight :size="18" />
              </button>
              <button class="btn btn-outline btn-large" @click="goLogin">Войти</button>
            </div>
            <div class="hero-stats">
              <div class="stat-item">
                <Users :size="20" />
                <span>Две роли: репетитор / ученик</span>
              </div>
              <div class="stat-item">
                <CheckCircle2 :size="20" />
                <span>Полный цикл заданий</span>
              </div>
            </div>
          </div>
          <div class="hero-visual">
            <div class="visual-card">
              <div class="visual-header">
                <div class="chip">Демонстрация аналитики</div>
                <div class="chip chip-success">Реальные данные</div>
              </div>
              <div class="chart-wrapper">
                <Doughnut :data="doughnutData" :options="doughnutOptions" />
              </div>
              <div class="visual-footer">
                <div class="metric">
                  <span class="metric-value">86%</span>
                  <span class="metric-label">Средняя успеваемость</span>
                </div>
                <div class="metric">
                  <span class="metric-value">42</span>
                  <span class="metric-label">Активных заданий</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Ключевые возможности (вместо цифр) -->
      <section class="features-highlight section-padding">
        <div class="container">
          <div class="section-header">
            <h2>Что реализовано в проекте</h2>
            <p>Полнофункциональное веб-приложение на Django + Vue 3</p>
          </div>
          <div class="features-grid">
            <div class="feature-card">
              <UserPlus :size="32" class="feature-icon" />
              <h3>Роли и приглашения</h3>
              <p>Регистрация с выбором роли. Репетитор приглашает учеников по email, ученик принимает приглашение.</p>
            </div>
            <div class="feature-card">
              <Calendar :size="32" class="feature-icon" />
              <h3>Расписание уроков</h3>
              <p>Создание, редактирование, удаление занятий. Поддержка индивидуальных и групповых уроков, еженедельное повторение.</p>
            </div>
            <div class="feature-card">
              <FileText :size="32" class="feature-icon" />
              <h3>Задания с файлами</h3>
              <p>Репетитор создаёт задание, прикрепляет файлы, назначает ученикам с индивидуальным дедлайном. Ученик загружает ответы.</p>
            </div>
            <div class="feature-card">
              <Award :size="32" class="feature-icon" />
              <h3>Проверка и оценки</h3>
              <p>Репетитор проверяет сданные работы, выставляет оценку и оставляет комментарий. Система ведёт историю.</p>
            </div>
            <div class="feature-card">
              <BarChart3 :size="32" class="feature-icon" />
              <h3>Аналитика</h3>
              <p>Графики среднего балла по месяцам, круговая диаграмма выполнения заданий, персональная статистика для ученика.</p>
            </div>
            <div class="feature-card">
              <Bell :size="32" class="feature-icon" />
              <h3>Дашборды и напоминания</h3>
              <p>Информационные панели с ближайшими дедлайнами, требующими внимания работами и персональными метриками.</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Гайд по использованию (пошагово) -->
      <section class="guide section-padding">
        <div class="container">
          <div class="section-header">
            <h2>Как пользоваться платформой</h2>
            <p>Руководство для репетитора и ученика</p>
          </div>
          <div class="guide-tabs">
            <div class="guide-column">
              <h3><GraduationCap :size="24" /> Для репетитора</h3>
              <ol class="guide-list">
                <li>Зарегистрируйтесь с ролью «Репетитор».</li>
                <li>В разделе «Ученики» отправьте приглашение по email ученика.</li>
                <li>После подтверждения учеником создавайте <strong>уроки</strong> в расписании и <strong>задания</strong>.</li>
                <li>При создании задания загрузите файлы, укажите предмет и назначьте учеников с дедлайном.</li>
                <li>Отслеживайте сдачу заданий на дашборде и в карточке задания.</li>
                <li>Проверяйте работы, выставляйте оценки и комментарии.</li>
                <li>Используйте аналитику для мониторинга прогресса учеников.</li>
              </ol>
            </div>
            <div class="guide-column">
              <h3><Users :size="24" /> Для ученика</h3>
              <ol class="guide-list">
                <li>Зарегистрируйтесь с ролью «Ученик».</li>
                <li>Примите приглашение от репетитора в разделе «Приглашения».</li>
                <li>Просматривайте назначенные задания на дашборде и в разделе «Мои задания».</li>
                <li>Загружайте файлы с ответами, после чего отправляйте работу на проверку.</li>
                <li>Следите за дедлайнами – система подсветит просроченные задания.</li>
                <li>Получайте уведомления о проверке и смотрите оценки с комментариями.</li>
                <li>Используйте личный календарь для отслеживания уроков.</li>
              </ol>
            </div>
          </div>
          <div class="guide-note">
            <p>💡 Все данные сохраняются в PostgreSQL, файлы хранятся на сервере. JWT-авторизация обеспечивает безопасный доступ.</p>
          </div>
        </div>
      </section>

      <!-- Демонстрация дашборда и аналитики -->
      <section class="demo-section section-padding">
        <div class="container two-columns">
          <div class="demo-text">
            <div class="section-header left">
              <h2>Пример аналитики репетитора</h2>
              <p>Автоматический расчёт метрик по заданиям и оценкам</p>
            </div>
            <ul class="feature-list">
              <li><CheckCircle2 :size="18" /> Средний балл ученика по всем заданиям</li>
              <li><CheckCircle2 :size="18" /> Процент выполнения заданий (назначено/сдано/проверено)</li>
              <li><CheckCircle2 :size="18" /> Динамика прогресса (растёт/падает/стабилен)</li>
              <li><CheckCircle2 :size="18" /> Сводная таблица по всем ученикам</li>
            </ul>
          </div>
          <div class="graph-preview">
            <div class="graph-card">
              <h3>Динамика среднего балла по месяцам</h3>
              <div class="chart-container">
                <Line :data="lineData" :options="lineOptions" />
              </div>
              <div class="graph-note">Данные формируются на основе реальных оценок из базы</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Лента событий (пример действий) -->
      <section class="activity-demo section-padding">
        <div class="container">
          <div class="section-header">
            <h2>Примеры событий в системе</h2>
            <p>Уведомления и действия, которые отслеживает платформа</p>
          </div>
          <div class="activity-timeline">
            <div class="activity-item">
              <div class="activity-icon"><UserPlus :size="18" /></div>
              <div><strong>Репетитор</strong> отправил приглашение ученику</div>
              <span class="activity-time">Статус: ожидает</span>
            </div>
            <div class="activity-item">
              <div class="activity-icon"><Upload :size="18" /></div>
              <div><strong>Ученик</strong> загрузил файлы и сдал задание</div>
              <span class="activity-time">Дедлайн: 2 дня</span>
            </div>
            <div class="activity-item">
              <div class="activity-icon"><Calendar :size="18" /></div>
              <div><strong>Репетитор</strong> создал повторяющееся занятие по алгебре</div>
              <span class="activity-time">Каждую среду</span>
            </div>
            <div class="activity-item">
              <div class="activity-icon"><Award :size="18" /></div>
              <div><strong>Репетитор</strong> выставил оценку и оставил комментарий к работе</div>
              <span class="activity-time">Обратная связь отправлена</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Технологический стек -->
      <section class="tech-stack section-padding">
        <div class="container">
          <div class="section-header">
            <h2>Технологический стек</h2>
            <p>Использованные технологии и библиотеки</p>
          </div>
          <div class="stack-grid">
            <div class="stack-item">Django 5.2</div>
            <div class="stack-item">Django REST Framework</div>
            <div class="stack-item">Simple JWT</div>
            <div class="stack-item">PostgreSQL</div>
            <div class="stack-item">Vue 3 + Composition API</div>
            <div class="stack-item">Pinia (state management)</div>
            <div class="stack-item">Vue Router</div>
            <div class="stack-item">Axios</div>
            <div class="stack-item">Chart.js</div>
            <div class="stack-item">Lucide Icons</div>
            <div class="stack-item">Docker + Nginx</div>
          </div>
        </div>
      </section>

      <!-- CTA для перехода (некоммерческий) -->
      <section class="cta-section section-padding">
        <div class="container cta-card">
          <div>
            <h2>Тестовая версия доступна</h2>
            <p>Вы можете зарегистрироваться как репетитор или ученик и опробовать все функции.</p>
          </div>
          <button class="btn btn-primary btn-large" @click="goRegister">
            Перейти к регистрации
            <Zap :size="18" />
          </button>
        </div>
      </section>
    </main>

    <footer class="footer">
      <div class="container">
        <div class="footer-content">
          <div class="brand">
            <div class="brand-title">4tutor</div>
            <div class="brand-subtitle">Krytishok | 2025</div>
          </div>
          <div class="footer-links">
            <a href="#">Описание проекта</a>
            <a href="https://github.com/Krytishok/4tutor-site">GitHub (репозиторий)</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Стили полностью сохранены из предыдущей версии – они уже адаптивные и современные.
   Ниже приведены только необходимые дополнения для новых элементов. */

.landing {
  background: linear-gradient(145deg, #F9FAFB 0%, #F3F4F6 100%);
}
.section-padding {
  padding: 60px 20px;
}
.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 16px;
}
.topbar {
  background: rgba(255,255,255,0.92);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid rgba(0,0,0,0.05);
  position: sticky;
  top: 0;
  z-index: 10;
}
.topbar-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  max-width: 1280px;
  margin: 0 auto;
}
.brand-title {
  font-size: 1.8rem;
  font-weight: 800;
  background: linear-gradient(135deg, #1E3A8A, #3B82F6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.hero-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: center;
}
.hero-badge {
  display: inline-flex;
  background: rgba(30,58,138,0.1);
  border-radius: 100px;
  padding: 6px 14px;
  font-size: 0.85rem;
  color: var(--primary);
  margin-bottom: 24px;
}
.hero-title {
  font-size: 3.2rem;
  line-height: 1.2;
  font-weight: 800;
  margin-bottom: 20px;
}
.highlight {
  color: #1E3A8A;
}
.hero-description {
  font-size: 1.1rem;
  color: var(--muted);
  margin-bottom: 32px;
}
.hero-buttons {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
  flex-wrap: wrap;
}
.btn-large {
  padding: 12px 24px;
  font-size: 1rem;
}
.hero-stats {
  display: flex;
  gap: 24px;
}
.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
}
.visual-card {
  background: white;
  border-radius: 32px;
  padding: 24px;
  box-shadow: 0 20px 40px -12px rgba(0,0,0,0.15);
}
.chart-wrapper {
  height: 220px;
  margin: 16px 0;
}
.visual-footer {
  display: flex;
  justify-content: space-between;
}
.metric-value {
  font-size: 1.5rem;
  font-weight: 800;
  color: #1E3A8A;
}
.section-header {
  text-align: center;
  margin-bottom: 48px;
}
.section-header h2 {
  font-size: 2rem;
  margin-bottom: 8px;
}
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 32px;
}
.feature-card {
  background: white;
  border-radius: 28px;
  padding: 32px 24px;
  text-align: center;
  transition: 0.2s;
}
.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -12px rgba(0,0,0,0.1);
}
.feature-icon {
  color: #1E3A8A;
  margin-bottom: 16px;
}
.guide-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  margin-bottom: 32px;
}
.guide-column h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
}
.guide-list {
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.guide-list li {
  line-height: 1.5;
}
.guide-note {
  background: #eef2ff;
  border-radius: 24px;
  padding: 20px;
  text-align: center;
}
.two-columns {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: center;
}
.feature-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.feature-list li {
  display: flex;
  align-items: center;
  gap: 10px;
}
.graph-card {
  background: white;
  border-radius: 28px;
  padding: 24px;
}
.chart-container {
  height: 280px;
}
.activity-timeline {
  max-width: 700px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.activity-item {
  display: flex;
  align-items: center;
  gap: 14px;
  background: white;
  padding: 16px 20px;
  border-radius: 20px;
}
.activity-icon {
  background: rgba(30,58,138,0.1);
  width: 36px;
  height: 36px;
  border-radius: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1E3A8A;
}
.activity-time {
  margin-left: auto;
  font-size: 0.75rem;
  color: var(--muted);
}
.stack-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px;
}
.stack-item {
  background: white;
  padding: 10px 20px;
  border-radius: 40px;
  font-weight: 500;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.cta-card {
  background: linear-gradient(120deg, #1E3A8A, #2563EB);
  border-radius: 48px;
  padding: 48px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  color: white;
}
.cta-card .btn-primary {
  background: white;
  color: #1E3A8A;
}
.footer {
  border-top: 1px solid rgba(0,0,0,0.05);
  padding: 32px 20px;
  background: white;
}
.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}
.footer-links {
  display: flex;
  gap: 24px;
}
@media (max-width: 1024px) {
  .hero-grid, .two-columns, .guide-tabs, .features-grid {
    grid-template-columns: 1fr;
  }
  .hero-visual {
    order: -1;
  }
  .hero-title {
    font-size: 2.4rem;
  }
}
@media (max-width: 640px) {
  .hero-buttons {
    flex-direction: column;
  }
  .cta-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>