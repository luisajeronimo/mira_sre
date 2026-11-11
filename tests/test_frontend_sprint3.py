"""Contratos novos consumidos pelo Reflex na Sprint 3."""

import asyncio
import inspect
import json

import httpx
import pytest

import app.chamados.gerente.state as gerente_module
from app.chamados.gerente.state import ChamadosGerenteState
from app.chamados.shared import _detalhe_para_dict, consumo_sla_para_dict
from app.services.service_desk import (
    AutorHistoricoStatus, ConsumoSLADTO, HistoricoStatusItem, XanoServiceDeskCliente,
    _detalhe_gerente,
)
from app.services.xano import (
    XanoConflito, XanoContratoInvalido, XanoEntradaInvalida,
    XanoIndisponivel, XanoNaoAutenticado, XanoNaoAutorizado, XanoNaoEncontrado,
)


BASE = "https://xano.example/api:mira-service-desk"


def executar(corrotina):
    return asyncio.run(corrotina)


@pytest.mark.parametrize(("faixa", "estado", "fracao", "consumo_ms", "situacao", "prazo"), [
    ("normal", "em_contagem", 0.25, 3600000, "Dentro do SLA", "3.0 h restantes"),
    ("risco", "em_contagem", 0.75, 10800000, "Próximo do vencimento", "1.0 h restantes"),
    ("critico", "em_contagem", 0.95, 13680000, "Próximo do vencimento", "0.2 h restantes"),
    ("violado", "em_contagem", 1.25, 18000000, "Vencido", "1.0 h excedidas"),
    ("normal", "pausada", 0.25, 3600000, "Pausado", ""),
    ("normal", "encerrada", 0.25, 3600000, "Encerrado", ""),
])
def test_apresentacao_sla_por_faixa_e_estado(faixa, estado, fracao, consumo_ms, situacao, prazo):
    consumo = ConsumoSLADTO(
        chamados_id=101, calculavel=True, motivo=None, consumo_ms=consumo_ms,
        sla_horas_aplicado=4, fracao_consumida=fracao, faixa=faixa,
        estado_contagem=estado, calculado_em=1780000000000,
    )
    exibido = consumo_sla_para_dict(consumo)
    assert exibido == {
        "situacao": situacao,
        "percentual": f"{fracao * 100:.1f}% consumido",
        "prazo": prazo,
        "motivo": "",
    }


def cliente(responder):
    return XanoServiceDeskCliente(BASE, transport=httpx.MockTransport(responder))


def detalhe_solicitante():
    return {
        "id": 101, "titulo": "Falha", "descricao": "Totem não conecta",
        "status": "Resolvido", "prioridade": "Alta", "origem": "manual",
        "criador_sistema": None, "criado_em": 1780000000000,
        "ultima_atualizacao_em": 1780000005000,
        "ativo": {"id": 1, "nome_ativo": "Totem 01"},
        "categoria": {"id": 2, "nome": "Rede"},
        "solicitante": {"nome": "Gerente"}, "tecnico": {"nome": "Técnico"},
        "loja": {"id": 1, "nome": "Centro"}, "resumo_totem": None,
    }


def detalhe_gerente():
    return {
        **detalhe_solicitante(), "status": "Solução Rejeitada",
        "sla_horas_aplicado": 2, "solicitante": {"id": 8, "nome": "Gerente"},
        "tecnico": {"id": 12, "nome": "Técnico"},
    }


def test_rejeicao_envia_somente_justificativa_e_versao_e_confirma_detalhe():
    requisicoes = []

    def responder(requisicao):
        requisicoes.append(requisicao)
        return httpx.Response(200, json={"sucesso": True, "chamado": detalhe_gerente()})

    resultado = executar(cliente(responder).rejeitar_solucao(
        "token", 101, justificativa="Ainda falha", ultima_atualizacao_em=1780000000000,
    ))
    assert resultado.status == "Solução Rejeitada"
    assert requisicoes[0].method == "POST"
    assert str(requisicoes[0].url) == f"{BASE}/gerente/chamados/101/rejeitar-solucao"
    assert json.loads(requisicoes[0].content) == {
        "justificativa": "Ainda falha", "ultima_atualizacao_em": 1780000000000,
    }


