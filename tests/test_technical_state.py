import asyncio
import inspect

import pytest

import app.chamados.gerente.pages as paginas_gerente
import app.chamados.tecnico.pages as paginas_chamados
import app.chamados.tecnico.state as chamados_module
from app.services.service_desk import (
    ChamadoDetalhe,
    ChamadoResumo,
    ReferenciaAtivo,
    ReferenciaCategoria,
    ReferenciaUsuario,
)
from app.services.xano import XanoConflito
from app.states.auth import MENSAGEM_INDISPONIVEL
from app.chamados.shared import _detalhe_para_dict, _tecnico_para_dict
from app.chamados.tecnico import ChamadosTecnicoState


def executar_evento(handler, estado, *args):
    async def coletar():
        return [evento async for evento in handler.fn(estado, *args)]

    return asyncio.run(coletar())


def resumo_tecnico(*, status="Novo", tecnico=None, atribuido_em=0):
    return ChamadoResumo(
        id=32,
        titulo="TESTE E2E - Falha operacional",
        status=status,
        prioridade="Alta",
        origem="manual",
        criado_em=1780000000000,
        ultima_atualizacao_em=1780000000000,
        ativo=ReferenciaAtivo(id=1, nome_ativo="Totem de teste"),
        categoria=ReferenciaCategoria(id=2, nome="Falha de Rede"),
        descricao="Descrição de teste",
        sla_horas_aplicado=2,
        atribuido_em=atribuido_em,
        solicitante=ReferenciaUsuario(id=8, nome="Gerente"),
        tecnico=tecnico,
    )


def detalhe_tecnico(
    *,
    status="Novo",
    tecnico=None,
    atribuido_em=1780000001000,
    criador_sistema=None,
):
    return ChamadoDetalhe(
        id=32,
        titulo="TESTE E2E - Falha operacional",
        descricao="Descrição de teste",
        status=status,
        prioridade="Alta",
        origem="manual",
        criado_em=1780000000000,
        ultima_atualizacao_em=1780000000000,
        sla_horas_aplicado=2,
        ativo=ReferenciaAtivo(id=1, nome_ativo="Totem de teste"),
        categoria=ReferenciaCategoria(id=2, nome="Falha de Rede"),
        solicitante=ReferenciaUsuario(id=8, nome="Gerente"),
        tecnico=tecnico,
        atribuido_em=atribuido_em,
        criador_sistema=criador_sistema,
    )


class ClienteTecnicoFalso:
    def __init__(self, *, resultado_assuncao=None, erro_assuncao=None, listas=None):
        self.resultado_assuncao = resultado_assuncao
        self.erro_assuncao = erro_assuncao
        self.listas = listas or {}
        self.visoes = []
        self.assuncoes = []

    async def listar_chamados_tecnico(self, token, visao):
        self.visoes.append((token, visao))
        return self.listas.get(visao, [])

    async def assumir_chamado_tecnico(self, token, chamado_id):
        self.assuncoes.append((token, chamado_id))
        if self.erro_assuncao is not None:
            raise self.erro_assuncao
        return self.resultado_assuncao


def novo_estado_tecnico():
    estado = ChamadosTecnicoState(_reflex_internal_init=True)
    object.__setattr__(estado, "_auth_token", "token-de-teste")
    object.__setattr__(estado, "sessao_confirmada", True)
    object.__setattr__(estado, "usuario_id", 9)
    object.__setattr__(estado, "role", "tecnico")
    return estado


def liberar_validacao_de_sessao(monkeypatch):
    async def validar(_estado):
        return None

    monkeypatch.setattr(ChamadosTecnicoState, "_validar_tecnico", validar)


@pytest.mark.parametrize("visao", ["nao_atribuidos", "atribuidos_a_mim"])
def test_selecionar_visao_consulta_a_visao_escolhida(monkeypatch, visao):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso()
    monkeypatch.setattr(
        chamados_module,
        "criar_cliente_service_desk",
        lambda: cliente,
    )
    estado = novo_estado_tecnico()

    executar_evento(ChamadosTecnicoState.selecionar_visao, estado, visao)

    assert estado.visao == visao
    assert cliente.visoes == [("token-de-teste", visao)]
    assert estado.carregando_fila is False


def test_elegibilidade_visual_usa_status_e_tecnico_sem_condicionar_timestamp():
    legado_com_timestamp = resumo_tecnico(atribuido_em=1780000001000)
    tecnico_atribuido = resumo_tecnico(
        tecnico=ReferenciaUsuario(id=13, nome="Outro Técnico"),
        atribuido_em=1780000001000,
    )
    status_diferente = resumo_tecnico(status="Em Atendimento", atribuido_em=0)

    assert _tecnico_para_dict(legado_com_timestamp)["pode_assumir"] is True
    assert _detalhe_para_dict(
        detalhe_tecnico(atribuido_em=1780000001000)
    )["pode_assumir"] is True
    assert _tecnico_para_dict(tecnico_atribuido)["pode_assumir"] is False
    assert _tecnico_para_dict(status_diferente)["pode_assumir"] is False


