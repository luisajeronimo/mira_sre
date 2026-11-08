"""E2E somente leitura da correção C-1 nos GETs genéricos de `chamados`.

Mesmas variáveis `MIRA_E2E_*` de `test_e2e_isolamento_interacoes_gerente.py`;
sem elas, o módulo é ignorado. Somente `POST /login` e consultas `GET`; nenhum
dado é alterado. Deve ser executado depois da publicação autorizada da change
`corrigir-gerente-gets-genericos-loja-historica`.

Referência de escopo: `GET gerente/chamados` (contrato funcional que já aplica
a Loja histórica). O contrato genérico não pode expor ao Gerente nada além dele.
"""

import re

import pytest

from tests.test_e2e_isolamento_interacoes_gerente import ROOT, Sessao, pytestmark  # noqa: F401


def _genericos_chamados(s):
    texto = (ROOT / "xano/api/apis_from_table_chamados/apis_from_table_chamados.xs").read_text(encoding="utf-8")
    origem = s.auth.split("/api:", 1)[0]
    return f"{origem}/api:" + re.search(r'canonical = "([^"]+)"', texto).group(1)


@pytest.fixture(scope="module")
def ctx():
    s = Sessao()
    base = _genericos_chamados(s)
    funcional = s.get("gerente", s.service_desk + "/gerente/chamados")
    assert funcional.status_code == 200
    fila = s.get("tecnico", s.service_desk + "/tecnico/chamados")
    assert fila.status_code == 200
    proprios = {i["id"] for i in funcional.json()["items"]}
    yield {"s": s, "base": base, "proprios": proprios, "outros": {i["id"] for i in fila.json()["items"]} - proprios}
    s.http.close()


def test_lista_generica_do_gerente_nao_excede_a_loja_historica(ctx):
    resposta = ctx["s"].get("gerente", ctx["base"] + "/chamados")
    assert resposta.status_code == 200
    ids = {c["id"] for c in resposta.json()}
    assert ids <= ctx["proprios"], sorted(ids - ctx["proprios"])
    assert ids == ctx["proprios"]


def test_detalhe_generico_nega_chamado_fora_da_loja_historica(ctx):
    if not ctx["outros"]:
        pytest.skip("sem chamado fora da Loja histórica do Gerente na fila global")
    for chamado_id in sorted(ctx["outros"])[:3]:
        resposta = ctx["s"].get("gerente", f"{ctx['base']}/chamados/{chamado_id}")
        assert resposta.status_code in (403, 404), (chamado_id, resposta.status_code)
        assert "titulo" not in resposta.text


def test_detalhe_generico_libera_chamado_da_loja_historica(ctx):
    if not ctx["proprios"]:
        pytest.skip("Gerente de teste sem chamado com Loja histórica")
    chamado_id = min(ctx["proprios"])
    resposta = ctx["s"].get("gerente", f"{ctx['base']}/chamados/{chamado_id}")
    assert resposta.status_code == 200
    assert resposta.json()["id"] == chamado_id


def test_tecnico_e_diretoria_mantem_consulta_global(ctx):
    total = len(ctx["proprios"] | ctx["outros"])
    for perfil in ("tecnico", "diretoria"):
        resposta = ctx["s"].get(perfil, ctx["base"] + "/chamados")
        assert resposta.status_code == 200
        assert len(resposta.json()) >= total


def test_administrador_e_anonimo_continuam_negados(ctx):
    assert ctx["s"].get("administrador", ctx["base"] + "/chamados").status_code == 403
    assert ctx["s"].get("anonimo", ctx["base"] + "/chamados").status_code == 401
