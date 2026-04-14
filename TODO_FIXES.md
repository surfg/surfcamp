# SurfCamp — список фиксов для автономного выполнения

**Режим выполнения:** Claude Code, `--dangerously-skip-permissions`.
**Цель:** Все пункты ниже должны быть пофикшены в коде, закоммичены, задеплоены на прод-сервер `146.190.31.111:8080` и вручную протестированы.

## Контекст и доступы

- **Прод-сервер:** `ssh root@146.190.31.111`
- **Путь проекта на сервере:** определить через `find / -name "docker-compose.prod.yml" 2>/dev/null` (вероятно `/home/surfcamp` или `/root/surfcamp`).
- **URL прода:** http://146.190.31.111:8080
- **Админка:** http://146.190.31.111:8080/admin/ (логин узнать у пользователя, либо `cat backend/.env` на сервере)
- **Деплой-цикл:**
  ```bash
  git add -A && git commit -m "..." && git push origin main
  ssh root@146.190.31.111 "cd <PROJECT_PATH> && git pull && docker compose -f docker-compose.prod.yml up -d --build"
  ```
- **Тест-кемп:** `Endless summer` — id 356, slug `endless-summer`. Использовать его для всех проверок «после фикса».

## Общие правила

1. **Перед каждым фиксом** — прочитать соответствующие файлы целиком, не предполагать структуру.
2. **После каждого фикса** — задеплоить на сервер и проверить вживую через curl/браузер. Не двигаться к следующему пункту, пока текущий не работает на проде.
3. **Если фикс ломает что-то** — откатиться (`git revert`), не оставлять полу-сломанное состояние.
4. **Логи сервера** при любой ошибке: `ssh root@146.190.31.111 "docker logs surfcamp_backend --tail 200"`.
5. **Миграции:** после `docker compose up -d --build` всегда `docker compose exec backend python manage.py migrate` и проверить `showmigrations`.
6. **Не коммитить** `.env`, `db.sqlite3`, `*.log`, `media/`, `__pycache__`, `venv/`.

---

## ФИКС 1 — Ошибка 500 при сохранении кемпа в админке

**Файл-источник:** скриншот «Баги на админке», URL `/admin/camps/surfcamp/356/change/`
**Симптом:** «Сохранить» → 500. «Сохранить и продолжить редактирование» → «страница недоступна».

### Диагностика (обязательна перед фиксом)

```bash
ssh root@146.190.31.111 "docker logs surfcamp_backend --tail 500 2>&1 | grep -A 30 'Internal Server Error\|Traceback\|ERROR'"
ssh root@146.190.31.111 "docker logs surfcamp_nginx --tail 200 2>&1 | grep -i 'error\|413\|502\|504'"
```

Записать реальный traceback. От него зависит точечный фикс.

### Гипотезы и фикс

Скорее всего одна из трёх причин:

**A) nginx режет тело запроса (413 Request Entity Too Large)**
- В [nginx/](nginx/) (или `nginx/nginx.conf` / `default.conf`) добавить в `server {}`:
  ```
  client_max_body_size 100M;
  client_body_timeout 300s;
  proxy_read_timeout 300s;
  proxy_send_timeout 300s;
  ```

**B) Django режет число полей формы (TooManyFieldsSent)**
- В [backend/config/settings.py](backend/config/settings.py) добавить:
  ```python
  DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
  DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024
  FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024
  ```

**C) Падает синхронная оптимизация картинок при сохранении**
- Найти место, где вызывается `optimize_images` на save (если есть сигнал/save-override) и обернуть в try/except с логированием — провал оптимизации не должен ронять запрос.

Применить **все три** превентивно (они не конфликтуют), плюс точечный фикс из traceback'а.

### Тест

1. Деплой.
2. Зайти в админку → кемп 356 → загрузить 5+ фото в инлайн `CampImage`, добавить инструктора → «Сохранить».
3. Ожидаемо: 302-редирект на список, никаких 500.
4. Повторить с «Сохранить и продолжить редактирование».
5. Проверить логи: `docker logs surfcamp_backend --tail 100` — без traceback'ов.
6. ✅ Готово, когда оба варианта save проходят без ошибок.

---

## ФИКС 2 — Картинки из админки не появляются на фронте

