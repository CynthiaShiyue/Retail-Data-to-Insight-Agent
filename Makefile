# === Makefile for Retail Data to Insight Agent ===
VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

.PHONY: all install run clean

install:
	@echo "Setting up environment..."
	python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Setup complete!"

run:
	@echo "Starting Streamlit app..."
	$(PYTHON) -m streamlit run dashboard.py

clean:
	@echo "🧹 Cleaning up virtual environment..."
	rm -rf $(VENV_DIR)
	@echo "Done."

all: install run
