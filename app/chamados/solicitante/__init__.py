"""Acompanhamento somente leitura dos chamados solicitados."""

from app.chamados.solicitante.pages import chamados_solicitados, detalhe_chamado_solicitado
from app.chamados.solicitante.state import ChamadosSolicitanteState

__all__ = [
    "ChamadosSolicitanteState",
    "chamados_solicitados",
    "detalhe_chamado_solicitado",
]
