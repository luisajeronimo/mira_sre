"""Jornada de chamados do Gerente."""

from app.chamados.gerente.pages import detalhe_chamado, gerente_chamados, novo_chamado
from app.chamados.gerente.state import ChamadosGerenteState

__all__ = [
    "ChamadosGerenteState",
    "detalhe_chamado",
    "gerente_chamados",
    "novo_chamado",
]
