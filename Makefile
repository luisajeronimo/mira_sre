PYTHON := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: help install run-simulator run-fiscal

help:
	@echo "Comandos disponíveis:"
	@echo "  make install        Instala as dependências Python"
	@echo "  make run-simulator  Inicia o simulador de totens"
	@echo "  make run-fiscal     Inicia o fiscal de heartbeat"

install:
	$(PIP) install --upgrade pip
	$(PIP) install requests python-dotenv

run-simulator:
	$(PYTHON) simulator/simulator.py

run-fiscal:
	$(PYTHON) fiscal/fiscal.py
