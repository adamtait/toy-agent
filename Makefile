.PHONY: all install test build clean

# Variables
PYTHON = python3
PIP = pip
VENV_DIR = venv

# Default target
all: install

# Create a virtual environment and install dependencies
install: $(VENV_DIR)/bin/activate

$(VENV_DIR)/bin/activate:
	@if [ ! -d "$(VENV_DIR)" ]; then \
		$(PYTHON) -m venv $(VENV_DIR); \
	fi
	. $(VENV_DIR)/bin/activate && \
	$(PIP) install -r requirements.txt && \
	$(PIP) install -r requirements-dev.txt
	@echo "Dependencies installed in virtual environment at $(VENV_DIR)"

# Run tests
test: install
	. $(VENV_DIR)/bin/activate && PYTHONPATH=. pytest tests/

# Build a binary
build: install
	. $(VENV_DIR)/bin/activate && pyinstaller --onefile --name react-agent src/main.py

# Clean up build artifacts and cache
clean:
	rm -rf build/ dist/ *.spec .pytest_cache/ __pycache__/
	find . -type d -name "__pycache__" -exec rm -r {} +
	@echo "Cleaned up build artifacts and cache."