@pytest.mark.parametrize("codigo,erro", [
    (401, XanoNaoAutenticado), (403, XanoNaoAutorizado),
    (404, XanoNaoEncontrado), (409, XanoConflito),
    (422, XanoEntradaInvalida), (500, XanoIndisponivel),
])
def test_rejeicao_classifica_falhas_sem_aceitar_resposta(codigo, erro):
    c = cliente(lambda _: httpx.Response(codigo, json={"message": "erro"}))
    with pytest.raises(erro):
        executar(c.rejeitar_solucao(
            "token", 101, justificativa="Falhou", ultima_atualizacao_em=1780000000000,
        ))


def test_detalhe_solicitante_recusa_sla_e_identificadores_de_usuario():
    dados = detalhe_solicitante()
    c = cliente(lambda _: httpx.Response(200, json={"chamado": dados}))
    resultado = executar(c.obter_chamado_solicitante("token", 101))
    assert resultado.solicitante.nome == "Gerente"
    assert resultado.tecnico.nome == "Técnico"
    assert resultado.sla_horas_aplicado is None
    for extra in ({"sla_horas_aplicado": 2}, {"solicitante": {"id": 8, "nome": "Gerente"}}):
        c = cliente(lambda _, extra=extra: httpx.Response(200, json={"chamado": {**dados, **extra}}))
        with pytest.raises(XanoContratoInvalido):
            executar(c.obter_chamado_solicitante("token", 101))


def test_historico_e_sla_validam_envelopes_sem_campos_privados():
    def responder(requisicao):
        if requisicao.url.path.endswith("historico-status"):
            return httpx.Response(200, json={"items": [{
                "id": 9, "status_anterior": "Resolvido",
                "status_resultante": "Solução Rejeitada", "criado_em": 1780000005000,
                "autor": {"nome": "Gerente", "perfil": "Gerente"},
            }]})
        return httpx.Response(200, json={"consumo_sla": {
            "chamados_id": 101, "calculavel": True, "motivo": None,
            "consumo_ms": 0, "sla_horas_aplicado": 4, "fracao_consumida": 0,
            "faixa": "normal", "estado_contagem": "em_contagem",
            "calculado_em": 1780000005000,
        }})

    c = cliente(responder)
    historico = executar(c.listar_historico_status_gerente("token", 101))
    sla = executar(c.obter_consumo_sla_tecnico("token", 101))
    assert historico[0].autor.perfil == "Gerente"
    assert sla.consumo_ms == 0
    assert sla.fracao_consumida == 0
    assert sla.estado_contagem == "em_contagem"


def test_lista_e_comentarios_solicitante_recusam_campos_extras():
    item = {campo: detalhe_solicitante()[campo] for campo in (
        "id", "titulo", "descricao", "status", "prioridade", "origem",
        "criado_em", "ultima_atualizacao_em", "ativo", "categoria",
    )}
    comentario = {"id": 11, "conteudo": "Atualização", "criado_em": 1780000005000, "autor": {"nome": "Gerente"}}
    def responder(requisicao):
        return httpx.Response(200, json={"items": [item] if requisicao.url.path.endswith("/solicitante/chamados") else [comentario]})
    c = cliente(responder)
    assert executar(c.listar_chamados_solicitante("token"))[0].id == 101
    assert executar(c.listar_comentarios_publicos_solicitante("token", 101))[0].conteudo == "Atualização"
    for metodo, registro in (
        (lambda c: c.listar_chamados_solicitante("token"), {**item, "tecnico_id": 12}),
        (lambda c: c.listar_comentarios_publicos_solicitante("token", 101), {**comentario, "visibilidade": "interna"}),
    ):
        c = cliente(lambda requisicao, registro=registro: httpx.Response(200, json={"items": [registro]}))
        with pytest.raises(XanoContratoInvalido):
            executar(metodo(c))


