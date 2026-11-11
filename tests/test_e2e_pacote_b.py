"""E2E somente leitura dos contratos publicados no Pacote B.

Mesmas variáveis `MIRA_E2E_*` de `test_e2e_isolamento_interacoes_gerente.py`;
sem elas, o módulo é ignorado. Somente `POST /login` e consultas `GET`.
"""

import pytest

from tests.test_e2e_isolamento_interacoes_gerente import Sessao, _publico, pytestmark  # noqa: F401


PERFIS = ("tecnico", "gerente", "diretoria", "administrador")
CAMPOS_ITEM = {"id", "titulo", "descricao", "status", "prioridade", "origem", "criado_em", "ultima_atualizacao_em", "ativo", "categoria"}
CAMPOS_DETALHE = CAMPOS_ITEM | {"criador_sistema", "solicitante", "tecnico", "loja", "resumo_totem"}
CAMPOS_HISTORICO = {"id", "status_anterior", "status_resultante", "criado_em", "autor"}
INEXISTENTE = 999999999


@pytest.fixture(scope="module")
def ctx():
    s = Sessao()
    fila = s.get("tecnico", s.service_desk + "/tecnico/chamados")
    assert fila.status_code == 200
    interacoes = s.get("tecnico", s.genericos + "/interacoes_chamado")
    assert interacoes.status_code == 200
    listas = {}
    for perfil in PERFIS:
        resposta = s.get(perfil, s.service_desk + "/solicitante/chamados")
        listas[perfil] = resposta
    yield {
        "s": s,
        "fila": {i["id"] for i in fila.json()["items"]},
        "interacoes": interacoes.json(),
        "listas": listas,
    }
    s.http.close()


def _solicitante_com_chamado(ctx):
    for perfil in PERFIS:
        itens = ctx["listas"][perfil].json()["items"]
        if itens:
            return perfil, itens
    return None, []


@pytest.mark.parametrize("perfil", PERFIS)
def test_lista_do_solicitante_por_perfil(ctx, perfil):
    resposta = ctx["listas"][perfil]
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert set(corpo) == {"items"}
    for item in corpo["items"]:
        assert set(item) == CAMPOS_ITEM
    chaves = [(-i["ultima_atualizacao_em"], -i["id"]) for i in corpo["items"]]
    assert chaves == sorted(chaves)


def test_detalhe_comentarios_e_historico_do_proprio_chamado(ctx):
    perfil, itens = _solicitante_com_chamado(ctx)
    if perfil is None:
        pytest.skip("nenhuma conta de teste é solicitante de chamado")
    s, chamado = ctx["s"], itens[0]["id"]

    detalhe = s.get(perfil, f"{s.service_desk}/solicitante/chamados/{chamado}")
    assert detalhe.status_code == 200
    dto = detalhe.json()["chamado"]
    assert set(dto) == CAMPOS_DETALHE
    assert dto["resumo_totem"] is None
    assert dto["solicitante"] is None or set(dto["solicitante"]) == {"nome"}
    assert dto["tecnico"] is None or set(dto["tecnico"]) == {"nome"}
    assert dto["loja"] is None or set(dto["loja"]) == {"id", "nome"}

    comentarios = s.get(perfil, f"{s.service_desk}/solicitante/chamados/{chamado}/comentarios")
    assert comentarios.status_code == 200
    recebidos = {c["id"] for c in comentarios.json()["items"]}
    esperados = {i["id"] for i in ctx["interacoes"] if i.get("chamados_id") == chamado and _publico(i)}
    assert recebidos == esperados
    for c in comentarios.json()["items"]:
        assert set(c) == {"id", "conteudo", "criado_em", "autor"}

    historico = s.get(perfil, f"{s.service_desk}/solicitante/chamados/{chamado}/historico-status")
    assert historico.status_code == 200
    for entrada in historico.json()["items"]:
        assert set(entrada) == CAMPOS_HISTORICO
        assert entrada["status_anterior"] != entrada["status_resultante"]
        assert entrada["autor"] is None or set(entrada["autor"]) == {"nome", "perfil"}


@pytest.mark.parametrize("sufixo", ["", "/comentarios", "/historico-status"])
def test_chamado_alheio_e_inexistente_tem_a_mesma_resposta_404(ctx, sufixo):
    perfil, itens = _solicitante_com_chamado(ctx)
    perfil = perfil or "gerente"
    proprios = {i["id"] for i in itens}
    alheio = next(iter(sorted(ctx["fila"] - proprios)), None)
    s = ctx["s"]
    for chamado in [c for c in (alheio, INEXISTENTE) if c is not None]:
        resposta = s.get(perfil, f"{s.service_desk}/solicitante/chamados/{chamado}{sufixo}")
        assert resposta.status_code == 404, (chamado, resposta.status_code)
        assert "titulo" not in resposta.text and "conteudo" not in resposta.text


def test_historico_do_gerente_nega_outra_loja_e_outros_perfis(ctx):
    s = ctx["s"]
    proprios_gerente = s.get("gerente", s.service_desk + "/gerente/chamados").json()["items"]
    outro = next(iter(sorted(ctx["fila"] - {i["id"] for i in proprios_gerente})), None)
    if outro is not None:
        assert s.get("gerente", f"{s.service_desk}/gerente/chamados/{outro}/historico-status").status_code == 403
        assert s.get("tecnico", f"{s.service_desk}/gerente/chamados/{outro}/historico-status").status_code == 403
    assert s.get("gerente", f"{s.service_desk}/gerente/chamados/{INEXISTENTE}/historico-status").status_code == 404


def test_sem_token_401(ctx):
    s = ctx["s"]
    assert s.get(None, s.service_desk + "/solicitante/chamados").status_code == 401
