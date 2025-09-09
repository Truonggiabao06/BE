# Jewelry Auction System Makefile

.PHONY: help install dev test clean migrate seed docker-up docker-down docker-logs

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install Python dependencies"
	@echo "  dev         - Run development server"
	@echo "  test        - Run tests"
	@echo "  clean       - Clean up temporary files"
	@echo "  migrate     - Run database migrations"
	@echo "  seed        - Seed database with initial data"
	@echo "  docker-up   - Start Docker services"
	@echo "  docker-down - Stop Docker services"
	@echo "  docker-logs - View Docker logs"

# Install dependencies
install:
	pip install -r requirements.txt

# Run development server
dev:
	@echo "Starting development server..."
	@if [ ! -f .env ]; then \
		echo "Creating .env from .env.example..."; \
		cp .env.example .env; \
	fi
	cd src && python app.py

# Run tests
test:
	@echo "Running tests..."
	cd src && python -m pytest tests/ -v --cov=. --cov-report=html

# Clean temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage

# Run database migrations
migrate:
	@echo "Running database migrations..."
	cd src && flask db upgrade

# Initialize database (first time setup)
init-db:
	@echo "Initializing database..."
	cd src && flask db init
	cd src && flask db migrate -m "Initial migration"
	cd src && flask db upgrade

# Seed database with initial data
seed:
	@echo "Seeding database..."
	cd src && python scripts/seed_data.py

# Docker commands
docker-up:
	@echo "Starting Docker services..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down

docker-logs:
	docker-compose logs -f

docker-build:
	docker-compose build

# Full setup for new development environment
setup: install
	@echo "Setting up development environment..."
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example"; \
		echo "Please update .env with your configuration"; \
	fi
	mkdir -p uploads logs
	@echo "Setup complete! Run 'make docker-up' to start services, then 'make migrate' and 'make seed'"

# Production deployment
deploy:
	@echo "Deploying to production..."
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

# Database backup (requires Docker SQL Server service)
backup:
	@echo "Creating database backup..."
	docker exec jewelry_auction_sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P Aa@123456 -Q "BACKUP DATABASE jewelry_auction_dev TO DISK = '/var/opt/mssql/backup_$(shell date +%Y%m%d_%H%M%S).bak'"

# Restore database from backup
restore:
	@echo "Restoring database from backup..."
	@read -p "Enter backup file name: " backup_file; \
	docker exec jewelry_auction_sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P Aa@123456 -Q "RESTORE DATABASE jewelry_auction_dev FROM DISK = '/var/opt/mssql/$$backup_file'"
