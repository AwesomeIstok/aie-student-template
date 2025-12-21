# S04 – eda_cli: мини-EDA для CSV

Небольшое CLI-приложение для базового анализа CSV-файлов.
Используется в рамках Семинара 03 курса «Инженерия ИИ».

## Требования

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) установлен в систему

## Инициализация проекта

В корне проекта (S03):

```bash
uv sync
```

Эта команда:

- создаст виртуальное окружение `.venv`;
- установит зависимости из `pyproject.toml`;
- установит сам проект `eda-cli` в окружение.

## Запуск CLI

### Краткий обзор

```bash
uv run eda-cli overview data/example.csv
```

Параметры:

- `--sep` – разделитель (по умолчанию `,`);
- `--encoding` – кодировка (по умолчанию `utf-8`).

### Полный EDA-отчёт

```bash
uv run eda-cli report data/example.csv --out-dir reports
uv run eda-cli report data/example.csv --out-dir reports_example  --max-hist-columns 3 --title "Заголовок"
```
Параметры:

- `--out-dir` – каталог для отчёта.
- `--sep` – разделитель (по умолчанию `,`).
- `--encoding` – кодировка (по умолчанию `utf-8`).
- `--max-hist-columns` – максимум числовых колонок для гистограмм (по умолчанию `6`).
- `--title` – заголовок отчёта (по умолчанию `EDA-отчёт`).

В результате в каталоге `reports/` появятся:

- `report.md` – основной отчёт в Markdown;
- `summary.csv` – таблица по колонкам;
- `missing.csv` – пропуски по колонкам;
- `correlation.csv` – корреляционная матрица (если есть числовые признаки);
- `top_categories/*.csv` – top-k категорий по строковым признакам;
- `hist_*.png` – гистограммы числовых колонок;
- `missing_matrix.png` – визуализация пропусков;
- `correlation_heatmap.png` – тепловая карта корреляций.



## Тесты

```bash
uv run pytest -q
```

## HTTP-сервис
Запуск сервиса:
```bash
uv run uvicorn eda_cli.api:app --reload --port 8000
```
URL после запуска сервиса 127.0.0.1:8000/docs
Системный эндпоинт:

/health – простой health проверка сервиса.
Эндпоинты качества:

/quality - принимает агрегированные признаки датасета и возвращает эвристическую оценку качества.
/quality-from-csv - Эндпоинт, который принимает CSV-файл, запускает EDA-ядро (summarize_dataset + missing_table + compute_quality_flags) и возвращает оценку качества данных.
/quality-flags-from-csv - Эндпоинт, который принимает CSV-файл, запускает EDA-ядро (summarize_dataset + missing_table + compute_quality_flags) и возвращает набов флагов качества данных.
Эндпоинт по выводу данных csv:

/head - Эндпоинт, который принимает CSV-файл, параметр n (число выводимых строк) и возвращает первых n строк данных.