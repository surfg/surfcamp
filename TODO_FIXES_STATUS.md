# Статус выполнения TODO_FIXES.md

**Контекст для следующего инстанса Claude:** Пользователь перезапустит тебя с `--dangerously-skip-permissions`. Твоя задача — прогнать весь `TODO_FIXES.md` по плану ниже и в конце выдать один общий отчёт. Не отчитывайся после каждого фикса.

## Режим работы (согласовано с пользователем)

1. Все 8 фиксов делаешь **локально** подряд, с локальным smoke-тестом.
2. **Один** общий деплой на прод в самом конце.
3. На проде — финальный чеклист из секции «ИТОГОВАЯ ПРИЁМКА» в `TODO_FIXES.md`.
4. Отчёт пользователю — **один** в самом конце.
5. Если упёрся в неочевидное решение — останавливайся и спрашивай, не импровизируй.

## Ключевые факты окружения

- Прод-сервер: `ssh root@146.190.31.111`, путь проекта `/root/surfcamp`.
- URL прода: `http://146.190.31.111:8080`, админка: `/admin/`.
- Тест-кемп: `Endless summer`, id 356, slug `endless-summer`.
- Контейнеры: `surfcamp_frontend`, `surfcamp_backend`, `surfcamp_nginx`, `surfcamp_db`.
- Git remote: `https://github.com/surfg/surfcamp.git` (origin).

## ✅ Уже сделано в этой сессии

- Прочитан весь `TODO_FIXES.md`.
- Проверена структура git: локально и на проде HEAD = `dd3f328`, на origin/main = `e57bf97` (отстаёт на 5 коммитов).
- Проверены логи прод-бэка: **свежих traceback'ов по 500 нет** — применяй все три превентивных фикса FIX 1 вслепую (согласовано с пользователем).
- Создан TaskList с 8 задачами (но тасклист сессионный, у тебя будет свой — пересоздай при необходимости).

## ⚠️ Первое, что нужно сделать после рестарта

**Запушить 5 локальных коммитов в `origin/main`** (пользователь согласовал, блокер — не было разрешения на `git push`):

```bash
git log origin/main..HEAD --oneline   # должно быть 5 коммитов: dd3f328, e718578, 3934d8a, 4316f53, e6f8d33
git push origin main
```

Если `git status` покажет `backend/populate_data.py` как modified и `TODO_FIXES.md` / `TODO_FIXES_STATUS.md` как untracked — **не коммить** их сейчас, они к фиксам не относятся. Разберёшься с ними после всех 8 фиксов (скорее всего: `populate_data.py` оставить как есть, `TODO_FIXES*.md` можно закоммитить отдельно или сразу с первым фиксом).

## План по фиксам (из TODO_FIXES.md)

Все 8 — в статусе **TODO**. Дальше идёт краткая выжимка с уже найденными файлами-якорями, чтобы не тратить токены на повторный поиск.

### FIX 1 — 500 при сохранении в админке
Применить **все три** превентивно:
- **nginx**: в `nginx/` найти конфиг (`nginx.conf` или `default.conf`), в `server {}` добавить `client_max_body_size 100M; client_body_timeout 300s; proxy_read_timeout 300s; proxy_send_timeout 300s;`
- **Django settings**: в `backend/config/settings.py` добавить `DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000`, `DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024`, `FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024`.
- **Image optimize try/except**: если есть save-override или сигнал с вызовом `optimize_images` — обернуть.

Локальный тест: `docker compose up`, загрузить 10+ фото через админку.

### FIX 2 — картинки из админки не показываются
- `backend/camps/serializers.py:73-90` — `_get_optimized_url`: проверять `os.path.exists(os.path.join(MEDIA_ROOT, optimized_path))`, если нет — отдавать оригинал `obj.image.url`.
- То же в `CampListSerializer.get_main_image` (~строка 148).
- Добавить `post_save` сигнал на `CampImage` в `backend/camps/models.py`, логику взять из `backend/optimize_images.py`. Подключить в `backend/camps/apps.py` через `ready()`. Обернуть в try/except.

### FIX 3 — lat/lng необязательные
- `backend/camps/models.py:98-99` — добавить `null=True, blank=True` к `latitude` и `longitude`.
- `python manage.py makemigrations camps`.
- Фронт: найти использование `latitude`/`longitude` в `frontend/src/` (вероятно `CampDetailPage`) — скрыть карту если координат нет.

