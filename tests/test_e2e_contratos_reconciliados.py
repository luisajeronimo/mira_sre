"""E2E HTTP sem escrita dos contratos reconciliados com o Xano publicado."""

import re

import pytest

from tests.test_e2e_isolamento_interacoes_gerente import ROOT, Sessao, pytestmark  # noqa: F401


@pytest.fixture(scope="module")
def sessao():
    cliente = Sessao()
    yield cliente
    cliente.http.close()


def test_administrador_nao_abre_chamado_pelo_contrato_do_gerente(sessao):
    resposta = sessao._pedir(
        "POST",
        sessao.service_desk + "/gerente/chamados",
        headers=sessao.cabecalhos["administrador"],
        json={},
    )
    assert resposta.status_code == 403


def test_opcoes_de_loja_excluem_status_inativo(sessao):
    base = sessao.auth + "/administracao/lojas"
    resposta = sessao.get("administrador", base)
    cadastro = sessao.get("administrador", base + "/registros")
    assert resposta.status_code == cadastro.status_code == 200
    opcoes = resposta.json()["lojas"]
    registros = cadastro.json()["items"]
    ativos = {loja["id"] for loja in registros if loja["status"] in {"Ativa", "ativa", "Ativo"}}
    inativos = {loja["id"] for loja in registros if loja["status"] not in {"Ativa", "ativa", "Ativo"}}
    assert {loja["id"] for loja in opcoes} == ativos
    assert all(set(loja) == {"id", "nome"} for loja in opcoes)
    if not inativos:
        pytest.skip("sem Loja inativa no ambiente para provar a exclusão em HTTP")
    assert not {loja["id"] for loja in opcoes} & inativos


def test_simulator_sem_chave_recebe_401_com_corpo_exato(sessao):
    grupo = (ROOT / "xano/api/apis_from_table_telemetria_equipamentos/apis_from_table_telemetria_equipamentos.xs").read_text(encoding="utf-8")
    canonical = re.search(r'canonical = "([^"]+)"', grupo).group(1)
    origem = sessao.auth.split("/api:", 1)[0]
    resposta = sessao._pedir("POST", f"{origem}/api:{canonical}/telemetria_equipamentos", json={})
    assert resposta.status_code == 401
    assert resposta.json() == {"error": "Não autenticado."}