@pytest.mark.parametrize("codigo,erro", [
    (401, XanoNaoAutenticado), (403, XanoNaoAutorizado),
    (404, XanoNaoEncontrado), (500, XanoIndisponivel), (503, XanoIndisponivel),
])
@pytest.mark.parametrize("metodo", [
    lambda c: c.listar_chamados_solicitante("token"),
    lambda c: c.obter_chamado_solicitante("token", 101),
    lambda c: c.listar_comentarios_publicos_solicitante("token", 101),
    lambda c: c.listar_historico_status_solicitante("token", 101),
    lambda c: c.listar_historico_status_gerente("token", 101),
])
def test_leituras_novas_classificam_erros_http(codigo, erro, metodo):
    c = cliente(lambda _: httpx.Response(codigo, json={"message": "interno"}))
    with pytest.raises(erro):
        executar(metodo(c))


@pytest.mark.parametrize("autor", [None, {"nome": "Sistema", "perfil": None}])
def test_historico_valida_autor_nulo_e_perfil_nulo(autor):
    item = {"id": 9, "status_anterior": "Resolvido", "status_resultante": "Encerrado",
            "criado_em": 1780000005000, "autor": autor}
    c = cliente(lambda _: httpx.Response(200, json={"items": [item]}))
    resultado = executar(c.listar_historico_status_solicitante("token", 101))[0]
    if autor is None:
        assert resultado.autor is None
    else:
        assert resultado.autor.nome == "Sistema"
        assert resultado.autor.perfil is None
    for invalido in ({**item, "usuarios_id": 8}, {**item, "status_resultante": "Resolvido"},
                     {**item, "criado_em": None}, {**item, "autor": {"nome": "X", "perfil": "Outro"}}):
        c = cliente(lambda _, invalido=invalido: httpx.Response(200, json={"items": [invalido]}))
        with pytest.raises(XanoContratoInvalido):
            executar(c.listar_historico_status_solicitante("token", 101))


def _estado_gerente():
    estado = ChamadosGerenteState(_reflex_internal_init=True)
    object.__setattr__(estado, "_auth_token", "token")
    object.__setattr__(estado, "sessao_confirmada", True)
    object.__setattr__(estado, "usuario_id", 8)
    object.__setattr__(estado, "role", "gerente")
    object.__setattr__(estado, "chamado_id", "101")
    dados = detalhe_gerente()
    dados["status"] = "Resolvido"
    estado.chamado = _detalhe_para_dict(_detalhe_gerente(dados))
    estado.detalhe_carregado = True
    return estado


def _executar_evento(handler, estado):
    async def coletar():
        return [evento async for evento in handler.fn(estado)]
    return asyncio.run(coletar())


def test_rejeicao_exige_justificativa_sem_chamar_backend(monkeypatch):
    estado = _estado_gerente()
    estado.justificativa_rejeicao = "   "
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: pytest.fail("Backend não deve ser chamado"))
    _executar_evento(ChamadosGerenteState.rejeitar_solucao, estado)
    assert estado.mensagem_rejeicao == "Informe a justificativa da rejeição."
    assert estado.chamado["status"] == "Resolvido"


def test_acao_rejeicao_inexistente_fora_de_resolvido(monkeypatch):
    estado = _estado_gerente()
    estado.chamado["status"] = "Encerrado"
    estado.justificativa_rejeicao = "Quero reabrir"
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: pytest.fail("Backend não deve ser chamado"))
    _executar_evento(ChamadosGerenteState.rejeitar_solucao, estado)
    assert estado.chamado["status"] == "Encerrado"
    assert estado.mensagem_rejeicao == "O chamado não está Resolvido."
    from app.chamados.gerente.pages import _detalhe
    pagina = inspect.getsource(_detalhe)
    assert 'ChamadosGerenteState.chamado["status"] == "Resolvido"' in pagina


