"""Coerência local do pacote da prova E0.3.

Confere cobertura da matriz e isolamento do pacote. Não executa XanoScript e
não prova rollback: a prova exige o runtime Xano no datasource de teste autorizado.
"""

import re
from pathlib import Path


ROOT = Path(__file__).parents[1]
PACOTE = ROOT / "openspec/changes/archive/2026-11-11-rejeicao-solucao-gerente/prova-e03"
CENARIOS = PACOTE / "function/e03/executar_cenario.xs"
WORKFLOW = PACOTE / "workflow_test/e03_rollback.xs"

MATRIZ = {
    "controle_sem_transacao",
    "add_precondition_standard",
    "add_precondition_inputerror",
    "add_throw",
    "add_function_run_erro",
    "patch_precondition",
    "duas_escritas_segunda_falha",
}


def fonte(caminho):
    return caminho.read_text(encoding="utf-8")


def test_funcao_implementa_toda_a_matriz():
    implementados = set(re.findall(r'\$input\.cenario == "(\w+)"', fonte(CENARIOS)))
    assert implementados == MATRIZ


def test_cenarios_com_transacao_escrevem_antes_de_falhar():
    texto = fonte(CENARIOS)
    assert texto.count("db.transaction {") == len(MATRIZ) - 1
    assert "db.patch e03_prova" in texto
    assert 'function.run "e03/falhar"' in texto
    assert 'error_type = "inputerror"' in texto and 'error_type = "standard"' in texto
    assert "throw {" in texto


def test_workflow_exercita_cada_cenario_e_le_depois():
    texto = fonte(WORKFLOW)
    chamados = re.findall(r'cenario: "(\w+)", marcador: "([\w-]+)"', texto)
    assert {c for c, _ in chamados} == MATRIZ
    for _, marcador in chamados:
        assert f'$db.e03_prova.rotulo == "{marcador}"' in texto
    assert len({m for _, m in chamados}) == len(chamados)
    assert texto.count("expect.to_throw") == len(MATRIZ)
    assert 'datasource = "live"' in texto
    assert 'datasource = "mira_e03"' not in texto


def test_controle_exige_persistencia_e_demais_exigem_zero_efeito():
    texto = fonte(WORKFLOW)
    esperados = re.findall(r"expect\.to_equal \(\$(\w+)\) \{\s*value = (\d+)", texto)
    valores = dict(esperados)
    assert valores.pop("controle") == "1"
    assert valores.pop("patch_preservado") == "1"
    assert set(valores.values()) == {"0"}


def test_pacote_fica_fora_de_xano_e_nao_colide_com_o_mira():
    assert not any("e03" in p.name for p in (ROOT / "xano").rglob("*.xs"))
    guids_mira = set(re.findall(r'guid = "([^"]+)"', "".join(fonte(p) for p in (ROOT / "xano").rglob("*.xs"))))
    guids_pacote = re.findall(r'guid = "([^"]+)"', "".join(fonte(p) for p in PACOTE.rglob("*.xs")))
    assert guids_pacote and not guids_mira & set(guids_pacote)
    tabelas_mira = {p.stem for p in (ROOT / "xano/table").glob("*.xs")}
    assert "e03_prova" not in tabelas_mira