### FIX 4 — защита от дублей + UX
- `backend/camps/models.py` → `SurfCamp.Meta.constraints = [UniqueConstraint(fields=['name','region'], name='unique_camp_name_per_region')]`.
- **Перед миграцией** проверить дубли через shell (команда в TODO). Если есть — остановись, спроси у пользователя, какие удалять.
- `backend/camps/admin.py:84` — расширить `search_fields` на `'slug'`, `'region__name'`, `'region__country__name'`.
- Создать `docs/admin_guide.md` с коротким how-to.

### FIX 5 — slug URLs + 301 с числовых
- Аудит фронта на `/camps/<id>` (grep команды в TODO).
- Бэкенд: добавить в `urls.py` редирект `/camps/<int:pk>/` → 301 на `/camps/<slug>/`.
- Проверить, что у всех кемпов есть slug (если нет — одноразовый management command).
- Sitemap.xml через `django.contrib.sitemaps` (кемпы + страны).

### FIX 6 — B&B бронирование
- `backend/bookings/models.py` (проверь путь) — добавить `package_type = CharField(choices=[('full','С уроками'),('bnb','Только проживание')], default='full')`. Миграция.
- Сериализатор/view бронирования: если `package_type='bnb'` — `total = camp.bed_breakfast_price * nights`, валидировать `has_bed_breakfast=True`.
- Фронт `CampDetailPage`: переключатель, виден только при `camp.has_bed_breakfast`.
- Фронт `CampsPage`: фильтр-чекбокс `has_bed_breakfast=true`.
- Бэк: в `SurfCampViewSet.filterset_fields` добавить `has_bed_breakfast`.

### FIX 7 — гео-лендинги (БОЛЬШОЙ)
- `Country` модель: поля `slug (unique)`, `landing_h1`, `landing_intro`, `landing_faq (JSONField list)`, `seo_title`, `seo_description`. Админка.
- Эндпоинт `GET /api/countries/<slug>/landing/` — страна + топ-кемпы по rating.
- Фронт роут `/:countrySlug` (разместить **последним** в Router, чтобы не перехватывал `/camps`, `/admin` и т.д.). Whitelist стран безопаснее.
- `react-helmet-async` — установить если нет.
- Страница `CountryLandingPage`: H1, intro, топ-кемпы с CTA, FAQ-аккордеон, уникальные title/meta.
- Заполнить контент для 5 стран: Bali, Portugal, Sri Lanka, Maldives, Thailand (через админку вручную или populate-скрипт).

**⚠️ Это самый объёмный фикс.** Если поймёшь, что на него уйдёт более ~1.5 часа — останови работу и согласуй с пользователем scope.

### FIX 8 — подтверждение SURFCAMP-12
- Уже сделано в `dd3f328`. Просто smoke-тест на проде в финальной приёмке.

## Итоговая приёмка (на проде, после одного общего деплоя)

9 пунктов из секции «ИТОГОВАЯ ПРИЁМКА» в `TODO_FIXES.md`. Прогнать все. Если хоть один падает — откатить последний фикс через `git revert`, задеплоить, попробовать починить.

## Формат финального отчёта пользователю

- Список сделанных фиксов с ссылками на коммиты (хэши).
- Список того, что протестировано на проде (по чеклисту приёмки).
- Список того, что **не** удалось (если есть) с причиной.
- Ссылка на админку `/admin/` и тест-URL `http://146.190.31.111:8080/camps/endless-summer`.

## Команды для деплоя

```bash
git add -A && git commit -m "..." && git push origin main
ssh root@146.190.31.111 "cd /root/surfcamp && git pull && docker compose -f docker-compose.prod.yml up -d --build && docker compose -f docker-compose.prod.yml exec -T backend python manage.py migrate && docker compose -f docker-compose.prod.yml exec -T backend python manage.py showmigrations camps | tail -20"
```

Логи при любой ошибке: `ssh root@146.190.31.111 "docker logs surfcamp_backend --tail 200"`.

## Не забыть

- После FIX 2 — разово запустить на проде `docker compose exec backend python optimize_images.py`, чтобы старые картинки получили WebP-копии.
- Не коммить `.env`, `db.sqlite3`, `*.log`, `media/`, `__pycache__`, `venv/`, `backup_camps_*.json`.
- На проде миграции применять **после** `up -d --build`.
- `populate_data.py` modified локально — оставить как есть, это не связано с фиксами.