**Файл-источник:** скриншот «Баг — система не грузит картинки из админки на фронт».
**Корень:** [backend/camps/serializers.py:73-90](backend/camps/serializers.py#L73-L90) — `_get_optimized_url` всегда отдаёт путь к WebP-копии в `/media/optimized/...`. После загрузки через админку этой копии нет → 404 на фронте.

### Фикс

В [backend/camps/serializers.py](backend/camps/serializers.py):

1. В `_get_optimized_url` проверять существование оптимизированного файла на диске (через `default_storage.exists(optimized_path)` или `os.path.exists(os.path.join(MEDIA_ROOT, optimized_path))`).
2. Если оптимизированной копии нет — возвращать URL на оригинал: `request.build_absolute_uri(obj.image.url)`.
3. То же исправить в `CampListSerializer.get_main_image` ([serializers.py:148](backend/camps/serializers.py#L148)).

### Дополнительно — авто-оптимизация при загрузке

В [backend/camps/models.py](backend/camps/models.py) добавить `post_save` сигнал на `CampImage`, который синхронно генерирует thumb/medium/large копии. Логику взять из существующего [backend/optimize_images.py](backend/optimize_images.py). Обернуть в try/except — провал оптимизации не должен валить save.

Подключить сигнал в [backend/camps/apps.py](backend/camps/apps.py) через `ready()`.

### Тест

1. Деплой.
2. Запустить разово: `docker compose exec backend python optimize_images.py` — чтобы существующие картинки получили WebP-копии.
3. В админке зайти в кемп `Endless summer` (356), убедиться что фото загружены.
4. Открыть http://146.190.31.111:8080/camps/endless-summer — фото должны быть видны.
5. Загрузить НОВУЮ картинку через админку → сохранить → проверить, что она появилась на фронте сразу (без ручного запуска оптимизатора).
6. В DevTools → Network: ни один запрос за картинками не должен возвращать 404.
7. ✅ Готово, когда фото видны и для старых, и для свежезагруженных кемпов.

---

## ФИКС 3 — Широта/Долгота не должны быть обязательными

**Файл-источник:** скриншот «Убрать широту и долготу из обязательных полей».
**Корень:** [backend/camps/models.py:98-99](backend/camps/models.py#L98-L99) — у `SurfCamp.latitude/longitude` нет `null=True, blank=True`.

### Фикс

1. В [backend/camps/models.py:98-99](backend/camps/models.py#L98-L99) добавить `null=True, blank=True` к обоим полям.
2. Сгенерировать миграцию: `docker compose exec backend python manage.py makemigrations camps` (запустить локально или на сервере).
3. На фронте, где рендерится карта (искать `latitude`/`longitude` в [frontend/src/](frontend/src/)) — добавить условный рендер: если координат нет, не показывать карту (или показывать карту региона).
4. **Не** ломать существующие записи — миграция должна быть аддитивной (просто `AlterField`).

### Тест

1. Деплой + `python manage.py migrate`.
2. Админка → «Добавить кемп» → заполнить только обязательные поля БЕЗ широты/долготы → сохранить. Не должно быть валидационной ошибки на этих полях.
3. Открыть на фронте кемп без координат — страница не должна падать (нет белого экрана), карта либо скрыта, либо плейсхолдер.
4. Открыть кемп с координатами (Endless summer, если есть) — карта работает как раньше.
5. ✅ Готово.

---

## ФИКС 4 — Защита от дублей кемпов + UX-инструкция

**Файл-источник:** SURFCAMP «Как править инфо о кемпах внутри уже загруженных?».
**Контекст:** пользователь не нашёл, как редактировать существующий кемп, и плодил дубли.

### Фикс

1. **В [backend/camps/models.py](backend/camps/models.py)** в `SurfCamp.Meta` добавить:
   ```python
   constraints = [
       models.UniqueConstraint(fields=['name', 'region'], name='unique_camp_name_per_region')
   ]
   ```
   Сгенерировать миграцию.

2. **Перед миграцией** — найти существующие дубли и решить вручную:
   ```bash
   docker compose exec backend python manage.py shell -c "
   from camps.models import SurfCamp
   from django.db.models import Count
   dups = SurfCamp.objects.values('name','region').annotate(c=Count('id')).filter(c__gt=1)
   for d in dups: print(d)
   "
   ```
   Если дубли есть — показать пользователю список и спросить, какие удалить. Не удалять автоматически.

3. **Расширить поиск в админке** — в [backend/camps/admin.py:84](backend/camps/admin.py#L84) добавить в `search_fields`: `'slug'`, `'region__name'`, `'region__country__name'`.

4. **Создать короткую инструкцию** [docs/admin_guide.md](docs/admin_guide.md):
   - Скриншот пути: «Камеры → Серф-кемпы → клик по названию для редактирования».
   - Где смотреть существующие кемпы перед созданием нового.

### Тест

1. Деплой + миграция.
2. В админке попытаться создать кемп с именем существующего в том же регионе — должна быть понятная ошибка («такой кемп уже есть»).
3. Поиск в списке кемпов по slug или стране — работает.
4. ✅ Готово.

---

## ФИКС 5 — Slug-URL для всех ссылок и редиректы с числовых

**Файл-источник:** SURFCAMP-20 п.1.
**Контекст:** числовые URL снижают доверие/конверсию. Slug-роут уже работает (`/camps/endless-summer`), нужен аудит и редиректы.

### Аудит (обязателен)

```bash
# Найти все места, где формируется URL кемпа
grep -rn "camps/\${" frontend/src/
grep -rn "/camps/" frontend/src/ --include="*.tsx" --include="*.ts"
grep -rn "camp.id" frontend/src/ --include="*.tsx" --include="*.ts"
```

Проверить:
- Карточки в списке (`CampsPage`).
- Шеринг-кнопки.
- OG/мета-теги (если есть SSR — вряд ли, фронт SPA, но проверить).
- `sitemap.xml` (если есть).

### Фикс

1. Все ссылки во фронте — на `/camps/{slug}`.
2. На бэке добавить эндпоинт-редирект: `/camps/<int:pk>/` → 301 на `/camps/<slug>/` (для уже проиндексированных Google'ом URL).
3. Если slug пустой у каких-то кемпов — заполнить транслитом из `name` (одноразовый management command).
4. **Sitemap.xml** — если его нет, добавить через `django.contrib.sitemaps` со всеми активными кемпами + страны (см. ФИКС 7).

### Тест

1. Открыть список — навести на карточку, в статус-баре браузера видно `/camps/<slug>`, не `/camps/<id>`.
2. Открыть `http://146.190.31.111:8080/camps/356` — должен быть 301-редирект на `/camps/endless-summer`.
3. `curl -I http://146.190.31.111:8080/camps/356` — `HTTP/1.1 301 Moved Permanently`.
4. ✅ Готово.

---

## ФИКС 6 — Бронирование «только проживание» (Bed & Breakfast)

**Файл-источник:** SURFCAMP-20 п.2.
**Контекст:** В модели уже есть `has_bed_breakfast` и `bed_breakfast_price` ([models.py:104-105](backend/camps/models.py#L104-L105)) — половина готова.

### Фикс

1. **Бэк — модель `Booking`** (в [backend/bookings/](backend/bookings/)) добавить поле:
   ```python
   PACKAGE_CHOICES = [('full', 'С уроками'), ('bnb', 'Только проживание')]
   package_type = models.CharField(max_length=10, choices=PACKAGE_CHOICES, default='full')
   ```
   Миграция.

2. **Бэк — расчёт цены** в сериализаторе/вьюхе бронирования: если `package_type='bnb'` — `total = bed_breakfast_price * nights` (и валидировать, что `has_bed_breakfast=True` у кемпа).

3. **Фронт — `CampDetailPage`:** под блоком цены добавить переключатель «С уроками / Только проживание (B&B)», показывать только если `camp.has_bed_breakfast`. При переключении пересчитывать итоговую цену.

4. **Фронт — `CampsPage` фильтр:** добавить чекбокс «Доступно только проживание» (фильтр `?has_bed_breakfast=true`).

5. **Бэк — фильтрация:** в `views.py` `SurfCampViewSet` добавить `has_bed_breakfast` в `filterset_fields`.

### Тест

1. В админке у Endless summer выставить `has_bed_breakfast=True`, `bed_breakfast_price=50`.
2. На фронте `/camps/endless-summer` — переключатель появился, цена меняется.
3. Сделать тестовое бронирование с `package_type=bnb`. В админке заявка появилась с правильным типом и ценой.
4. На `/camps?has_bed_breakfast=true` — в списке только кемпы с этим флагом.
5. ✅ Готово.

---

## ФИКС 7 — Гео-лендинги для рекламы (`/bali`, `/portugal`, ...)

**Файл-источник:** SURFCAMP-16, формат `yoursite.ru/bali`.

### Фикс

1. **Бэк — расширить модель `Country`** ([backend/camps/models.py](backend/camps/models.py)) полями:
   - `slug = SlugField(unique=True)` (если нет)
   - `landing_h1 = CharField(max_length=200, blank=True)`
   - `landing_intro = TextField(blank=True)`
   - `landing_faq = JSONField(default=list, blank=True)` — список `[{q, a}]`
   - `seo_title = CharField(max_length=200, blank=True)`
   - `seo_description = CharField(max_length=300, blank=True)`

   Миграция. В админке `CountryAdmin` добавить эти поля в форму.

2. **Бэк — эндпоинт** `GET /api/countries/<slug>/landing/` — возвращает Country + список активных кемпов в этой стране (топ по rating).

3. **Фронт — роут** `/:countrySlug` (например `/bali`). Реализовать `CountryLandingPage`:
   - H1, intro-текст
   - Список топ-кемпов с CTA
   - FAQ-аккордеон
   - Уникальные `<title>` и `<meta description>` через `react-helmet-async` (или установить, если нет).

4. **Конфликт роутов:** убедиться, что `/:countrySlug` НЕ перехватывает существующие роуты (`/camps`, `/about` и т.п.). В React Router расположить его последним; альтернатива — whitelist стран в роуте.

5. **Заполнить контентом** топ-5 стран: Bali, Portugal, Sri Lanka, Maldives, Thailand. Ввести базовый текст через админку (или populate-script).

### Тест

1. Открыть http://146.190.31.111:8080/bali — рендерится лендинг, в `<title>` SEO-заголовок, виден список кемпов на Бали.
2. `view-source` страницы — мета-теги уникальные.
3. Существующие роуты не сломались: `/camps`, `/camps/endless-summer`, `/admin/`.
4. ✅ Готово.

---

## ФИКС 8 — Подтвердить SURFCAMP-12 (Язык обучения в фильтрах)

**Статус:** уже сделано в коммите `dd3f328`.

### Тест

1. Открыть http://146.190.31.111:8080/camps — фильтр «Язык обучения» виден.
2. Применить — список фильтруется.
3. Открыть карточку кемпа — теги языков отображаются.
4. ✅ Готово, отметить в трекере как закрытое.

---

## ИТОГОВАЯ ПРИЁМКА (после всех фиксов)

Прогнать сквозной сценарий:

1. ✅ Создать новый кемп в админке без широты/долготы — сохраняется.
2. ✅ Загрузить 5 фото и 3 инструкторов — сохраняется без 500.
3. ✅ Открыть кемп на фронте по slug — фото видны, карта корректна.
4. ✅ Попытка создать дубль — блокируется.
5. ✅ Открыть `/camps/<id>` — редирект на slug.
6. ✅ `/bali` — лендинг открывается с SEO-тегами.
7. ✅ Бронирование B&B — работает, цена корректная.
8. ✅ Фильтр по языку обучения — работает.
9. ✅ `docker logs surfcamp_backend --tail 200` — нет traceback'ов после полного прохода.

**Только после успеха всех 9 пунктов** — отчитаться пользователю с кратким списком: что сделано, что протестировано, ссылки на коммиты.

## Откаты

Если какой-то фикс вызывает регрессию на проде и быстро не чинится:
```bash
ssh root@146.190.31.111 "cd <PROJECT_PATH> && git log --oneline -10"
# выбрать последний рабочий коммит
ssh root@146.190.31.111 "cd <PROJECT_PATH> && git revert <bad_commit> && git push && docker compose -f docker-compose.prod.yml up -d --build"
```

И сразу написать пользователю, что откатили и почему.
