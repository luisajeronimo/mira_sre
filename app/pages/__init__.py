"""Páginas registradas pela aplicação Reflex."""

from app.pages.home import diretoria, gerente, index, tecnico
from app.pages.login import login
from app.pages.chamados import (
    detalhe_chamado,
    detalhe_chamado_tecnico,
    gerente_chamados,
    novo_chamado,
    tecnico_chamados,
)

__all__ = [
    "detalhe_chamado",
    "detalhe_chamado_tecnico",
    "diretoria",
    "gerente",
    "gerente_chamados",
    "index",
    "login",
    "novo_chamado",
    "tecnico",
    "tecnico_chamados",
]
