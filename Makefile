.PHONY: install test backtest paper live docker-build docker-up docker-down clean

install:
\tpoetry install

test:
\tpoetry run pytest tests/ -v --cov=src --cov-report=html

test-unit:
\tpoetry run pytest tests/ -v -m unit

backtest:
\tpoetry run python src/main.py --mode backtest --start 2024-01-01 --end 2024-12-31

paper:
\tpoetry run python src/main.py --mode paper

live:
\tpoetry run python src/main.py --mode live

docker-build:
\tdocker-compose build

docker-up:
\tdocker-compose up -d

docker-down:
\tdocker-compose down

docker-logs:
\tdocker-compose logs -f

docker-backtest:
\tdocker-compose --profile backtest up forex-bot-backtest

clean:
\tfind . -type d -name __pycache__ -exec rm -rf {} +
\tfind . -type f -name "*.pyc" -delete
\trm -rf .pytest_cache .coverage htmlcov/
\trm -rf logs/*.log

format:
\tpoetry run black src/ tests/
\tpoetry run flake8 src/ tests/

lint:
\tpoetry run flake8 src/ tests/
\tpoetry run mypy src/