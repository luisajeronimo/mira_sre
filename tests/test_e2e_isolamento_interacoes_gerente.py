"""E2E somente leitura: isolamento de interações do Gerente (tasks 2.2 e 2.3).

Executa contra o Xano publicado apenas quando as variáveis abaixo estão
definidas; caso contrário, o módulo é ignorado. Credenciais e tokens ficam só
em memória. Somente `POST /login` e consultas `GET`; nenhum dado é alterado.

    MIRA_E2E_ORIGEM            ex.: https://<instância>.xano.io
    MIRA_E2E_SENHA
    MIRA_E2E_EMAIL_TECNICO, MIRA_E2E_EMAIL_GERENTE,
    MIRA_E2E_EMAIL_DIRETORIA, MIRA_E2E_EMAIL_ADMINISTRADOR

A "própria Loja" do Gerente é o conjunto de chamados devolvido pelo contrato
publicado `GET gerente/chamados`; "outra Loja" é o restante da fila global.
"""

import os
import re
import time
from pathlib import Path

import httpx
import pytest


ROOT = Path(__file__).parents[1]
VARIAVEIS = (
    "MIRA_E2E_ORIGEM",
    "MIRA_E2E_SENHA",
    "MIRA_E2E_EMAIL_TECNICO",
    "MIRA_E2E_EMAIL_GERENTE",
    "MIRA_E2E_EMAIL_DIRETORIA",
    "MIRA_E2E_EMAIL_ADMINISTRADOR",
)
pytestmark = pytest.mark.skipif(
    not all(os.getenv(v) for v in VARIAVEIS),
    reason="E2E HTTP: variáveis MIRA_E2E_* não definidas",
)

# Plano Free: 10 requisições a cada 20 s.
PAUSA_SEGUNDOS = 2.5
TENTATIVAS_429 = 5
TIPOS_COMENTARIO = (None, "", "comentario")


def _canonical(arquivo):
    texto = (ROOT / arquivo).read_text(encoding="utf-8")
    return re.search(r'canonical = "([^"]+)"', texto).group(1)


class Sessao:
    def __init__(self):
        origem = os.environ["MIRA_E2E_ORIGEM"].rstrip("/")
        self.auth = f"{origem}/api:{_canonical('xano/api/mira_auth/mira_auth.xs')}"
        self.service_desk = f"{origem}/api:{_canonical('xano/api/mira_service_desk/mira_service_desk.xs')}"
        self.genericos = f"{origem}/api:" + _canonical(
            "xano/api/apis_from_table_interacoes_chamado/apis_from_table_interacoes_chamado.xs"
        )
        self.http = httpx.Client(timeout=30)
        self.cabecalhos = {}
        for perfil in ("tecnico", "gerente", "diretoria", "administrador"):
            resposta = self._pedir("POST", self.auth + "/login", json={
                "email": os.environ[f"MIRA_E2E_EMAIL_{perfil.upper()}"],
                "senha": os.environ["MIRA_E2E_SENHA"],
            })
            assert resposta.status_code == 200, (perfil, resposta.status_code)
            self.cabecalhos[perfil] = {"Authorization": "Bearer " + resposta.json()["authToken"]}

    def _pedir(self, metodo, url, **kwargs):
        # O limite do Free é compartilhado pelo workspace; 429 aguarda e repete.
        for _ in range(TENTATIVAS_429):
            time.sleep(PAUSA_SEGUNDOS)
            resposta = self.http.request(metodo, url, **kwargs)
            if resposta.status_code != 429:
                return resposta
            espera = resposta.headers.get("Retry-After", "")
            time.sleep(float(espera) if espera.replace(".", "", 1).isdigit() else 20)
        return resposta

    def get(self, perfil, url):
        return self._pedir("GET", url, headers=self.cabecalhos.get(perfil, {}))


@pytest.fixture(scope="module")
def ctx():
    s = Sessao()
    gerente = s.get("gerente", s.service_desk + "/gerente/chamados")
    assert gerente.status_code == 200
    proprios = {item["id"] for item in gerente.json()["items"]}
    fila = s.get("tecnico", s.service_desk + "/tecnico/chamados")
    assert fila.status_code == 200
    todos = {item["id"] for item in fila.json()["items"]}
    interacoes = s.get("tecnico", s.genericos + "/interacoes_chamado")
    assert interacoes.status_code == 200
    itens = interacoes.json()
    yield {
        "s": s,
        "proprios": proprios,
        "outros": todos - proprios,
        "interacoes": itens,
        "total_tecnico": len(itens),
    }
    s.http.close()


def _publico(i):
    return i.get("tipo_evento") in TIPOS_COMENTARIO and i.get("visibilidade") == "publica" and (i.get("mensagem") or "") != ""


def _interno(i):
    return i.get("tipo_evento") in TIPOS_COMENTARIO and i.get("visibilidade") != "publica"


def _evento(i):
    return i.get("tipo_evento") not in TIPOS_COMENTARIO


def _primeira(ctx, chamados, criterio):
    return next((i for i in ctx["interacoes"] if i.get("chamados_id") in chamados and criterio(i)), None)


