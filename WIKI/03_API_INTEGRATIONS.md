# 03. Руководство по внешним API и интеграциям

В проекте используются три внешних API: **Google AI Studio**, **Groq Cloud API** и **Figma / FigJam REST API**.

---

## 1. Google AI Studio API (Основная LLM)

### Назначение:
Интеллектуальная обработка текста, построение иерархии экранов из сметы, глубокий сравнительный анализ расшифровок встреч, детекция противоречий и генерация глав Технического задания.

### Используемые модели:
* **Основная модель**: `gemma-4-31b-it` (или актуальная открытая модель линейки Gemma в Google AI Studio).
* **Фоллбек-модель**: `gemini-2.5-flash` / `gemini-1.5-flash` — сверхбыстрая модель с контекстным окном до **1-2 млн токенов**. Она способна за один запрос вместить все транскрипции созвонов (более 150 000 символов) без потери деталей.

### Настройка в `.env`:
```env
GOOGLE_API_KEY=AIzaSy...
LLM_MODEL=gemma-4-31b-it
LLM_FALLBACK_MODEL=gemini-2.5-flash
```

### Как получить ключ:
1. Перейдите в [Google AI Studio](https://aistudio.google.com/).
2. Нажмите **«Get API key»** -> **«Create API key»**.
3. Скопируйте полученный ключ в переменную `GOOGLE_API_KEY` в файле `.env`.
*Ключ бесплатен в рамках Free Tier (до 15 запросов в минуту).*

### Механика Structured Output:
Сервис запрашивает у модели ответ строго в формате JSON, передавая схему Pydantic в параметре `response_schema`. Это гарантирует, что на выходе никогда не будет лишнего пояснительного текста или сломанного формата.

---

## 2. Groq Cloud API (Сверхбыстрая транскрибация аудио)

### Назначение:
Мгновенная расшифровка аудиозаписей встреч с клиентом в текст с высокой точностью распознавания русской речи и терминов.

### Используемая модель:
* `whisper-large-v3` (или `whisper-large-v3-turbo`) на аппаратных ускорителях LPU Groq.
* Обработка 1 часа аудио занимает **менее 15-20 секунд**!

### Настройка в `.env`:
```env
GROQ_API_KEY=gsk_...
GROQ_WHISPER_MODEL=whisper-large-v3
```

### Как получить ключ:
1. Зарегистрируйтесь на [Groq Console](https://console.groq.com/).
2. Перейдите в раздел **API Keys** -> **Create API Key**.
3. Скопируйте ключ в `GROQ_API_KEY` в `.env`.
*Бесплатный тариф предоставляет щедрые лимиты, которых более чем достаточно для предпроектного обследования.*

### Формат запроса:
Сервис отправляет мультипарт-запрос на эндпоинт `https://api.groq.com/openai/v1/audio/transcriptions` с параметрами:
* `model`: `whisper-large-v3`
* `language`: `ru`
* `response_format`: `verbose_json` (для сохранения тайм-кодов фраз).

---

## 3. Figma & FigJam: Двусторонняя интеграция и автоматическая отрисовка

### 3.1. Архитектурное устройство платформы Figma
При проектировании интеграции важно учитывать разделение платформы Figma на два контура:
1. **Figma REST API (`https://api.figma.com/v1/`)**:
   * **Принципиально Read-Only для объектов холста**. В официальной спецификации Figma OpenAPI отсутствуют методы `POST /v1/files` или `POST /v1/nodes`. Через REST API можно только считывать данные файла, оставлять комментарии и управлять переменными. Сам холст Figma исполняется на C++/WebAssembly и синхронизируется через бинарный протокол WebSocket.
   * **Назначение в сервисе**: чтение существующих дизайнерских прототипов и схем (`GET /v1/files/{file_key}`) для обогащения разделов итогового ТЗ (Шаг 4) в полном соответствии с ТЗ кейса Xpage.

2. **Figma Plugin API (`figjam-plugin/`)**:
   * **Официальный нативный способ создания и изменения объектов на холсте**. Плагин исполняется внутри движка FigJam и имеет прямой программный доступ к методам `figma.createShapeWithText()`, `figma.createConnector()`, `figma.createSticky()` и `figma.viewport.scrollAndZoomIntoView()`.
   * **Назначение в сервисе**: **100% автоматическое построение карты экранов и функций** на холсте FigJam без ручных действий и без `Ctrl+V`.

---

### 3.2. Компонент автоматической отрисовки: FigJam Plugin (`figjam-plugin/`)

В папке `figjam-plugin/` расположен готовый плагин для Figma/FigJam:
* `manifest.json`: манифест плагина с разрешениями доступа к локальному бэкенду `http://localhost:8080`.
* `ui.html`: окно управления внутри FigJam с автоматической подгрузкой проектов из локального сервиса.
* `code.js`: исполнительный модуль Figma Plugin API, который:
  - Предзагружает шрифты семейств `Inter` (Regular, Medium, Bold);
  - Создает корпоративные вертикальные стеки карточек экранов через `figma.createShapeWithText()` с типом `ROUNDED_RECTANGLE` (фиолетовые шапки `#7C3AED`, белые карточки функциональных блоков с границами `#CBD5E1`, левым выравниванием текста);
  - Расставляет верхние навигационные кнопки-плашки (`PILL`);
  - Протягивает ортогональные векторные коннекторы `figma.createConnector()` типа `ELBOWED` с точной привязкой к магнитам (`start_magnet` / `end_magnet`) и синей обводкой `#3B82F6`;
  - Автоматически центрирует и масштабирует камеру холста на всей созданной структуре (`figma.viewport.scrollAndZoomIntoView`).

#### Как запустить плагин и нарисовать дерево (2 шага):
1. **Открыть доску FigJam**: В приложении Figma Desktop создайте новую доску FigJam (кнопка `+` ⟶ `FigJam board`) или откройте существующую.
2. **Запустить плагин**: 
   - Нажмите меню Figma (или правой кнопкой по холсту) ⟶ **Plugins ⟶ Development ⟶ Xpage ППО FigJam Sync**.
   - В окне плагина статус покажет: `🟢 Сервис ППО подключен (localhost:8080)`.
   - В выпадающем списке выберите проект (по умолчанию выбран `Сквозной кейс: Приложение ломбарда (Xpage)`).
   - Нажмите кнопку **«⚡ Нарисовать на холсте FigJam»**.
   - Плагин программно создаст и расставит карточки модулей, экранов и векторных связей ровно по корпоративному стандарту Xpage (без стикеров и наложений), после чего отцентрирует камеру на созданной схеме!

---

### 3.3. Бэкенд-эндпоинт расчета авто-лейаута (`backend/app/routers/figjam.py`)

Для построения архитектуры на холсте FigJam бэкенд использует движок `backend/app/services/figjam_layout.py`:
* `GET /api/figjam/projects`: возвращает список проектов с количеством экранов и модулей для селектора плагина.
* `GET /api/figjam/nodes/{project_id}`: возвращает массив узлов (117 узлов и 33 коннектора для кейса ломбарда) с координатами `(x, y)`, шириной, высотой, заливками, шрифтами, выравниванием и магнитами коннекторов.
* `POST /api/figjam/sync/{project_id}`: обратная синхронизация — чтение прототипов Figma по ключу файла через REST API и передача компонентов в генератор ТЗ.

---

### 3.4. Настройка токена в `.env`:
```env
FIGMA_ACCESS_TOKEN=figd_...
```

#### Как получить токен:
1. Войдите в свой аккаунт на [Figma.com](https://www.figma.com/).
2. Кликните по аватарке профиля в левом верхнем углу ⟶ **Settings** ⟶ вкладка **Security**.
3. В блоке **Personal access tokens** нажмите **«Generate new token»** (права `File content (Read)`).
4. Скопируйте токен в `FIGMA_ACCESS_TOKEN` в `.env`.

---

### 3.5. Особенности настройки manifest.json и устранение ошибок (Troubleshooting)

При разработке и локальном запуске плагинов для Figma/FigJam действуют строгие правила безопасности песочницы Figma:

#### 1. Ошибка `Invalid value for networkAccess / devAllowedDomains`:
* **Симптом**: `Manifest error: Invalid value for devAllowedDomains. 'http://127.0.0.1:8080' must be a valid URL.`
* **Причина**: Внутренний валидатор манифеста Figma строго требует указания хоста в формате **`http://localhost:<port>`** и отклоняет числовые IP-адреса (`127.0.0.1`). Также локальные адреса разработки должны находиться в массиве `devAllowedDomains`, а не в `allowedDomains`.
* **Правильная конфигурация в `figjam-plugin/manifest.json`**:
```json
{
  "name": "Xpage ППО FigJam Sync",
  "id": "xpage-ppo-figjam-sync",
  "api": "1.0.0",
  "main": "code.js",
  "ui": "ui.html",
  "editorType": ["figjam", "figma"],
  "networkAccess": {
    "allowedDomains": ["none"],
    "devAllowedDomains": ["http://localhost:8080"],
    "reasoning": "Подключение к локальному серверу ППО для загрузки структуры проекта"
  }
}
```

#### 2. Ограничение среды исполнения: Web Browser vs Desktop App:
* **В браузере (Chrome/Firefox/Edge)** пункт меню `Development ⟶ Import plugin from manifest` скрыт Figma, так как браузер изолирован от чтения файлов с диска.
* **Локальные плагины по манифесту запускаются только в настольном приложении Figma Desktop App**.

#### 3. Политика CORS для iframe плагина (`origin: null`) и Private Network Access (PNA):
* Окна плагинов в Figma работают внутри изолированного iframe с источником `Origin: null`.
* В браузерах Chromium 100+ и Electron (на котором построена Figma Desktop) при запросе из веб-контекста или iframe к локальным адресам (`localhost` / `127.0.0.1`) отправляется preflight-запрос `OPTIONS` с заголовком `Access-Control-Request-Private-Network: true`.
* Если сервер не возвращает в ответ заголовок `Access-Control-Allow-Private-Network: true`, браузер блокирует запрос политикой безопасности Private Network Access.
* Стандартный middleware `CORSMiddleware` из библиотеки Starlette при определенных параметрах или `allow_credentials=True` также отвергает `null` и возвращает `400 Disallowed CORS origin`.
* **Решение в `backend/app/main.py`**:
  Реализован собственный middleware перехвата HTTP-запросов, который для любых `OPTIONS` немедленно отдает HTTP 200 и добавляет полные CORS-заголовки:
  ```python
  @app.middleware("http")
  async def add_universal_cors_headers(request: Request, call_next):
      if request.method == "OPTIONS":
          response = Response(status_code=200)
      else:
          response = await call_next(request)
      response.headers["Access-Control-Allow-Origin"] = "*"
      response.headers["Access-Control-Allow-Methods"] = "*"
      response.headers["Access-Control-Allow-Headers"] = "*"
      response.headers["Access-Control-Allow-Private-Network"] = "true"
      return response
  ```

#### 4. Архитектурное разделение среды исполнения в плагине:
* Код холста `code.js` исполняется в легковесной песочнице Figma QuickJS, где нет браузерных объектов `window`, `DOM` и глобального `fetch`.
* Код интерфейса `ui.html` исполняется в полноценном Chromium iframe, где доступны все браузерные сетевые API (`fetch`).
* Поэтому загрузка структуры проекта (`/api/figjam/nodes/{id}`) осуществляется непосредственно в `ui.html`, после чего сформированный payload передается в `code.js` по шине `parent.postMessage({ pluginMessage: { type: 'DRAW_STRUCTURE', payload } })`. Это обеспечивает 100% надежность отрисовки в любой версии Figma Desktop.

#### 5. Ошибка `TypeError: object is not extensible` при обращении к свойствам узлов Figma:
* **Симптом**: Модальное окно Figma сообщает: `Ошибка отрисовки: object is not extensible`. При этом на холсте успевает появиться только первая фигура без текста.
* **Причина**: В песочнице Figma QuickJS все объекты узлов (`ShapeWithTextNode`, `TextSublayerNode`, `ConnectorNode`) представляют собой нативные C++ прокси-объекты со строгой изоляцией и запретом на расширение (`Object.isExtensible() === false`). Попытка присвоить свойство, которого нет в официальной сигнатуре интерфейса Figma (например, `shape.text.textAlignVertical = 'CENTER'`), не игнорируется, а выбрасывает фатальное исключение JavaScript: `TypeError: object is not extensible`.
* **Правильная спецификация интерфейса `TextSublayerNode`**:
  - Вертикальное выравнивание текста внутри фигур `ShapeWithTextNode` выполняется движком FigJam **автоматически** по центру; свойства `textAlignVertical` в объекте `shape.text` нет.
  - Допустимое свойство выравнивания — только горизонтальное: `shape.text.textAlignHorizontal = 'LEFT' | 'CENTER'`.
  - Присвоение текста `shape.text.characters = fullText;` обязательно должно происходить **до** модификации шрифтов `fontName` и заливки `fills`, чтобы в песочнице инициализировались текстовые глифы.
  - Все операции присвоения шрифтов и цветов текста обернуты в блоки `try/catch` с безопасным дефолтом, что исключает сбой всего процесса построения архитектуры.



