# 🏠 house-hunter

Automated apartment scraper for [Funda](https://www.funda.nl) and [Pararius](https://www.pararius.nl). 
Sends email alerts for new listings that match your filters, and includes a small web UI to browse, favourite, and dismiss listings.

## Features

- Scrapes Funda and Pararius for new listings on a schedule
- Filters by price, area, neighbourhood, floor, balcony/roof terrace, and more
- Deduplicates listings that appear on both platforms
- Sends a formatted email digest for each run that finds something new
- Web UI to browse all matched listings, mark favourites, and reject duds

## Structure

```
house-hunter/
├── scraper/              # The scraper + email alerter
│   ├── main.py           # Orchestrator — runs both scrapers, sends email
│   ├── funda_script.py   # Funda scraper
│   ├── pararius_script.py# Pararius scraper
│   ├── utils.py          # Shared settings, filters, helpers
│   └── Dockerfile
├── app/                  # Web UI
│   ├── app.py            # FastAPI backend
│   ├── index.html        # Frontend
│   └── Dockerfile.app
├── docker-compose.yml
└── .env.example
```

## Quickstart

### 1. Clone and configure

```bash
git clone https://github.com/your-username/house-hunter.git
cd house-hunter
cp .env.example .env
# Edit .env with your Gmail credentials
```

### 2. Adjust your search

Edit `scraper/utils.py` to set your filters:

```python
LOCATION  = 'amsterdam'     # City to search in
PRICE_MIN =                 # Min price in EUR
PRICE_MAX = 700_000         # Max price in EUR
AREA_MIN  = 75              # Min living area in m²
AREA_MAX  =                 # Max living area in m²

NEIGHBOURHOODS = [...]      # Leave empty [] to skip neighbourhood filter

REQUIRE_BALCONY_OR_ROOF_TERRACE = True
NOT_FIRST_FLOOR                 = True
SINGLE_STORY                    = True
```

And `scraper/funda_script.py` for Funda-specific filters:

```python
MIN_BEDROOMS = 2
REQUIRE_LIFT = True
```

### 3. Run

**Scraper** (run on a schedule, e.g. via cron or Synology Task Scheduler):

```bash
docker compose run --rm house-hunter            # buy listings
docker compose run --rm house-hunter python main.py rent  # rental listings
```

**Web UI** (always-on):

```bash
docker compose up -d house-hunter-app
# Visit http://localhost:8099
```

## Gmail setup

The scraper sends email via Gmail SMTP. You need a [Gmail App Password](https://myaccount.google.com/apppasswords) — your regular password won't work if you have 2FA enabled (which you should).

Set `EMAIL_FROM`, `EMAIL_PASSWORD`, and `EMAIL_TO` in your `.env` file.

## Deployment on a Synology NAS

1. Place the project in `/volume1/docker/house-hunter/`
2. Open **Container Manager → Project** and point it at `docker-compose.yml`
3. Schedule the scraper via **Control Panel → Task Scheduler**:
   - Task type: User-defined script
   - Command: `docker compose -f /volume1/docker/house-hunter/docker-compose.yml run --rm house-hunter`
   - Schedule: every 30–60 minutes

## Dependencies

- [`pyfunda`](https://github.com/0xMH/pyfunda) — unofficial Funda API wrapper
- [`pypararius`](https://github.com/0xMH/pypararius) — unofficial Pararius API wrapper
- [`fastapi`](https://fastapi.tiangolo.com) + [`uvicorn`](https://www.uvicorn.org) — web UI backend

> **Note:** Both scraper libraries use unofficial APIs and may break if the respective websites change their structure.

## License

MIT
