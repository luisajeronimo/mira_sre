"""Jornada de chamados do Técnico."""

from app.chamados.tecnico.pages import detalhe_chamado_tecnico, tecnico_chamados
from app.chamados.tecnico.state import ChamadosTecnicoState

__all__ = ["ChamadosTecnicoState", "detalhe_chamado_tecnico", "tecnico_chamados"]
