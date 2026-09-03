# FixFlow

Maintenance request coordination for apartments, hostels, campuses, and small facilities teams.

FixFlow gives residents a simple way to report problems and gives operators a traceable workflow for triage, assignment, service-level tracking, communication, and resolution.

## Core capabilities

- Property, unit, and resident records
- Maintenance tickets and priority rules
- Technician assignment and status history
- Resident-visible comments
- Service-level monitoring
- Operational metrics and overdue queues

## Technology

Python 3.12, Django, Django REST Framework, PostgreSQL, Pytest, Ruff, and GitHub Actions.

## Local setup

1. Create a Python 3.12 virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env`.
4. Run `python manage.py migrate`.
5. Start with `python manage.py runserver`.

## Quality commands

```bash
ruff check .
pytest
python manage.py check
```

## License

MIT
