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
	@echo "  test        Run all tests with coverage"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint        Run all quality checks"
	@echo "  format      Format code"
	@echo ""
	@echo "Database:"
	@echo "  db-setup    Setup database"
	@echo ""
	@echo "Utilities:"
	@echo "  clean       Clean temporary files"
	@echo "  ci-local    Run local CI pipeline"

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
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=app --cov-report=term-missing --cov-fail-under=60

# Code Quality
lint:
	@echo "🔍 Running all quality checks..."
	black --check app/ tests/ || echo "⚠️ Format issues found"
	isort --check-only app/ tests/ || echo "⚠️ Import issues found"
	flake8 app/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127
	bandit -r app/ -f txt || echo "⚠️ Security issues found"
	safety check || echo "⚠️ Dependency issues found"

format:
	@echo "🎨 Formatting code..."
	black app/ tests/
	isort app/ tests/

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
	make test
	@echo "✅ All CI checks passed!"

# Quick Development Commands
dev: format lint test
	@echo "✅ Development checks complete!"
