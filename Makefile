# Smart Learning Hub - Development Makefile

.PHONY: help install test lint format security clean run build deploy

# Default target
help:
	@echo "Smart Learning Hub - Development Commands"
	@echo "========================================"
	@echo ""
	@echo "Setup:"
	@echo "  install     Install all dependencies"
	@echo "  setup       Setup development environment"
	@echo ""
	@echo "Development:"
	@echo "  run         Run the development server"
	@echo "  test        Run all tests"
	@echo "  test-cov    Run tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint        Run linting checks"
	@echo "  format      Format code with black and isort"
	@echo "  security    Run security checks"
	@echo ""
	@echo "Database:"
	@echo "  db-setup    Setup database"
	@echo "  db-migrate  Run database migrations"
	@echo ""
	@echo "Deployment:"
	@echo "  build       Build application for production"
	@echo "  deploy      Deploy to production"
	@echo ""
	@echo "Utilities:"
	@echo "  clean       Clean temporary files"
	@echo "  deps        Update dependencies"

# Setup and Installation
install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

setup: install db-setup
	@echo "✅ Development environment setup complete!"
	@echo "Run 'make run' to start the development server"

# Development Server
run:
	@echo "🚀 Starting development server..."
	export FLASK_ENV=development && python start.py

# Testing
test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

test-fast:
	@echo "⚡ Running fast tests..."
	pytest tests/ -v -m "not slow"

# Code Quality
lint:
	@echo "🔍 Running linting checks..."
	flake8 app/ tests/
	black --check app/ tests/
	isort --check-only app/ tests/

format:
	@echo "🎨 Formatting code..."
	black app/ tests/
	isort app/ tests/

security:
	@echo "🔒 Running security checks..."
	bandit -r app/
	safety check

# Database
db-setup:
	@echo "🗄️  Setting up database..."
	python database/setup_database.py

db-migrate:
	@echo "🔄 Running database migrations..."
	flask db upgrade

# Build and Deployment
build:
	@echo "🔨 Building application..."
	chmod +x build.sh
	./build.sh

deploy:
	@echo "🚀 Deploying to production..."
	git push origin main

# Utilities
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf dist/
	rm -rf build/

deps:
	@echo "📦 Updating dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt

# CI/CD Simulation
ci-local:
	@echo "🔄 Running local CI pipeline..."
	make lint
	make security
	make test-cov
	@echo "✅ All CI checks passed!"

# Performance Testing
perf-test:
	@echo "⚡ Running performance tests..."
	pytest tests/ -v -m performance --html=performance_report.html

# Documentation
docs:
	@echo "📚 Generating documentation..."
	# Add documentation generation commands here

# Docker (if using Docker)
docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t smart-learning-hub .

docker-run:
	@echo "🐳 Running Docker container..."
	docker run -p 8000:8000 smart-learning-hub

# Environment Management
env-check:
	@echo "🔍 Checking environment..."
	@echo "Python version: $(shell python --version)"
	@echo "Pip version: $(shell pip --version)"
	@echo "Flask version: $(shell pip show flask | grep Version)"
	@echo "Environment: $(FLASK_ENV)"

# Quick Development Commands
dev: format lint test
	@echo "✅ Development checks complete!"

quick-test:
	@echo "⚡ Running quick tests..."
	pytest tests/test_app.py -v

# Git Hooks (optional)
install-hooks:
	@echo "🔗 Installing git hooks..."
	cp scripts/pre-commit .git/hooks/
	chmod +x .git/hooks/pre-commit

# Backup and Restore
backup-db:
	@echo "💾 Creating database backup..."
	cp instance/site.db backups/site_backup_$(shell date +%Y%m%d_%H%M%S).db

restore-db:
	@echo "🔄 Restoring database..."
	@echo "Usage: make restore-db BACKUP_FILE=backups/site_backup_20231201_120000.db"
	cp $(BACKUP_FILE) instance/site.db
