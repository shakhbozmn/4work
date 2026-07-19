# 4work — Freelance Marketplace

A Django web application where clients post freelance projects and freelancers
apply with a cover letter, proposed timeline, and proposed budget. Clients
review applications and assign one freelancer per project; the freelancer then
marks the project complete.

![coverage](https://img.shields.io/badge/coverage-%E2%89%A580%25-brightgreen)

---

## Features

- Custom user model with `client` and `freelancer` roles and a 1:1 profile
- Project CRUD with category, deadline (validated server-side), budget, and
  many-to-many skills
- Freelancer applications with cover letter, timeline, and proposed budget
  that survive re-render on validation errors
- Application workflow: pending → accepted (assigns freelancer, rejects peer
  pending apps atomically) or pending → rejected
- Role-aware dashboards and applicant-PII boundaries (owner sees all,
  freelancer sees own, anonymous sees nothing)
- Server-rendered Django templates, Tailwind via CDN, Alpine.js for the
  mobile nav, Flatpickr for date inputs
- PostgreSQL data store, Redis cache + session backend
- Idempotent demo seeder with rolling deadlines and an `adminus` admin account
- Production configuration that fails closed on missing secrets or hosts
- Real health endpoint that probes PostgreSQL and Redis

## Stack

| Layer    | Tooling                                                        |
|----------|----------------------------------------------------------------|
| Language | Python 3.12 (production), 3.14 (local venv)                     |
| Web      | Django 6.0, Gunicorn, Nginx                                    |
| Data     | PostgreSQL 15, Redis 7                                         |
| Frontend | Django templates, Tailwind (CDN), Alpine.js, Flatpickr, vanilla JS |
| Tests    | pytest, pytest-django, pytest-cov (≥80% gate)                  |
| Lint     | flake8, black, isort                                           |
| Build    | Docker multi-stage build, Docker Compose                       |
| CI       | GitHub Actions (lint → test → build → publish → deploy)        |

## Architecture

Gunicorn serves Django behind an Nginx reverse proxy that terminates TLS and
serves `/static/` and `/media/` directly. PostgreSQL holds users, profiles,
projects, and applications; Redis holds sessions and the cache. The health
endpoint at `/health/` verifies both before returning 200.

The data model lives in [`4work_ERD.drawio`](4work_ERD.drawio).

## Local setup

Docker is the recommended path. The dev image installs both runtime and
developer dependencies.

```bash
git clone https://github.com/shakhbozmn/4work.git
cd 4work
make bootstrap-demo
```

`make bootstrap-demo` will:

1. Copy `.env.example` to `.env` if missing
2. Build the dev compose stack (PostgreSQL, Redis, Django)
3. Run database migrations
4. Collect static files
5. Load the demo accounts

The site is then available at `http://localhost:${APP_PORT:-8000}`.

To start without demo data, run `make bootstrap` instead. Stop the stack with
`make down`, and drop the volume data with `make reset`.

### Demo accounts

| Role       | Username           | Password      |
|------------|--------------------|---------------|
| Client     | `john_client`      | `password123` |
| Freelancer | `jane_freelancer`  | `password123` |
| Freelancer | `bob_freelancer`   | `password123` |
| Admin      | `adminus`          | `admin123us`  |

The admin user can sign in at `/admin/`. Re-running `load_demo_data` refreshes
passwords and recomputes deadlines relative to the current date.

## Tests, lint, and coverage

Run everything inside the dev container:

```bash
make test          # pytest
make coverage      # pytest with the 80% coverage gate
make lint          # flake8 + black --check + isort --check
make check         # python manage.py check --deploy
```

To target a single test inside the container:

```bash
docker compose -f docker-compose.dev.yml exec web \
  pytest accounts/tests/test_management_commands.py::LoadDemoDataCommandTest::test_first_load_seeds_expected_counts -v
```

CI runs lint and the coverage-gated test suite on every push and pull request.
The Docker build runs only on pushes to `main`; publishing and deployment are
manual via the production environment.

## Deployment

Production runs the multi-stage `Dockerfile` behind Nginx. Configure the
target host with `.env.production`:

```bash
cp .env.production.example .env.production
$EDITOR .env.production
docker compose --env-file .env.production -f docker-compose.yml config  # validate
docker compose --env-file .env.production -f docker-compose.yml up -d --build
```

The production settings module refuses to load when `SECRET_KEY`,
`DB_PASSWORD`, `REDIS_PASSWORD`, or `ALLOWED_HOSTS` are missing or blank, or
when `DEBUG=True`. The Nginx template at
[`nginx/default.conf.template`](nginx/default.conf.template) is rendered by
the official `nginx` image using `${DOMAIN}` from the env file.

`deploy.sh` is the VM-side counterpart: it pulls, recreates the web
container, migrates, collects static, and then polls the Docker health
status until the web service reports `healthy` (failing the deploy if it
does not within the timeout).

## Project structure

```
4work/
├── Makefile                       # one-command developer workflow
├── LICENSE                        # MIT
├── README.md
├── manage.py
├── pytest.ini                     # DJANGO_SETTINGS_MODULE = config.settings.test
├── requirements.txt               # runtime only
├── requirements-dev.txt           # runtime + tests + linters
├── .coveragerc                    # accounts/marketplace/config, fail-under 80%
├── Dockerfile                     # multi-stage production image
├── Dockerfile.dev                 # dev image with -r requirements-dev.txt
├── docker-compose.yml             # production stack
├── docker-compose.dev.yml         # local development stack
├── .github/workflows/deploy.yml   # CI: lint, test, build, publish
├── config/                        # Django project (settings, urls, wsgi, health)
├── accounts/                      # auth + profile app
├── marketplace/                   # projects + applications app
├── fixtures/                      # categories, skills, demo data
├── templates/                     # base, home, accounts, marketplace
├── nginx/                         # envsubst template + cert volume mount
├── entrypoint.sh                  # container bootstrap (wait, migrate, gunicorn)
├── deploy.sh                      # VM deployment script with health-poll loop
└── 4work_ERD.drawio               # data model diagram
```

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 shakhbozmn.
