# Web Scraper: Полное руководство для начинающих

## Оглавление
1. [Что такое веб-скрапинг?](#что-такое-веб-скрапинг)
2. [Архитектура нашего парсера](#архитектура-нашего-парсера)
3. [Технологии и библиотеки](#технологии-и-библиотеки)
4. [Компоненты системы](#компоненты-системы)
5. [Как работает каждый модуль](#как-работает-каждый-модуль)
6. [Проблемы и их решения](#проблемы-и-их-решения)
7. [Запуск и использование](#запуск-и-использование)

---

## Что такое веб-скрапинг?

**Веб-скрапинг** (web scraping) — это автоматическое извлечение данных с веб-сайтов.

### Простая аналогия:
Представь, что тебе нужно собрать информацию о 50 серф-кемпах. Ты можешь:
- **Вручную**: открыть каждый сайт, скопировать данные — займёт 2-3 дня
- **Автоматически**: написать скрипт, который сделает это за 15 минут

### Как это работает на базовом уровне:

```
1. Скрипт отправляет HTTP-запрос на сайт (как браузер)
2. Сервер возвращает HTML-код страницы
3. Скрипт парсит (разбирает) HTML и извлекает нужные данные
4. Данные сохраняются в базу данных
```

### Пример:
```python
# Браузер делает это когда ты открываешь сайт:
GET https://www.surfcamp.com/

# Сервер отвечает HTML:
<html>
  <h1>Baleal Surf Camp</h1>
  <p class="price">$45 per night</p>
  <img src="photo.jpg">
</html>

# Наш скрипт извлекает:
name = "Baleal Surf Camp"
price = 45
image = "photo.jpg"
```

---

## Архитектура нашего парсера

### Общая схема:

```
┌─────────────────────────────────────────────────────────────────┐
│                        run_scraper.py                           │
│                    (Главный оркестратор)                        │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Evomi Client │    │  Camp Parser  │    │   TripAdvisor │
│  (Fetch HTML) │    │ (Extract Data)│    │    Parser     │
└───────────────┘    └───────────────┘    └───────────────┘
        │                     │                     │
        │                     ▼                     │
        │            ┌───────────────┐              │
        │            │  Claude AI    │              │
        │            │ (Smart Parse) │              │
        │            └───────────────┘              │
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌───────────────┐
                    │    Image      │
                    │  Downloader   │
                    └───────────────┘
                              │
                              ▼
                    ┌───────────────┐
                    │   DB Saver    │
                    │ (Django ORM)  │
                    └───────────────┘
                              │
                              ▼
                    ┌───────────────┐
                    │   SQLite /    │
                    │  PostgreSQL   │
                    └───────────────┘
```

### Поток данных:

```
surf_camps.ru (список URL)
        │
        ▼
[1] Evomi API получает HTML страницы
        │
        ▼
[2] CampParser извлекает данные из HTML
        │
        ├──▶ BeautifulSoup: базовый парсинг (название, email, телефон)
        │
        └──▶ Claude AI: умный парсинг (цены, описания, инструкторы)
        │
        ▼
[3] TripAdvisorParser ищет отзывы
        │
        ▼
[4] ImageDownloader скачивает фото
        │
        ▼
[5] DatabaseSaver сохраняет в Django модели
```

---

## Технологии и библиотеки

### 1. Python
**Что это**: Язык программирования
**Зачем**: Основной язык для скрапинга благодаря богатой экосистеме библиотек

### 2. Requests
**Что это**: HTTP-библиотека для Python
**Зачем**: Отправка запросов к сайтам

```python
import requests

# GET-запрос — получить страницу
response = requests.get('https://example.com')
html = response.text  # HTML-код страницы

# POST-запрос — отправить данные
response = requests.post('https://api.com', json={'url': 'https://site.com'})
```

**Под капотом**:
- Открывает TCP-соединение с сервером
- Отправляет HTTP-заголовки (User-Agent, Accept, etc.)
- Получает ответ и парсит его

### 3. BeautifulSoup
**Что это**: Библиотека для парсинга HTML/XML
**Зачем**: Извлечение данных из HTML-кода

```python
from bs4 import BeautifulSoup

html = '<html><h1 class="title">Hello</h1><p>World</p></html>'
soup = BeautifulSoup(html, 'html.parser')

# Найти элемент по тегу
title = soup.find('h1')  # <h1 class="title">Hello</h1>
print(title.text)        # "Hello"

# Найти по классу
title = soup.find('h1', class_='title')

# Найти все элементы
paragraphs = soup.find_all('p')  # [<p>World</p>]

# CSS-селекторы
soup.select('div.content > p')  # все <p> внутри <div class="content">
```

**Под капотом**:
- Строит DOM-дерево (Document Object Model) из HTML
- Позволяет навигировать по дереву как по объектам Python
- Использует разные парсеры: html.parser (встроенный), lxml (быстрый), html5lib (точный)

### 4. Evomi API
**Что это**: Сервис для веб-скрапинга
**Зачем**: Обход защиты сайтов от ботов

```python
# Без Evomi — сайт видит наш IP и может заблокировать
response = requests.get('https://tripadvisor.com')
# Результат: 403 Forbidden или CAPTCHA

# С Evomi — запрос идёт через их серверы
response = requests.post(
    'https://scrape.evomi.com/api/v1/scraper/realtime',
    headers={'x-api-key': 'YOUR_KEY'},
    json={'url': 'https://tripadvisor.com'}
)
# Результат: HTML страницы
```

**Под капотом Evomi**:
1. Получает твой запрос
2. Выбирает случайный IP из пула (residential proxies)
3. Запускает headless-браузер (Chrome без интерфейса)
4. Загружает страницу, выполняет JavaScript
5. Ждёт пока страница полностью загрузится
6. Возвращает тебе готовый HTML

**Почему это нужно**:
- Многие сайты блокируют запросы от серверов (datacenter IPs)
- JavaScript-контент не загружается без браузера
- CAPTCHA и anti-bot защита

### 5. Anthropic Claude API
**Что это**: AI-модель для обработки текста
**Зачем**: Умное извлечение данных из неструктурированного текста

```python
import anthropic

client = anthropic.Anthropic(api_key='YOUR_KEY')

response = client.messages.create(
    model='claude-3-haiku-20240307',
    max_tokens=1000,
    messages=[{
        'role': 'user',
        'content': '''
        Извлеки данные из этого текста:
        "Baleal Surf Camp - €45/night, includes breakfast,
        beginner lessons from €30, contact: info@baleal.com"

        Верни JSON: {name, price, email, lessons_price}
        '''
    }]
)

# Claude вернёт:
# {"name": "Baleal Surf Camp", "price": 45, "email": "info@baleal.com", "lessons_price": 30}
```

**Зачем AI в скрапинге**:
- Каждый сайт имеет уникальную структуру HTML
- Писать отдельный парсер для каждого сайта — долго
- AI понимает контекст и извлекает данные из любого формата

**Пример проблемы без AI**:
```html
<!-- Сайт 1 -->
<span class="price">$45</span>

<!-- Сайт 2 -->
<div data-cost="45 USD">

<!-- Сайт 3 -->
<p>Цена: от 45 долларов за ночь</p>

<!-- AI понимает все три варианта -->
```

### 6. Django ORM
**Что это**: Object-Relational Mapping для Django
**Зачем**: Работа с базой данных через Python-объекты

```python
# Без ORM — чистый SQL:
cursor.execute(
    "INSERT INTO camps (name, price) VALUES (?, ?)",
    ("Baleal", 45)
)

# С Django ORM — Python-объекты:
camp = SurfCamp(name="Baleal", price=45)
camp.save()

# Или одной строкой:
SurfCamp.objects.create(name="Baleal", price=45)

# Поиск:
camp = SurfCamp.objects.get(slug='baleal-surf-camp')
camps = SurfCamp.objects.filter(price__lt=50)  # цена < 50
```

**Под капотом**:
- Django переводит Python-код в SQL-запросы
- Автоматически экранирует данные (защита от SQL-injection)
- Управляет соединениями с БД
- Кеширует запросы

---

## Компоненты системы

### Файловая структура:

```
scraper/
├── __init__.py           # Делает папку Python-пакетом
├── config.py             # Конфигурация (API ключи, пути)
├── run_scraper.py        # Главный скрипт запуска
│
├── parsers/
│   ├── __init__.py
│   ├── camp_parser.py        # Парсинг сайтов кемпов
│   └── tripadvisor_parser.py # Парсинг TripAdvisor
│
└── utils/
    ├── __init__.py
    ├── evomi_client.py       # HTTP-клиент с retry
    ├── image_downloader.py   # Скачивание изображений
    └── db_saver.py           # Сохранение в Django БД
```

---

## Как работает каждый модуль

### 1. evomi_client.py — HTTP-клиент

**Задача**: Получать HTML-страницы через Evomi API с обработкой ошибок.

```python
class EvomiClient:
    def __init__(self, api_key, max_retries=3):
        self.api_key = api_key
        self.max_retries = max_retries

    def fetch(self, url):
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    EVOMI_API_URL,
                    headers={'x-api-key': self.api_key},
                    json={'url': url},
                    timeout=60
                )

                if response.status_code == 200:
                    return response.json()['html']

                elif response.status_code == 429:
                    # Rate limit — ждём и пробуем снова
                    time.sleep(attempt * 2)

            except requests.Timeout:
                # Таймаут — пробуем снова
                continue

        return None  # Все попытки исчерпаны
```

**Ключевые концепции**:

1. **Retry логика** — если запрос упал, пробуем снова (до 3 раз)
2. **Exponential backoff** — каждая следующая попытка ждёт дольше
3. **Timeout** — не ждём ответа вечно (60 секунд максимум)
4. **Error handling** — ловим исключения, не падаем

### 2. camp_parser.py — Парсер сайтов

**Задача**: Извлечь структурированные данные из HTML.

```python
class CampParser:
    def parse(self, html, url):
        soup = BeautifulSoup(html, 'html.parser')
        data = CampData()

        # 1. Базовый парсинг
        data.name = self._extract_name(soup)
        data.email = self._extract_email(html)
        data.images = self._extract_images(soup, url)

        # 2. AI-парсинг (если включен)
        if self.use_ai:
            ai_data = self._ai_extract(html)
            data.merge(ai_data)

        return data

    def _extract_name(self, soup):
        # Приоритет: <title> → <h1> → <meta og:title>

        title = soup.find('title')
        if title:
            return title.text.split('|')[0].strip()

        h1 = soup.find('h1')
        if h1:
            return h1.text.strip()

        return None

    def _extract_email(self, html):
        # Регулярное выражение для email
        pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        emails = re.findall(pattern, html)

        # Фильтруем мусор
        valid_emails = [
            e for e in emails
            if 'example' not in e and 'test' not in e
        ]

        return valid_emails[0] if valid_emails else None

    def _extract_images(self, soup, base_url):
        images = []

        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src')
            if not src:
                continue

            # Относительный URL → абсолютный
            if src.startswith('/'):
                src = base_url + src

            # Фильтруем иконки и логотипы
            if 'logo' in src.lower() or 'icon' in src.lower():
                continue

            images.append(src)

        return images[:20]  # Максимум 20 изображений
```

**Ключевые концепции**:

1. **Fallback стратегия** — если один метод не работает, пробуем другой
2. **Regex** — регулярные выражения для поиска паттернов (email, телефон)
3. **URL нормализация** — превращаем относительные пути в абсолютные
4. **Фильтрация** — отсеиваем мусор (иконки, placeholder'ы)

### 3. tripadvisor_parser.py — Парсер отзывов

**Задача**: Найти кемп на TripAdvisor и собрать отзывы.

```python
class TripAdvisorParser:
    def __init__(self, evomi_client):
        self.evomi = evomi_client

    def search_camp(self, camp_name, location):
        # Формируем поисковый запрос
        query = f"{camp_name} {location} surf"
        search_url = f"https://www.tripadvisor.com/Search?q={quote_plus(query)}"

        # Получаем страницу поиска
        html = self.evomi.fetch(search_url)
        soup = BeautifulSoup(html, 'html.parser')

        # Ищем ссылки на результаты
        for link in soup.find_all('a', href=re.compile(r'/Attraction_Review')):
            href = link.get('href')
            text = link.text.lower()

            # Проверяем что это наш кемп
            if camp_name.lower().split()[0] in text:
                return 'https://www.tripadvisor.com' + href

        return None

    def parse_reviews(self, tripadvisor_url):
        html = self.evomi.fetch(tripadvisor_url)
        soup = BeautifulSoup(html, 'html.parser')

        reviews = []

        for review_div in soup.find_all('div', {'data-reviewid': True}):
            review = {
                'author': self._extract_author(review_div),
                'rating': self._extract_rating(review_div),
                'text': self._extract_text(review_div),
                'date': self._extract_date(review_div)
            }
            reviews.append(review)

        return reviews
```

**Проблемы с TripAdvisor**:
- Агрессивная защита от ботов
- Динамический контент (React/JavaScript)
- Часто меняют структуру HTML
- Поэтому многие кемпы не находятся

### 4. image_downloader.py — Загрузчик изображений

**Задача**: Скачать изображения и сохранить локально.

```python
class ImageDownloader:
    def __init__(self, base_dir, max_size_mb=10):
        self.base_dir = Path(base_dir)
        self.max_size = max_size_mb * 1024 * 1024  # В байтах

    def download_image(self, url, camp_slug, index):
        # Пропускаем data: URL (встроенные SVG)
        if url.startswith('data:'):
            return None

        try:
            # Скачиваем
            response = requests.get(url, timeout=30, stream=True)

            # Проверяем размер
            size = response.headers.get('Content-Length')
            if size and int(size) > self.max_size:
                return None

            # Определяем расширение
            content_type = response.headers.get('Content-Type', '')
            ext = self._get_extension(url, content_type)

            # Генерируем уникальное имя файла
            filename = f"{camp_slug}_{index:02d}_{hash(url)[:8]}{ext}"
            filepath = self.base_dir / 'camps' / camp_slug / filename

            # Создаём директорию
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Сохраняем файл
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)

            return f"camps/{camp_slug}/{filename}"

        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return None
```

**Ключевые концепции**:

1. **Streaming** — скачиваем по частям (chunks), не загружаем всё в память
2. **Content-Type** — определяем тип файла из HTTP-заголовка
3. **Уникальные имена** — хэш URL предотвращает конфликты
4. **mkdir -p** — `parents=True, exist_ok=True` создаёт все папки

### 5. db_saver.py — Сохранение в БД

**Задача**: Сохранить данные в Django-модели.

```python
class DatabaseSaver:
    def save_camp(self, camp_data, location, country):
        # 1. Найти или создать регион
        region = self._find_or_create_region(location, country)

        # 2. Создать slug (URL-friendly имя)
        slug = slugify(f"{camp_data['name']}-{location}")

        # 3. Найти или создать кемп
        camp, created = SurfCamp.objects.get_or_create(
            slug=slug,
            defaults={
                'name': camp_data['name'],
                'region': region,
                'price_per_night': camp_data.get('price', 0),
                # ... другие поля
            }
        )

        # 4. Обновить данные если кемп уже существовал
        if not created:
            camp.description = camp_data.get('description', camp.description)
            camp.save()

        # 5. Сохранить связанные данные
        self._save_images(camp, camp_data['images'])
        self._save_reviews(camp, camp_data['reviews'])

        return camp
```

**Ключевые концепции**:

1. **get_or_create** — атомарная операция: найти или создать
2. **Slug** — URL-friendly идентификатор ("Baleal Surf Camp" → "baleal-surf-camp")
3. **Идемпотентность** — можно запускать много раз, не создаёт дубликаты
4. **Связанные данные** — отдельно сохраняем images, reviews

### 6. run_scraper.py — Оркестратор

**Задача**: Координировать работу всех компонентов.

```python
class SurfCampScraper:
    def __init__(self):
        # Инициализация компонентов
        self.evomi = EvomiClient(EVOMI_API_KEY)
        self.camp_parser = CampParser(ANTHROPIC_API_KEY)
        self.tripadvisor = TripAdvisorParser(self.evomi)
        self.image_downloader = ImageDownloader(MEDIA_DIR)
        self.db_saver = DatabaseSaver()

    def process_camp(self, camp_entry):
        name = camp_entry['name']
        url = camp_entry['url']

        try:
            # 1. Получить HTML сайта кемпа
            html = self.evomi.fetch(url)
            if not html:
                logger.warning(f"Failed to fetch {url}")
                return False

            # 2. Распарсить данные
            camp_data = self.camp_parser.parse(html, url)

            # 3. Получить данные с TripAdvisor
            ta_data = self.tripadvisor.get_camp_data(name, camp_entry['location'])

            # 4. Скачать изображения
            image_paths = self.image_downloader.download_images(
                camp_data.image_urls,
                camp_data.slug
            )

            # 5. Сохранить в БД
            self.db_saver.save_camp(camp_data, ta_data, image_paths)

            return True

        except Exception as e:
            # Ловим любую ошибку, логируем, продолжаем
            logger.error(f"Error processing {name}: {e}")
            return False

    def run(self):
        camps = self.parse_camps_file(CAMPS_FILE)

        for i, camp in enumerate(camps):
            logger.info(f"[{i+1}/{len(camps)}] {camp['name']}")

            self.process_camp(camp)

            # Задержка между запросами
            time.sleep(3)
```

**Ключевые концепции**:

1. **Dependency Injection** — компоненты создаются снаружи и передаются
2. **Error Isolation** — ошибка в одном кемпе не останавливает весь процесс
3. **Rate Limiting** — задержки между запросами чтобы не забанили
4. **Progress Logging** — видим на каком этапе находимся

---

## Проблемы и их решения

### 1. Блокировка по IP

**Проблема**: Сайт видит много запросов с одного IP и блокирует.

**Решение**:
- Residential прокси (Evomi) — IP обычных пользователей
- Ротация IP — каждый запрос с нового адреса
- Задержки между запросами

### 2. JavaScript-контент

**Проблема**: Данные загружаются JavaScript'ом после загрузки страницы.

```html
<!-- Сервер отдаёт: -->
<div id="content"></div>
<script>
  fetch('/api/data').then(data => {
    document.getElementById('content').innerHTML = data;
  });
</script>

<!-- Нам нужно: -->
<div id="content">Actual data here</div>
```

**Решение**:
- Headless браузер (Puppeteer, Playwright)
- Evomi рендерит JS за нас

### 3. CAPTCHA

**Проблема**: Сайт показывает капчу.

**Решение**:
- Evomi обходит большинство капч
- Сервисы решения капч (2captcha)
- Или просто пропустить этот сайт

### 4. Разная структура сайтов

**Проблема**: Каждый сайт хранит данные по-разному.

```html
<!-- Сайт 1 -->
<span class="price">$45</span>

<!-- Сайт 2 -->
<div data-price="45">

<!-- Сайт 3 -->
<script>var price = 45;</script>
```

**Решение**:
- AI (Claude) понимает контекст
- Fallback стратегии
- Regex для типичных паттернов

### 5. Rate Limiting

**Проблема**: Сайт ограничивает количество запросов.

```
429 Too Many Requests
```

**Решение**:
- Exponential backoff — увеличиваем задержку с каждой попыткой
- Retry логика — пробуем снова после паузы
- Соблюдаем robots.txt

### 6. Устойчивость к ошибкам

**Проблема**: Один сбой не должен останавливать весь процесс.

**Решение**:
```python
for camp in camps:
    try:
        process(camp)
    except Exception as e:
        logger.error(e)
        continue  # Продолжаем со следующим
```

---

## Запуск и использование

### Установка зависимостей:

```bash
cd /Users/surfg/projects/surfcamp/backend
source venv/bin/activate
pip install requests beautifulsoup4 anthropic
```

### Запуск:

```bash
# Тестовый режим (2 кемпа)
python -m scraper.run_scraper --test

# Полный запуск
python -m scraper.run_scraper

# Без TripAdvisor (быстрее)
python -m scraper.run_scraper --skip-ta

# Конкретный кемп
python -m scraper.run_scraper --camp "Baleal"

# Начать с N-го кемпа
python -m scraper.run_scraper --start 10
```

### Мониторинг:

```bash
# Следить за логом в реальном времени
tail -f scraper_output.log

# Сколько кемпов обработано
grep -c "SUCCESS:" scraper_output.log

# Посмотреть ошибки
grep "ERROR\|FAILED" scraper_output.log
```

---

## Словарь терминов

| Термин | Объяснение |
|--------|------------|
| **HTML** | HyperText Markup Language — язык разметки веб-страниц |
| **DOM** | Document Object Model — древовидное представление HTML |
| **HTTP** | Протокол передачи данных в интернете |
| **API** | Application Programming Interface — способ общения между программами |
| **Proxy** | Посредник между тобой и сайтом |
| **Headless браузер** | Браузер без интерфейса, управляемый кодом |
| **Regex** | Regular Expression — шаблон для поиска текста |
| **ORM** | Object-Relational Mapping — работа с БД через объекты |
| **Slug** | URL-friendly строка (без пробелов и спецсимволов) |
| **Rate Limiting** | Ограничение количества запросов |
| **Retry** | Повторная попытка после ошибки |
| **Backoff** | Увеличение задержки между попытками |

---

## Полезные ссылки

- [BeautifulSoup документация](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests документация](https://requests.readthedocs.io/)
- [Anthropic API](https://docs.anthropic.com/)
- [Django ORM](https://docs.djangoproject.com/en/5.0/topics/db/queries/)
- [Evomi](https://evomi.com/)

---

*Создано: 2026-04-07*
*Автор: Claude Code*
