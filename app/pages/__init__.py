"""Páginas registradas pela aplicação Reflex."""

from app.pages.home import diretoria, gerente, index, tecnico
from app.pages.login import login
from app.chamados.gerente import (
    detalhe_chamado,
    gerente_chamados,
    novo_chamado,
)
from app.chamados.tecnico import (
    detalhe_chamado_tecnico,
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
