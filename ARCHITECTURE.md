# SurfSelect - Архитектура проекта

Подробная документация архитектуры приложения для бронирования серф-кемпов.

## Содержание

1. [Обзор проекта](#обзор-проекта)
2. [Структура проекта](#структура-проекта)
3. [Backend (Django)](#backend-django)
4. [Frontend (React)](#frontend-react)
5. [База данных](#база-данных)
6. [API](#api)
7. [Локализация](#локализация)
8. [Сборка и запуск](#сборка-и-запуск)
9. [Как работает парсинг данных](#как-работает-парсинг-данных)

---

## Обзор проекта

**SurfSelect** - это веб-приложение для поиска, сравнения и бронирования серф-кемпов по всему миру.

### Технологический стек

| Компонент | Технология |
|-----------|------------|
| Backend | Django 5.x + Django REST Framework |
| Frontend | React 18 + TypeScript + Vite |
| База данных | SQLite (dev) / PostgreSQL (prod) |
| Карты | Leaflet + OpenStreetMap |
| Стили | Inline CSS (без фреймворков) |
| Иконки | Lucide React |

---

## Структура проекта

```
surfcamp/
├── backend/                    # Django приложение
│   ├── config/                 # Настройки Django
│   │   ├── settings.py         # Основные настройки
│   │   ├── urls.py             # Главный роутер URL
│   │   └── wsgi.py             # WSGI конфигурация
│   ├── camps/                  # Приложение "Кемпы"
│   │   ├── models.py           # Модели данных
│   │   ├── views.py            # API views
│   │   ├── serializers.py      # DRF сериализаторы
│   │   ├── admin.py            # Админка Django
│   │   └── urls.py             # URL маршруты
│   ├── spots/                  # Приложение "Серф-споты"
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── admin.py
│   ├── bookings/               # Приложение "Бронирования"
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── admin.py
│   ├── populate_world_camps.py # Скрипт заполнения данных
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/                   # React приложение
│   ├── src/
│   │   ├── components/         # React компоненты
│   │   ├── pages/              # Страницы приложения
│   │   ├── contexts/           # React контексты
│   │   ├── lib/                # Утилиты и API клиент
│   │   ├── types/              # TypeScript типы
│   │   ├── App.tsx             # Главный компонент
│   │   └── main.tsx            # Точка входа
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── tasks.md                    # Список задач
├── check.md                    # Чеклист проверки
└── ARCHITECTURE.md             # Этот файл
```

---

## Backend (Django)

### Приложения Django

#### 1. `camps` - Серф-кемпы

**Модели:**

```python
# Страна
class Country(models.Model):
    name = CharField         # Русское название ("Индонезия")
    name_en = CharField      # Английское название ("Indonesia")
    code = CharField         # ISO код ("IDN")
    image = ImageField       # Изображение флага/страны
    description = TextField  # Описание
    is_active = BooleanField

# Регион
class Region(models.Model):
    country = ForeignKey(Country)
    name = CharField         # "Бали"
    name_en = CharField      # "Bali"
    latitude = DecimalField
    longitude = DecimalField

# Тип доски
class BoardType(models.Model):
    name = CharField         # "Софттопы"
    name_en = CharField      # "Soft tops"
    icon = CharField
    description = TextField

# Удобства
class Amenity(models.Model):
    name = CharField
    name_en = CharField
    icon = CharField
    category = CharField     # 'accommodation', 'food', 'activities', 'services'

# Серф-кемп (главная модель)
class SurfCamp(models.Model):
    # Основное
    name = CharField
    slug = SlugField
    region = ForeignKey(Region)

    # Описание
    short_description = CharField
    description = TextField
    history = TextField

    # Геолокация
    latitude = DecimalField
    longitude = DecimalField
    address = CharField

    # Цены
    price_per_night = DecimalField
    price_per_lesson = DecimalField
    bed_breakfast_price = DecimalField
    board_rental_price = DecimalField

    # Характеристики
    skill_levels = JSONField       # ['beginner', 'intermediate', 'advanced']
    board_types = ManyToMany(BoardType)
    amenities = ManyToMany(Amenity)

    # Флаги
    has_pool = BooleanField
    has_yoga = BooleanField
    has_restaurant = BooleanField
    has_parties = BooleanField
    has_bed_breakfast = BooleanField
    board_rental_available = BooleanField

    # Контакты
    website = URLField
    email = EmailField
    phone = CharField
    instagram = CharField
    whatsapp = CharField

    # Рейтинг
    rating = DecimalField
    reviews_count = PositiveIntegerField
    is_featured = BooleanField

# Инструктор
class Instructor(models.Model):
    camp = ForeignKey(SurfCamp)
    name = CharField
    photo = ImageField
    bio = TextField
    experience_years = PositiveIntegerField
    certifications = TextField
    languages = CharField
    is_head_coach = BooleanField

# Активность/Экскурсия
class Activity(models.Model):
    camp = ForeignKey(SurfCamp)
    name = CharField
    name_en = CharField
    description = TextField
    price = DecimalField
    is_included = BooleanField

# Отзыв
class Review(models.Model):
    camp = ForeignKey(SurfCamp)
    author_name = CharField
    author_country = CharField
    rating = PositiveIntegerField  # 1-5
    title = CharField
    text = TextField
    surf_level = CharField
    is_verified = BooleanField
    is_published = BooleanField
```

#### 2. `spots` - Серф-споты

```python
class SurfSpot(models.Model):
    name = CharField
    slug = SlugField
    region = ForeignKey(Region)
    camps = ManyToMany(SurfCamp)  # Ближайшие кемпы

    # Геолокация
    latitude = DecimalField
    longitude = DecimalField

    # Характеристики волны
    wave_direction = CharField   # 'left', 'right', 'both'
    wave_type = CharField        # 'beach', 'reef', 'point'
    wave_height_min = DecimalField
    wave_height_max = DecimalField

    # Условия
    skill_levels = JSONField
    best_tide = CharField
    best_swell = CharField
    best_wind = CharField
    best_season = CharField
    crowd_level = CharField      # 'low', 'medium', 'high', 'very_high'

    # Опасности
    hazards = TextField
    has_rocks = BooleanField
    has_reef = BooleanField
    has_currents = BooleanField
    has_sharks = BooleanField

    # Инфраструктура
    has_parking = BooleanField
    has_showers = BooleanField
    has_rentals = BooleanField
    has_cafe = BooleanField
    has_lifeguard = BooleanField
```

#### 3. `bookings` - Бронирования

```python
class Booking(models.Model):
    booking_number = CharField  # "SC260328X355"
    camp = ForeignKey(SurfCamp, on_delete=PROTECT)

    # Даты
    check_in = DateField
    check_out = DateField

    # Гости
    adults = PositiveIntegerField
    children = PositiveIntegerField

    # Опции
    include_breakfast = BooleanField
    include_lessons = BooleanField
    lessons_count = PositiveIntegerField
    include_board_rental = BooleanField

    # Цены (сохраняются на момент бронирования)
    price_per_night = DecimalField
    breakfast_total = DecimalField
    lessons_total = DecimalField
    board_rental_total = DecimalField
    subtotal = DecimalField
    service_fee = DecimalField  # 10%
    total_price = DecimalField

    # Статусы
    status = CharField  # 'pending', 'confirmed', 'paid', 'cancelled', 'completed'
    payment_status = CharField

    # Дополнительно
    special_requests = TextField
    arrival_time = TimeField

class Guest(models.Model):
    booking = ForeignKey(Booking)
    is_primary = BooleanField
    first_name = CharField
    last_name = CharField
    email = EmailField
    phone = CharField
    country = CharField
    city = CharField
    surf_level = CharField
    emergency_name = CharField
    emergency_phone = CharField

class Payment(models.Model):
    booking = ForeignKey(Booking)
    amount = DecimalField
    method = CharField  # 'card', 'paypal', 'bank_transfer'
    status = CharField
    transaction_id = CharField
    card_last_four = CharField
    card_brand = CharField
```

### Django Admin

Админка доступна по адресу `/admin/` с полным управлением:

- **Кемпы**: CRUD, фильтры по стране/региону, поиск
- **Инструкторы**: Привязка к кемпам
- **Отзывы**: Модерация (is_published)
- **Бронирования**: Просмотр, статусы
- **Страны/Регионы**: Справочники

Создание суперпользователя:
```bash
python manage.py createsuperuser
```

### Views и API

```python
# camps/views.py

class SurfCampViewSet(ReadOnlyModelViewSet):
    """
    GET /api/camps/           - Список кемпов (пагинация, фильтры)
    GET /api/camps/{slug}/    - Детали кемпа
    GET /api/camps/featured/  - Рекомендуемые
    GET /api/camps/map_data/  - Данные для карты
    """
    queryset = SurfCamp.objects.filter(is_active=True)
    filterset_class = SurfCampFilter
    lookup_field = 'slug'

# Фильтры
class SurfCampFilter(FilterSet):
    country = CharFilter        # ?country=IDN
    region = NumberFilter       # ?region=19
    min_price = NumberFilter    # ?min_price=50
    max_price = NumberFilter    # ?max_price=200
    skill_level = CharFilter    # ?skill_level=beginner
    has_pool = BooleanFilter
    has_yoga = BooleanFilter
    has_parties = BooleanFilter
    has_bed_breakfast = BooleanFilter
    board_rental = BooleanFilter
    board_types = CharFilter    # ?board_types=1,2,3

# Поиск с автодополнением
@api_view(['GET'])
def search_autocomplete(request):
    """
    GET /api/search/?q=bali&lang=ru

    Ищет по:
    - Странам (name, name_en)
    - Регионам (name, name_en)
    - Кемпам (name, short_description)

    Возвращает локализованные названия в зависимости от lang
    """
```

---

## Frontend (React)

### Страницы

| Страница | Путь | Описание |
|----------|------|----------|
| HomePage | `/` | Главная с поиском и featured кемпами |
| CampsPage | `/camps` | Список всех кемпов с фильтрами |
| CampDetailPage | `/camps/:slug` | Детальная страница кемпа |
| BookingPage | `/camps/:slug/book` | Шаг 1: Выбор дат и опций |
| GuestInfoPage | `/booking/:number/guests` | Шаг 2: Данные гостей |
| PaymentPage | `/booking/:number/payment` | Шаг 3: Оплата |
| ConfirmationPage | `/booking/:number/confirmation` | Шаг 4: Подтверждение |
| MapPage | `/map` | Интерактивная карта |
| SpotsPage | `/spots` | Список серф-спотов |
| SpotDetailPage | `/spots/:slug` | Детали спота |

### Компоненты

```
src/components/
├── Header.tsx           # Навигация, лого, языковой переключатель
├── Footer.tsx           # Подвал сайта
├── SearchBar.tsx        # Поиск с автокомплитом
├── CampCard.tsx         # Карточка кемпа в списке
├── LanguageSwitcher.tsx # Переключатель EN/RU
└── ...
```

### Контексты

```typescript
// contexts/LanguageContext.tsx

type Language = 'en' | 'ru';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;           // Перевод по ключу
  getLocalized: (ru, en) => string;     // Выбор локализации
}

// Использование:
const { t, language } = useLanguage();
<h1>{t('hero.title')}</h1>  // "Find Your Perfect" / "Найди свой идеальный"
```

### API клиент

```typescript
// lib/api.ts

// Кемпы
getCamps(filters)        // Список с фильтрами
getCamp(slug)            // Детали
getFeaturedCamps()       // Рекомендуемые
getCampsMapData()        // Для карты

// Поиск
searchAutocomplete(query, lang)  // Автокомплит

// Бронирование
createBooking(data)      // Создать
getBooking(number)       // Получить
updateBookingGuests()    // Обновить гостей
processPayment()         // Оплата
cancelBooking()          // Отмена

// Расчёт цены (клиентский)
calculatePricePreview(camp, nights, adults, children, options)
```

### TypeScript типы

```typescript
// types/index.ts

interface SurfCamp {
  id: number;
  name: string;
  slug: string;
  short_description: string;
  region_name: string;
  country_name: string;
  country_code: string;
  latitude: number;
  longitude: number;
  price_per_night: number;
  skill_levels: string[];
  rating: number;
  reviews_count: number;
  has_pool: boolean;
  has_yoga: boolean;
  is_featured: boolean;
  main_image: string | null;
  // ...
}

interface SurfCampDetail extends SurfCamp {
  region: Region;
  country: Country;
  description: string;
  history: string;
  board_types: BoardType[];
  amenities: Amenity[];
  instructors: Instructor[];
  activities: Activity[];
  reviews: Review[];
  spots: SurfSpot[];
  // ...
}

interface Booking {
  booking_number: string;
  camp: number;
  check_in: string;
  check_out: string;
  adults: number;
  children: number;
  total_price: number;
  status: 'pending' | 'confirmed' | 'paid' | 'cancelled';
  guests: Guest[];
  // ...
}
```

---

## База данных

### Текущее состояние

| Таблица | Количество записей |
|---------|-------------------|
| Countries | 15 стран |
| Regions | 59 регионов |
| SurfCamps | 263 кемпа |
| SurfSpots | 24 спота |
| BoardTypes | 5 типов |
| Amenities | 10 удобств |
| Instructors | ~800 инструкторов |
| Reviews | ~1500 отзывов |

### Миграции

```bash
# Создать миграции
python manage.py makemigrations

# Применить миграции
python manage.py migrate
```

---

## API

### Основные эндпоинты

```
GET  /api/camps/                    # Список кемпов
GET  /api/camps/{slug}/             # Детали кемпа
GET  /api/camps/featured/           # Рекомендуемые
GET  /api/camps/map_data/           # Данные для карты

GET  /api/spots/                    # Список спотов
GET  /api/spots/{slug}/             # Детали спота
GET  /api/spots/map_data/           # Данные для карты

GET  /api/countries/                # Список стран
GET  /api/regions/                  # Список регионов
GET  /api/filters/                  # Опции для фильтров
GET  /api/search/?q=&lang=          # Поиск с автокомплитом

POST /api/bookings/                 # Создать бронирование
GET  /api/bookings/{number}/        # Получить бронирование
PUT  /api/bookings/{number}/update_guests/  # Обновить гостей
POST /api/bookings/{number}/process_payment/  # Оплата
POST /api/bookings/{number}/cancel/   # Отмена
```

### Фильтры кемпов

```
?country=IDN                # По стране (ISO код)
?region=19                  # По региону (ID)
?min_price=50               # Мин. цена
?max_price=200              # Макс. цена
?skill_level=beginner       # Уровень серфинга
?has_pool=true              # С бассейном
?has_yoga=true              # С йогой
?has_parties=true           # С вечеринками
?has_bed_breakfast=true     # Только B&B
?board_rental=true          # С арендой досок
?board_types=1,2,3          # По типам досок
?search=canggu              # Текстовый поиск
?ordering=price_per_night   # Сортировка
```

---

## Локализация

### Поддерживаемые языки

- **EN** - English (по умолчанию)
- **RU** - Русский

### Как работает

1. **Frontend**: Все тексты UI хранятся в `LanguageContext.tsx`
2. **Backend**: Модели имеют поля `name` (RU) и `name_en` (EN)
3. **API**: Параметр `?lang=ru` возвращает локализованные названия

### Добавление нового перевода

```typescript
// contexts/LanguageContext.tsx

const translations = {
  'new.key': { en: 'English text', ru: 'Русский текст' },
  // ...
};

// Использование
const { t } = useLanguage();
<span>{t('new.key')}</span>
```

---

## Сборка и запуск

### Требования

- Python 3.11+
- Node.js 18+
- npm или yarn

### Backend

```bash
cd backend

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или venv\Scripts\activate  # Windows

# Установить зависимости
pip install -r requirements.txt

# Миграции
python manage.py migrate

# Заполнить данными
python manage.py shell < populate_world_camps.py

# Создать админа
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver 8000
```

### Frontend

```bash
cd frontend

# Установить зависимости
npm install

# Режим разработки
npm run dev

# Сборка для продакшена
npm run build

# Превью сборки
npm run preview
```

### Production

```bash
# Backend (с gunicorn)
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Frontend (статика)
npm run build
# Раздать dist/ через nginx
```

---

## Как работает парсинг данных

### Откуда данные?

Данные для серф-кемпов **генерируются программно** в скрипте `populate_world_camps.py`.

### Принцип работы

1. **Страны и регионы** - Захардкожены реальные данные:
   - 15 популярных серф-стран (Индонезия, Португалия, Марокко и т.д.)
   - 59 регионов с реальными координатами (Бали, Пениш, Тагазут и т.д.)

2. **Названия кемпов** - Шаблоны по регионам:
   ```python
   camp_names = {
       'Bali': ['Padang Padang Surf Camp', 'Uluwatu Wave Riders', ...],
       'Peniche': ['Supertubos Surf Camp', 'Baleal Surf House', ...],
       # ...
   }
   ```

3. **Характеристики** - Рандомизированы:
   ```python
   base_price = random.randint(35, 200)
   has_pool = random.random() > 0.6
   has_yoga = random.random() > 0.5
   rating = round(random.uniform(4.0, 5.0), 1)
   ```

4. **Координаты** - Реальные центры регионов + небольшой сдвиг:
   ```python
   latitude = region.latitude + random.uniform(-0.05, 0.05)
   longitude = region.longitude + random.uniform(-0.05, 0.05)
   ```

5. **Инструкторы** - Случайные имена из списка:
   ```python
   instructor_names = ["Carlos", "Maria", "João", "Made", "Wayan", ...]
   ```

6. **Отзывы** - Шаблонные тексты:
   ```python
   review_texts = [
       "Amazing experience! The waves were perfect...",
       "Best surf camp I've ever been to...",
       # ...
   ]
   ```

### Запуск парсинга

```bash
cd backend
source venv/bin/activate
python manage.py shell < populate_world_camps.py
```

### Что создаётся

| Сущность | Количество |
|----------|------------|
| Страны | 15 |
| Регионы | 59 |
| Кемпы | 263 |
| Инструкторы | ~800 |
| Активности | ~700 |
| Отзывы | ~1500 |
| Типы досок | 5 |
| Удобства | 10 |

### Добавление реальных данных

Для добавления реальных кемпов можно:

1. **Через админку**: `/admin/camps/surfcamp/add/`
2. **Через API**: `POST /api/camps/` (нужна авторизация)
3. **Через скрипт**: Модифицировать `populate_world_camps.py`

### Парсинг реальных источников

Для реального парсинга можно использовать:
- **Surfline** - API спотов
- **Booking.com** - API отелей
- **Google Places** - Информация о местах

Пример структуры парсера:
```python
import requests
from bs4 import BeautifulSoup

def parse_real_camps():
    # 1. Получить список кемпов с агрегатора
    # 2. Для каждого кемпа получить детали
    # 3. Геокодировать адрес
    # 4. Сохранить в базу
    pass
```

---

## Полезные команды

```bash
# Backend
python manage.py shell              # Django shell
python manage.py dbshell            # SQL shell
python manage.py showmigrations     # Список миграций
python manage.py dumpdata camps     # Экспорт данных
python manage.py loaddata camps     # Импорт данных

# Frontend
npm run lint                        # Проверка кода
npm run type-check                  # Проверка типов
npm run build                       # Сборка

# Тестирование API
curl http://localhost:8000/api/camps/
curl "http://localhost:8000/api/search/?q=bali&lang=ru"
```

---

## Контакты и поддержка

- **GitHub Issues**: Для багов и предложений
- **Документация API**: `/api/docs/` (если включён Swagger)

---

*Документация обновлена: 2026-03-29*
