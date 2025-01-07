# Password Manager Makefile

# Python commands
PYTHON := python
PIP := pip
PYTEST := pytest

# Project settings
VENV := .venv
REQUIREMENTS := requirements.txt
MAIN := main.py
TEST_DIR := tests
SRC_DIR := src

# Windows-specific commands
ifeq ($(OS),Windows_NT)
	PYTHON_VENV := $(VENV)/Scripts/python.exe
	PIP_VENV := $(VENV)/Scripts/pip.exe
	ACTIVATE := $(VENV)/Scripts/activate
	# Command to create virtual environment
	VENV_CREATE := $(PYTHON) -m venv $(VENV)
else
	PYTHON_VENV := $(VENV)/bin/python
	PIP_VENV := $(VENV)/bin/pip
	ACTIVATE := $(VENV)/bin/activate
	# Command to create virtual environment
	VENV_CREATE := $(PYTHON) -m venv $(VENV)
endif

.PHONY: all clean install test run lint format help venv build build-debug

# Default target
all: install test

# Create virtual environment
venv:
	@echo "Creating virtual environment..."
	$(VENV_CREATE)

# Install dependencies
install: venv
	@echo "Installing dependencies..."
	$(PIP_VENV) install --upgrade pip
	$(PIP_VENV) install -r $(REQUIREMENTS)
	@echo "Dependencies installed successfully!"

# Run tests
test: install
	@echo "Running tests..."
	$(PYTHON_VENV) -m unittest discover $(TEST_DIR)

# Run the application
run: install
	@echo "Starting Password Manager..."
	$(PYTHON_VENV) $(MAIN)

# Clean up generated files and virtual environment
clean:
	@echo "Cleaning up..."
	rm -rf $(VENV) __pycache__ .pytest_cache .coverage
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type f -name "*.log" -delete
	@echo "Cleanup complete!"

# Install development dependencies and formatting tools
dev-install: install
	@echo "Installing development dependencies..."
	$(PIP_VENV) install black pylint pytest pytest-cov
	@echo "Development dependencies installed!"

# Run linting
lint: dev-install
	@echo "Running linting..."
	$(PYTHON_VENV) -m pylint $(SRC_DIR)

# Format code using black
format: dev-install
	@echo "Formatting code..."
	$(PYTHON_VENV) -m black $(SRC_DIR) $(TEST_DIR) $(MAIN)

# Run tests with coverage report
coverage: dev-install
	@echo "Running tests with coverage..."
	$(PYTHON_VENV) -m pytest --cov=$(SRC_DIR) $(TEST_DIR) --cov-report=term-missing

# Create a new database backup
backup:
	@echo "Creating database backup..."
	@if exist "passwords.db" ( \
		copy passwords.db "passwords_backup_$$(date /T)_$$(time /T).db" \
	) else ( \
		echo "No database file found!" \
	)

# Build the application
build:
	$(PYTHON) -m PyInstaller --clean --onefile --windowed --name py-account-manager \
		--add-data "src/gui/styles.py:src/gui" \
		--icon=src/gui/assets/icon.ico \
		main.py

# Build the application in debug mode
build-debug:
	$(PYTHON) -m PyInstaller --clean --onefile --name py-account-manager-debug \
		--add-data "src/gui/styles.py:src/gui" \
		--icon=src/gui/assets/icon.ico \
		main.py

# Help command
help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies in a virtual environment"
	@echo "  make run        - Run the Password Manager application"
	@echo "  make test       - Run unit tests"
	@echo "  make clean      - Clean up generated files and virtual environment"
	@echo "  make dev-install- Install development dependencies"
	@echo "  make lint       - Run linting checks"
	@echo "  make format     - Format code using black"
	@echo "  make coverage   - Run tests with coverage report"
	@echo "  make backup     - Create a database backup"
	@echo "  make build      - Build the application"
	@echo "  make build-debug- Build the application in debug mode"
	@echo "  make help       - Show this help message"