# Task 2.2 — GET /interacoes_chamado/{id} nega o Gerente antes de ler


@pytest.mark.parametrize("criterio", [_publico, _interno, _evento], ids=["comentario-publico", "comentario-interno", "evento-operacional"])
def test_2_2_gerente_403_para_interacao_da_propria_loja(ctx, criterio):
    alvo = _primeira(ctx, ctx["proprios"], criterio)
    if alvo is None:
        pytest.skip("sem interação desse tipo em chamado da própria Loja")
    s = ctx["s"]
    resposta = s.get("gerente", f"{s.genericos}/interacoes_chamado/{alvo['id']}")
    assert resposta.status_code == 403
    assert "mensagem" not in resposta.text and "visibilidade" not in resposta.text


def test_2_2_gerente_403_para_identificador_inexistente(ctx):
    s = ctx["s"]
    assert s.get("gerente", f"{s.genericos}/interacoes_chamado/999999999").status_code == 403


def test_2_2_tecnico_preservado(ctx):
    s = ctx["s"]
    alvo = ctx["interacoes"][0]
    resposta = s.get("tecnico", f"{s.genericos}/interacoes_chamado/{alvo['id']}")
    assert resposta.status_code == 200 and resposta.json()["id"] == alvo["id"]
    assert s.get("tecnico", f"{s.genericos}/interacoes_chamado/999999999").status_code == 404


# Task 2.3 (a) e (b) — contrato funcional de comentários públicos do Gerente


def _chamado_proprio_com_comentario_publico(ctx):
    candidatos = [c for c in ctx["proprios"] if any(i.get("chamados_id") == c and _publico(i) for i in ctx["interacoes"])]
    # Prefere chamado que também tenha conteúdo restrito, para exercitar (b).
    candidatos.sort(key=lambda c: not any(i.get("chamados_id") == c and (_interno(i) or _evento(i)) for i in ctx["interacoes"]))
    return candidatos[0] if candidatos else None


def test_2_3_a_b_gerente_recebe_somente_comentarios_publicos_da_propria_loja(ctx):
    chamado = _chamado_proprio_com_comentario_publico(ctx)
    if chamado is None:
        pytest.skip("sem chamado da própria Loja com comentário público")
    s = ctx["s"]
    resposta = s.get("gerente", f"{s.service_desk}/gerente/chamados/{chamado}/comentarios")
    assert resposta.status_code == 200
    itens = resposta.json()["items"]
    do_chamado = [i for i in ctx["interacoes"] if i.get("chamados_id") == chamado]
    esperados = {i["id"] for i in do_chamado if _publico(i)}
    restritos = {i["id"] for i in do_chamado if _interno(i) or _evento(i)}
    recebidos = {i["id"] for i in itens}
    assert recebidos == esperados
    assert not recebidos & restritos
    for item in itens:
        assert set(item) == {"id", "conteudo", "criado_em", "autor"}
        assert item["autor"] is None or set(item["autor"]) == {"nome"}
    criados = [i["criado_em"] for i in itens]
    assert criados == sorted(criados, reverse=True)


def test_2_3_b_gerente_nao_obtem_interacoes_pelos_genericos(ctx):
    s = ctx["s"]
    assert s.get("gerente", s.genericos + "/interacoes_chamado").status_code == 403


# Task 2.3 (c) — outra Loja


def test_2_3_c_gerente_403_em_chamado_e_comentarios_de_outra_loja(ctx):
    if not ctx["outros"]:
        pytest.skip("sem chamado de outra Loja na fila global")
    s = ctx["s"]
    com_interacao = [c for c in ctx["outros"] if any(i.get("chamados_id") == c for i in ctx["interacoes"])]
    chamado = (com_interacao or sorted(ctx["outros"]))[0]
    assert s.get("gerente", f"{s.service_desk}/gerente/chamados/{chamado}").status_code == 403
    comentarios = s.get("gerente", f"{s.service_desk}/gerente/chamados/{chamado}/comentarios")
    assert comentarios.status_code == 403
    alvo = _primeira(ctx, {chamado}, lambda i: True)
    if alvo is not None:
        assert s.get("gerente", f"{s.genericos}/interacoes_chamado/{alvo['id']}").status_code == 403


# Task 2.3 (d) — Técnico, Diretoria e Administrador preservados


def test_2_3_d_tecnico_mantem_resultado_dos_genericos(ctx):
    assert ctx["total_tecnico"] > 0


@pytest.mark.parametrize("perfil", ["diretoria", "administrador"])
def test_2_3_d_diretoria_e_administrador_preservados(ctx, perfil):
    s = ctx["s"]
    assert s.get(perfil, s.genericos + "/interacoes_chamado").status_code == 403
    assert s.get(perfil, s.service_desk + "/tecnico/chamados").status_code == 200
    chamado = next(iter(ctx["proprios"] or ctx["outros"]))
    assert s.get(perfil, f"{s.service_desk}/gerente/chamados/{chamado}/comentarios").status_code == 403
