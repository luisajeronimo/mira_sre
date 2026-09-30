"""Regressões de ligação entre rotas e eventos funcionais."""

from app.app import app
from app.chamados.gerente import ChamadosGerenteState
from app.chamados.tecnico import ChamadosTecnicoState


def test_rota_gerente_carrega_a_listagem_de_chamados():
    pagina = app._unevaluated_pages["gerente"]

    assert pagina.on_load.fn is ChamadosGerenteState.carregar_lista.fn


def test_rotas_tecnicas_carregam_fila_e_detalhe():
    fila = app._unevaluated_pages["tecnico"]
    detalhe = app._unevaluated_pages["tecnico/chamados/[chamado_id]"]

    assert fila.on_load.fn is ChamadosTecnicoState.carregar_fila.fn
    assert detalhe.on_load.fn is ChamadosTecnicoState.carregar_detalhe_tecnico.fn