def test_rejeicao_confirma_status_e_comentarios_e_limpa_justificativa(monkeypatch):
    estado = _estado_gerente()
    estado.justificativa_rejeicao = "Ainda falha"
    chamadas = []

    async def garantir(_):
        return None

    class Falso:
        async def rejeitar_solucao(self, token, chamado_id, **payload):
            chamadas.append((token, chamado_id, payload))
            return _detalhe_gerente(detalhe_gerente())

        async def listar_comentarios_publicos(self, token, chamado_id):
            return []

    monkeypatch.setattr(ChamadosGerenteState, "_garantir_gerente", garantir)
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", Falso)
    _executar_evento(ChamadosGerenteState.rejeitar_solucao, estado)
    assert chamadas == [("token", 101, {
        "justificativa": "Ainda falha", "ultima_atualizacao_em": 1780000005000,
    })]
    assert estado.chamado["status"] == "Solução Rejeitada"
    assert estado.justificativa_rejeicao == ""
    assert estado.mensagem_sucesso_rejeicao == "Solução rejeitada."


def test_conflito_recarrega_detalhe_e_preserva_justificativa(monkeypatch):
    estado = _estado_gerente()
    estado.justificativa_rejeicao = "Ainda falha"

    async def garantir(_):
        return None

    class Falso:
        async def rejeitar_solucao(self, *args, **kwargs):
            raise XanoConflito("interno")

        async def obter_chamado(self, token, chamado_id):
            dados = detalhe_gerente()
            dados["status"] = "Encerrado"
            return _detalhe_gerente(dados)

    monkeypatch.setattr(ChamadosGerenteState, "_garantir_gerente", garantir)
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", Falso)
    _executar_evento(ChamadosGerenteState.rejeitar_solucao, estado)
    assert estado.justificativa_rejeicao == "Ainda falha"
    assert estado.chamado["status"] == "Encerrado"
    assert "mudou" in estado.mensagem_rejeicao


def test_interface_propria_do_solicitante_nao_esta_registrada():
    from app.app import app

    rotas = set(app._unevaluated_pages)
    assert "chamados/solicitados" not in rotas
    assert "chamados/solicitados/[chamado_id]" not in rotas
    assert "inicio" in rotas
    assert "chamados/[chamado_id]" in rotas


def test_historico_gerente_carrega_independente_dos_comentarios(monkeypatch):
    estado = _estado_gerente()

    async def garantir(_):
        return None

    class Falso:
        async def obter_chamado(self, token, chamado_id):
            return _detalhe_gerente(detalhe_gerente())

        async def listar_comentarios_publicos(self, token, chamado_id):
            return []

        async def obter_consumo_sla_gerente(self, token, chamado_id):
            return ConsumoSLADTO(chamados_id=101, calculavel=False, motivo="linha do tempo inconsistente",
                                 consumo_ms=None, sla_horas_aplicado=2, fracao_consumida=None,
                                 faixa=None, estado_contagem=None, calculado_em=1780000005000)

        async def listar_historico_status_gerente(self, token, chamado_id):
            return [HistoricoStatusItem(9, "Resolvido", "Solução Rejeitada",
                                        1780000005000, AutorHistoricoStatus("Gerente", "Gerente"))]

    monkeypatch.setattr(ChamadosGerenteState, "_garantir_gerente", garantir)
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", Falso)
    _executar_evento(ChamadosGerenteState.carregar_detalhe, estado)
    assert estado.detalhe_carregado
    assert estado.comentarios == []
    assert estado.historico_status[0]["autor_nome"] == "Gerente"
    assert estado.consumo_sla["situacao"] == "Não calculável"
    assert estado.consumo_sla["percentual"] == ""
