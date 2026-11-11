"""E2E de leitura e negação dos contratos publicados na Sprint 3.

Usa as variáveis MIRA_E2E_* do módulo de isolamento. Não executa rejeição
válida nem o comando de encerramento, pois ambos alterariam dados reais.
"""

import pytest

from tests.test_e2e_isolamento_interacoes_gerente import Sessao, pytestmark  # noqa: F401


INEXISTENTE = 999999999


@pytest.fixture(scope="module")
def ctx():
    sessao = Sessao()
    gerente = sessao.get("gerente", sessao.service_desk + "/gerente/chamados")
    tecnico = sessao.get("tecnico", sessao.service_desk + "/tecnico/chamados")
    assert gerente.status_code == tecnico.status_code == 200
    proprios = {item["id"] for item in gerente.json()["items"]}
    fila = {item["id"] for item in tecnico.json()["items"]}
    yield sessao, proprios, fila
    sessao.http.close()


def test_consumo_sla_tecnico_e_administrador(ctx):
    sessao, _, fila = ctx
    if not fila:
        pytest.skip("fila técnica sem chamados")
    chamado = min(fila)
    for perfil in ("tecnico", "administrador"):
        resposta = sessao.get(perfil, f"{sessao.service_desk}/tecnico/chamados/{chamado}/consumo-sla")
        assert resposta.status_code == 200, (perfil, resposta.status_code)
        consumo = resposta.json()["consumo_sla"]
        assert consumo["chamados_id"] == chamado
        assert isinstance(consumo["calculavel"], bool)


def test_consumo_sla_gerente_isolado_por_loja(ctx):
    sessao, proprios, fila = ctx
    if proprios:
        chamado = min(proprios)
        resposta = sessao.get("gerente", f"{sessao.service_desk}/gerente/chamados/{chamado}/consumo-sla")
        assert resposta.status_code == 200
        assert resposta.json()["consumo_sla"]["chamados_id"] == chamado
    outro = next(iter(sorted(fila - proprios)), None)
    if outro is not None:
        resposta = sessao.get("gerente", f"{sessao.service_desk}/gerente/chamados/{outro}/consumo-sla")
        assert resposta.status_code == 403
    assert sessao.get("gerente", f"{sessao.service_desk}/gerente/chamados/{INEXISTENTE}/consumo-sla").status_code == 404


def test_consumo_sla_nega_perfil_e_anonimo(ctx):
    sessao, _, fila = ctx
    chamado = min(fila) if fila else INEXISTENTE
    assert sessao.get("gerente", f"{sessao.service_desk}/tecnico/chamados/{chamado}/consumo-sla").status_code == 403
    assert sessao.get(None, f"{sessao.service_desk}/tecnico/chamados/{chamado}/consumo-sla").status_code == 401
    assert sessao.get("tecnico", f"{sessao.service_desk}/tecnico/chamados/{INEXISTENTE}/consumo-sla").status_code == 404


def test_rejeicao_nega_outro_perfil_e_anonimo_sem_mutacao(ctx):
    sessao, proprios, fila = ctx
    chamado = min(proprios or fila) if proprios or fila else INEXISTENTE
    url = f"{sessao.service_desk}/gerente/chamados/{chamado}/rejeitar-solucao"
    dados = {"justificativa": "Teste de autorização", "ultima_atualizacao_em": 0}
    assert sessao._pedir("POST", url, json=dados).status_code == 401
    assert sessao._pedir("POST", url, headers=sessao.cabecalhos["tecnico"], json=dados).status_code == 403
    outro = next(iter(sorted(fila - proprios)), None)
    if outro is not None:
        url_alheia = f"{sessao.service_desk}/gerente/chamados/{outro}/rejeitar-solucao"
        assert sessao._pedir("POST", url_alheia, headers=sessao.cabecalhos["gerente"], json=dados).status_code == 403


def test_comando_encerramento_nega_chave_ausente_e_invalida(ctx):
    sessao, _, _ = ctx
    url = f"{sessao.service_desk}/automacao/encerrar-resolvidos"
    assert sessao._pedir("POST", url).status_code == 401
    assert sessao._pedir("POST", url, headers={"X-Mira-Encerramento-Key": "chave-invalida"}).status_code == 401
