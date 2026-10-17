"""Páginas registradas pela aplicação Reflex."""

from app.pages.home import diretoria, gerente, index, tecnico
from app.pages.login import login
from app.pages.administracao import administracao, primeiro_acesso
from app.pages.rotas import alias, chamados, detalhe_chamado_canonico, inicio
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
    "detalhe_chamado_canonico",
    "administracao",
    "alias",
    "detalhe_chamado_tecnico",
    "diretoria",
    "gerente",
    "gerente_chamados",
    "index",
    "inicio",
    "login",
    "novo_chamado",
    "chamados",
    "primeiro_acesso",
    "tecnico",
    "tecnico_chamados",
]