def test_detalhe_mostra_nome_do_bot_somente_quando_persistido():
    automatico = _detalhe_para_dict(
        detalhe_tecnico(criador_sistema="bot_fiscalizacao")
    )
    legado = _detalhe_para_dict(detalhe_tecnico(criador_sistema=None))

    assert automatico["criador_sistema_nome"] == "Bot de Fiscalização"
    assert legado["criador_sistema_nome"] == ""


def test_detalhes_apresentam_autoria_persistida_sem_ampliar_listagens():
    detalhe_gerente = inspect.getsource(paginas_gerente._detalhe)
    detalhe_tecnico = inspect.getsource(paginas_chamados._detalhe_tecnico)
    lista_gerente = inspect.getsource(paginas_gerente._lista)
    fila_tecnica = inspect.getsource(paginas_chamados._fila_tecnico)

    for detalhe in (detalhe_gerente, detalhe_tecnico):
        assert '"criador_sistema_nome"] != ""' in detalhe
        assert "Criado por: " in detalhe
        assert "Origem: " in detalhe

    assert "criador_sistema" not in lista_gerente
    assert "criador_sistema" not in fila_tecnica


def test_assuncao_bem_sucedida_recarrega_fila_e_preserva_confirmacao(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(
        resultado_assuncao=detalhe_tecnico(
            tecnico=ReferenciaUsuario(id=9, nome="Técnico 9"),
        ),
        listas={"nao_atribuidos": []},
    )
    monkeypatch.setattr(
        chamados_module,
        "criar_cliente_service_desk",
        lambda: cliente,
    )
    estado = novo_estado_tecnico()

    executar_evento(ChamadosTecnicoState.assumir, estado, 32)

    assert cliente.assuncoes == [("token-de-teste", 32)]
    assert cliente.visoes == [("token-de-teste", "nao_atribuidos")]
    assert estado.chamado["status"] == "Novo"
    assert estado.chamado["tecnico_nome"] == "Técnico 9"
    assert estado.chamado["atribuido_em_texto"] != "Não informado"
    assert estado.mensagem_assuncao == "Chamado assumido com sucesso."
    assert estado.assumindo_id is None
    assert estado.carregando_fila is False
    assert estado.chamados == []


def test_conflito_informa_e_recarrega_sem_substituir_detalhe_local(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(erro_assuncao=XanoConflito("detalhe interno"))
    monkeypatch.setattr(
        chamados_module,
        "criar_cliente_service_desk",
        lambda: cliente,
    )
    estado = novo_estado_tecnico()
    detalhe_anterior = {"id": 32, "tecnico_nome": "Não atribuído"}
    estado.chamado = detalhe_anterior

    executar_evento(ChamadosTecnicoState.assumir, estado, 32)

    assert cliente.assuncoes == [("token-de-teste", 32)]
    assert cliente.visoes == [("token-de-teste", "nao_atribuidos")]
    assert estado.chamado == detalhe_anterior
    assert estado.mensagem_assuncao == "Este chamado foi assumido por outro Técnico."
    assert estado.assumindo_id is None
    assert estado.carregando_fila is False


def test_excecao_inesperada_libera_loading_e_nao_expoe_detalhe(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(
        erro_assuncao=RuntimeError("resposta interna sensível")
    )
    monkeypatch.setattr(
        chamados_module,
        "criar_cliente_service_desk",
        lambda: cliente,
    )
    estado = novo_estado_tecnico()

    executar_evento(ChamadosTecnicoState.assumir, estado, 32)

    assert estado.assumindo_id is None
    assert estado.carregando_fila is False
    assert estado.mensagem_assuncao == MENSAGEM_INDISPONIVEL
    assert "sensível" not in estado.mensagem_assuncao
    assert cliente.visoes == [("token-de-teste", "nao_atribuidos")]


def test_telas_tecnicas_nao_exibem_acoes_de_tratativa_ou_reatribuicao():
    fonte = "\n".join(
        (
            inspect.getsource(paginas_chamados._fila_tecnico),
            inspect.getsource(paginas_chamados._detalhe_tecnico),
        )
    ).casefold()

    for acao in (
        "resolver",
        "diagnóstico",
        "diagnostico",
        "work log",
        "reatribuir",
        "liberar",
        "cancelar",
        "alterar status",
    ):
        assert acao not in fonte
