# MIRA - Makefile
# Preparação e execução do ambiente

# Detecta o sistema operacional
ifeq ($(OS),Windows_NT)
	VENV_PYTHON := .venv/Scripts/python.exe
	SYSTEM_PYTHON := python
else
	VENV_PYTHON := .venv/bin/python
	SYSTEM_PYTHON := python3
endif


.PHONY: setup install xano-install openspec-install simulator fiscal


setup:
	@echo "======================================"
	@echo " Preparando ambiente do MIRA"
	@echo "======================================"
	@$(SYSTEM_PYTHON) -m venv .venv
	@$(MAKE) install
	@$(VENV_PYTHON) -c "from pathlib import Path; env=Path('.env'); example=Path('.env.example'); env.exists() or (example.exists() and env.write_text(example.read_text()))"
	@echo ""
	@echo "Ambiente preparado com sucesso."
	@echo ""
	@echo "Proximos comandos:"
	@echo "  make simulator"
	@echo "  make fiscal"

install:
	@echo "Instalando dependencias..."
	@$(VENV_PYTHON) -m pip install --upgrade pip
	@$(VENV_PYTHON) -m pip install -r requirements.txt
	@echo "Dependencias instaladas."

xano-install:
	@echo "Verificando Node.js..."
	@node --version
	@echo "Verificando npm..."
	@npm --version
	@echo "Instalando Xano CLI..."
	@npm install -g @xano/cli
	@echo "Xano CLI instalado:"
	@xano --version
	@echo ""
	@echo "Execute 'xano auth' para autenticar esta maquina."

openspec-install:
	@echo "Instalando OpenSpec..."
	@npm install -g @fission-ai/openspec@latest
	@openspec --version

simulator:
	@echo "Iniciando Simulator..."
	@$(VENV_PYTHON) simulator/simulator.py

fiscal:
	@echo "Iniciando Fiscal..."
	@$(VENV_PYTHON) fiscal/fiscal.py