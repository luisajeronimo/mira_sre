"""Regressões do registro de rotas funcionais do Reflex."""

from app.app import app
from app.chamados.gerente import ChamadosGerenteState
from app.chamados.tecnico import ChamadosTecnicoState
from app.pages.administracao import AdministracaoState
from app.states.auth import AuthState


def test_rotas_canonicas_e_compatibilidade_usam_handlers_corretos():
    inicio = app._unevaluated_pages["inicio"]
    chamados = app._unevaluated_pages["chamados"]
    detalhe = app._unevaluated_pages["chamados/[chamado_id]"]

    assert inicio.on_load.fn is AuthState.carregar_inicio.fn
    assert chamados.on_load.fn is AuthState.redirecionar_chamados_para_inicio.fn
    assert detalhe.on_load.fn is AuthState.carregar_detalhe_chamado.fn


def test_aliases_sao_redirecionadores_protegidos():
    gerente = app._unevaluated_pages["gerente"]
    gerente_novo = app._unevaluated_pages["gerente/chamados/novo"]
    tecnico = app._unevaluated_pages["tecnico"]
    admin = app._unevaluated_pages["administracao"]

    assert gerente.on_load.fn is ChamadosGerenteState.redirecionar_alias_lista.fn
    assert gerente_novo.on_load.fn is ChamadosGerenteState.redirecionar_alias_novo.fn
    assert tecnico.on_load.fn is ChamadosTecnicoState.redirecionar_alias_fila.fn
    assert admin.on_load.fn is AdministracaoState.redirecionar_alias_administracao.fn


def test_rota_estatica_de_novo_e_registrada_antes_do_detalhe_dinamico():
    rotas = list(app._unevaluated_pages)

    assert rotas.index("chamados/novo") < rotas.index("chamados/[chamado_id]")
