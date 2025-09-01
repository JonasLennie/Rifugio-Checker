.PHONY: help setup test test-cov lint format clean install-dev run

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup:  ## Set up conda environment
	conda env create -f environment.yml
	conda activate rifugio-monitor
	@echo "✅ Environment created. Run: conda activate rifugio-monitor"

install-dev:  ## Install development dependencies
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install
	@echo "✅ Development dependencies installed"

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

lint:  ## Run linting
	flake8 src/ tests/
	mypy src/ --ignore-missing-imports

format:  ## Format code
	black src/ tests/
	isort src/ tests/ --profile black

format-check:  ## Check code formatting
	black src/ tests/ --check
	isort src/ tests/ --profile black --check-only

run:  ## Run the monitor locally
	cd src && python monitor.py

clean:  ## Clean up generated files
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf src/__pycache__/
	rm -rf tests/__pycache__/
	rm -f monitor.log
	rm -f temp_calendar.pdf
	@echo "✅ Cleaned up generated files"

check-env:  ## Check if required environment variables are set
	@echo "Checking environment variables..."
	@python -c "import os; print('✅ EMAIL_FROM:', os.getenv('EMAIL_FROM', '❌ Not set'))"
	@python -c "import os; print('✅ EMAIL_TO:', os.getenv('EMAIL_TO', '❌ Not set'))"
	@python -c "import os; print('✅ EMAIL_PASSWORD:', '✅ Set' if os.getenv('EMAIL_PASSWORD') else '❌ Not set')"
	@python -c "import os; print('✅ TARGET_DATES:', os.getenv('TARGET_DATES', '❌ Not set'))"

test-email:  ## Test email connection
	@cd src && python -c "from notifier import EmailNotifier; import os; n = EmailNotifier(os.getenv('EMAIL_FROM'), os.getenv('EMAIL_TO'), os.getenv('EMAIL_PASSWORD')); print('✅ Email connection OK' if n.test_email_connection() else '❌ Email connection failed')"

all: format lint test  ## Run format, lint, and test