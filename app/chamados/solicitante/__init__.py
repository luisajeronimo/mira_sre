"""Acompanhamento somente leitura de chamados solicitados."""

from .state import ChamadosSolicitanteState
from .pages import chamados_solicitados, detalhe_chamado_solicitado

__all__ = ["ChamadosSolicitanteState", "chamados_solicitados", "detalhe_chamado_solicitado"]
