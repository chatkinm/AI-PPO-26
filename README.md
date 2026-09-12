# AI-сервис автоматизации предпроектного обследования (ППО) для IT-компании Xpage

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![Figma Plugin](https://img.shields.io/badge/Figma-FigJam_Plugin-F24E1E?style=flat&logo=figma&logoColor=white)](https://www.figma.com/)
[![Groq LPU](https://img.shields.io/badge/Groq-Whisper_LPU-F55036?style=flat)](https://groq.com/)

Комплексная система автоматизации этапа предпроектного обследования (ППО) заказной разработки цифровых продуктов. Сервис преобразует первичные сметы и записи созвонов с клиентом в утвержденную интерактивную карту экранов в **FigJam** и официальное **Техническое задание (ТЗ)** по корпоративному стандарту Xpage.

---

## 🎯 Бизнес-цели и метрики эффективности (KPI)

| Метрика | До внедрения | С AI-сервисом ППО | Эффект |
| :--- | :--- | :--- | :--- |
| **Трудозатраты на 1 ППО** | ~160 человеко-часов | **~50 человеко-часов** | Сокращение на **~70%** |
| **Разбор сметы и структура экранов** | ~1 час ручной работы | **~15 секунд** | Ускорение в **~200 раз** |
| **Подготовка и оформление ТЗ** | 8–16 часов | **~10 секунд** компиляция | Автоматический документ по стандарту Xpage |
| **Качество требований** | Субъективно, риск багов | **Стандартизировано** | Автопоиск противоречий и расчет DoR |

---

## 🚀 4 ключевых этапа системы

`mermaid
flowchart LR
    S1[1. Смета Excel] -->|openpyxl + LLM| S2[2. Иерархия экранов]
    S3[3. Аудио созвонов] -->|Groq Whisper LPU| S4[4. Кросс-анализ и DoR]
    S2 --> S5[5. Авто-отрисовка в FigJam]
    S4 --> S6[6. Генерация ТЗ .docx]
    S5 --> S6
`

1. **Этап 1: Первичная смета ⟶ Структура экранов**:
   * Парсинг Excel-смет через openpyxl (очистка от шума и формул, экономия 80% контекста).
   * AI-декомпозиция на модули, экраны со статусами и интерактивные элементы интерфейса.
   * Интерактивный холст React + SVG с масштабированием и ручной валидацией PM.
2. **Этап 2: База знаний созвонов ⟶ Анализ противоречий, DoR и опросник**:
   * Скоростная транскрибация аудиозаписей через Groq Whisper Large V3 на LPU (1 час аудио за 15–20 сек).
   * Сопоставление требований со сметой и онтологией Чек-лист полноты информации по проекту с рисками (для этапа ППО).md.
   * Расчет индекса готовности требований (DoR от 0 до 100%), реестр REQ-01..., выявление противоречий (Scope Creep) и экспорт опросника клиенту в Markdown.
3. **Этап 3: Интеграция с FigJam и нативная авто-отрисовка**:
   * Математический расчет 2D-координат в igjam_layout.py.
   * Нативный плагин Figma Desktop (igjam-plugin/): 100% программное создание вертикальных стеков экранов (Wireframe stacks с фиолетовыми шапками, белыми карточками и ортогональными связями) без Ctrl+V за 0.5 секунды.
   * Чтение дизайнерских файлов через Figma REST API.
4. **Этап 4: Генерация официального Технического задания по стандарту Xpage**:
   * Движок компиляции 	z_generator.py на базе Шаблон Технического задания (ТЗ) Xpage.md.
   * Итоговый документ Microsoft Word (.docx) на 35–50 страниц (~75 КБ, 380+ параграфов, 18 таблиц, все 11 корпоративных разделов стандарта Xpage, матрица RBAC/CRUD, схема BFF -> 1C, NFR/SLA, Use Cases, каллауты и колонтитулы).

---

## 🛠️ Стек технологий

* **Backend**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2, python-docx, openpyxl, Groq SDK.
* **AI & Speech**: Groq LPU (Whisper Large V3), каскад LLM (gpt-oss-120b, gpt-oss-20b, qwen3.8-27b, Google Gemini).
* **Frontend**: React 18, Tailwind CSS, Markmap / SVG Canvas.
* **Figma**: Figma Desktop Plugin API (QuickJS C++ Sandbox), Figma REST API.

---

## ⚡ Быстрый старт

### 1. Клонирование репозитория и установка зависимостей
`ash
git clone https://github.com/chatkinm/AI-PPO-26.git
cd AI-PPO-26
pip install -r backend/requirements.txt
`

### 2. Настройка переменных окружения
Скопируйте пример файла конфигурации:
`ash
cp .env.example .env
`
Укажите ваш API-ключ GROQ_API_KEY (бесплатно на [console.groq.com](https://console.groq.com/)) и при необходимости FIGMA_ACCESS_TOKEN.

### 3. Запуск сервиса
`ash
python run.py
`
Сервис запустится по адресу: **[http://localhost:8080](http://localhost:8080)**  
Swagger API документация: **[http://localhost:8080/docs](http://localhost:8080/docs)**

---

## 🔌 Запуск FigJam плагина (Figma Desktop)

1. Откройте приложение **Figma Desktop** и создайте новую доску FigJam (New FigJam board).
2. В меню Figma выберите: **Plugins ⟶ Development ⟶ Import plugin from manifest...**.
3. Выберите файл igjam-plugin/manifest.json.
4. Запустите плагин: **Plugins ⟶ Development ⟶ Xpage ППО FigJam Sync**.
5. Выберите проект и нажмите **«⚡ Нарисовать на холсте FigJam»**.

---

## 📚 База Знаний проекта (WIKI)

Подробная инженерная и архитектурная документация доступна в директории WIKI/:
* [01. Обзор проекта и бизнес-контекст](WIKI/01_OVERVIEW.md)
* [02. Архитектура и карта кодовой базы](WIKI/02_ARCHITECTURE_AND_CODE_MAP.md)
* [03. Руководство по внешним API и интеграциям](WIKI/03_API_INTEGRATIONS.md)
* [04. Руководство разработчика: запуск и User Flow](WIKI/04_DEVELOPMENT_GUIDE.md)
* [05. Глубокое погружение: AI-модели, шаблоны, ограничения и FigJam плагин](WIKI/05_AI_AND_PLUGIN_DEEP_DIVE.md)
* [06. Полный пайплайн проекта и стек инструментов по этапам](WIKI/06_PIPELINE_AND_TOOLSTACK.md)
