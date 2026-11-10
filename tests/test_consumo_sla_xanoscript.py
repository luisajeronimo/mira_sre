"""Contrato local da função somente leitura de consumo de SLA.

Lê `calcular_consumo_sla_chamado.xs` e confere, com um modelo de referência das
regras D1–D2 de `sla-resolucao-encerramento` (tempo corrido, DS-1), que os
valores esperados de cada bloco ``test`` decorrem dos mocks declarados. Não
executa o runtime Xano: os blocos ``test`` continuam pendentes de execução lá.
"""

import re
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
FUNCAO = ROOT / "xano/function/service_desk/calcular_consumo_sla_chamado.xs"
HORA_MS = 3_600_000

CONTAM = {"Novo", "Em Atendimento", "Aguardando Solicitante", "Aguardando Mudança", "Solução Rejeitada"}
CANONICOS = CONTAM | {"Resolvido", "Encerrado", "Cancelado"}


def fonte():
    return FUNCAO.read_text(encoding="utf-8")


def _numero(valor):
    return None if valor == "null" else int(valor)


def mocks_chamados():
    trecho = fonte().split("db.query chamados", 1)[1].split("} as $chamado", 1)[0]
    mocks = {}
    for nome, corpo in re.findall(r'"([^"]+)": (\{[^\n]*\}|null)', trecho):
        if corpo == "null":
            mocks[nome] = None
            continue
        mocks[nome] = {
            "status": re.search(r'status: "([^"]+)"', corpo).group(1),
            "criado_em": _numero(re.search(r"criado_em: (\w+)", corpo).group(1)),
            "sla": _numero(re.search(r"sla_horas_aplicado: (\w+)", corpo).group(1)),
        }
    return mocks


def mocks_eventos():
    trecho = fonte().split("db.query interacoes_chamado", 1)[1].split("} as $eventos", 1)[0]
    eventos = {}
    for nome, corpo in re.findall(r'"([^"]+)": \[(.*?)\]\n', trecho, re.DOTALL):
        lista = []
        for linha in corpo.strip().splitlines():
            status = re.search(r'status: \{anterior: "([^"]+)", resultante: "([^"]+)"\}', linha)
            lista.append(
                {
                    "anterior": status.group(1) if status else None,
                    "resultante": status.group(2) if status else None,
                    "criado_em": int(re.search(r"criado_em: (\d+)", linha).group(1)),
                }
            )
        eventos[nome] = lista
    return eventos


def mocks_agora():
    trecho = fonte().split("var $agora {", 1)[1].split("\n    }\n", 1)[0]
    return {nome: int(valor) for nome, valor in re.findall(r'"([^"]+)"\s*: (\d+)', trecho)}


def instante(nome, corpo):
    """Instante de referência do teste; ausente ou 0 usa o instante atual mockado."""
    m = re.search(r"instante_referencia: (\d+)", corpo)
    if m and int(m.group(1)) != 0:
        return int(m.group(1))
    return mocks_agora()[nome]


def blocos_teste():
    blocos = {}
    for nome, corpo in re.findall(r'test "([^"]+)" \{(.*?)\n  \}', fonte(), re.DOTALL):
        esperado = dict(re.findall(r"expect\.to_equal \(\$response\.(\w+)\) \{\s*value = \"?([^\"\n]+)\"?", corpo))
        blocos[nome] = {
            "t": instante(nome, corpo),
            "esperado": esperado,
            "nulos": re.findall(r"expect\.to_be_null \(\$response\.(\w+)\)", corpo),
            "lanca": "expect.to_throw" in corpo,
        }
    return blocos


def referencia(chamado, eventos, t):
    """Modelo de referência de D1–D2; devolve o DTO esperado da função."""
    motivo = "sem_criado_em" if chamado["criado_em"] is None else None
    estado, inicio, consumo = "Novo", chamado["criado_em"], 0
    for evento in eventos:
        anterior, resultante = evento["anterior"], evento["resultante"]
        if not anterior or not resultante or anterior == resultante or motivo:
            continue
        if anterior != estado:
            motivo = "transicao_desencadeada"
        elif resultante not in CANONICOS:
            motivo = "status_fora_da_lista"
        elif evento["criado_em"] < inicio:
            motivo = "ordem_temporal_inconsistente"
        else:
            if estado in CONTAM:
                consumo += max(0, min(evento["criado_em"], t) - inicio)
            estado, inicio = resultante, evento["criado_em"]
    if motivo is None and estado != chamado["status"]:
        motivo = "status_atual_divergente"
    if motivo is None and estado in CONTAM:
        consumo += max(0, t - inicio)
    if motivo is None and not chamado["sla"]:
        motivo = "sem_sla_aplicado"
    if motivo is not None:
        return {"calculavel": False, "motivo": motivo, "consumo_ms": None, "faixa": None, "estado_contagem": None,
                "sla_horas_aplicado": chamado["sla"], "calculado_em": t}
    sla_ms = chamado["sla"] * HORA_MS
    if consumo * 10 < sla_ms * 7:
        faixa = "normal"
    elif consumo * 10 <= sla_ms * 9:
        faixa = "risco"
    elif consumo <= sla_ms:
        faixa = "critico"
    else:
        faixa = "violado"
    contagem = "em_contagem" if estado in CONTAM else "pausada" if estado == "Resolvido" else "encerrada"
    return {"calculavel": True, "motivo": None, "consumo_ms": consumo, "faixa": faixa, "estado_contagem": contagem,
            "sla_horas_aplicado": chamado["sla"], "calculado_em": t}


@pytest.mark.parametrize("nome", list(blocos_teste()))
def test_valores_esperados_decorrem_das_regras_aprovadas(nome):
    bloco = blocos_teste()[nome]
    chamado = mocks_chamados()[nome]
    if bloco["lanca"]:
        assert chamado is None
        return
    resultado = referencia(chamado, mocks_eventos()[nome], bloco["t"])
    for campo, valor in bloco["esperado"].items():
        assert str(resultado[campo]) == valor, (campo, resultado[campo], valor)
    for campo in bloco["nulos"]:
        assert resultado[campo] is None, campo


def test_cada_teste_tem_mock_proprio_nas_duas_consultas():
    testes = set(blocos_teste())
    assert testes == set(mocks_chamados())
    assert testes - {"chamado inexistente"} == set(mocks_eventos())


def test_exemplo_numerico_do_design_rejeicao_retoma_saldo():
    resultado = referencia(
        mocks_chamados()["exemplo do design com rejeicao"],
        mocks_eventos()["exemplo do design com rejeicao"],
        blocos_teste()["exemplo do design com rejeicao"]["t"],
    )
    assert resultado["consumo_ms"] == 4 * HORA_MS


def test_funcao_e_somente_leitura_interna_e_sem_filtros_rejeitados():
    texto = fonte()
    assert not re.search(r"\bdb\.(add|edit|patch|del|bulk|transaction)\b", texto)
    assert "num_min" not in texto and "num_max" not in texto
    assert "alteracao_status" not in texto
    chamadores = sorted([p.name for p in (ROOT / "xano").rglob("*.xs") if p != FUNCAO and "calcular_consumo_sla_chamado" in p.read_text(encoding="utf-8")])
    assert chamadores == ["obter_consumo_sla_gerente.xs", "obter_consumo_sla_tecnico.xs"], "exposição por DE-8 autorizada para Gerente e Técnico/Admin"


def test_estados_e_faixas_seguem_dominio_e_design():
    texto = fonte()
    for estado in CONTAM:
        assert f'$estado == "{estado}"' in texto
    for estado in CANONICOS:
        assert f'$resultante == "{estado}"' in texto
    assert "Aguardando Terceiro" not in texto.split("db.query chamados", 1)[0]
    assert "$consumo * 10 < $sla_ms * 7" in texto
    assert "$consumo * 10 <= $sla_ms * 9" in texto
    assert "$consumo <= $sla_ms" in texto
    assert "if ($duracao > 0)" in texto and "if ($duracao_final > 0)" in texto
    assert "if ($t < $fim_segmento)" in texto


def test_caminho_padrao_do_instante_de_referencia_e_testado():
    """Auditoria M-4: ausência (null ou 0) usa o instante atual, nunca 0."""
    texto = re.sub(r"\s+", "", fonte().split("\n  test ", 1)[0])
    assert "if($t==null||$t==0){var.update$t{value=$agora}}" in texto
    assert 'var$agora{value="now"|to_ms' in texto
    corpo = re.search(r'test "instante omitido usa o instante atual" \{(.*?)\n  \}', fonte(), re.S).group(1)
    assert "instante_referencia" not in corpo
    blocos = blocos_teste()
    agora = mocks_agora()
    for nome in ("instante omitido usa o instante atual", "instante zero e tratado como ausente"):
        assert blocos[nome]["esperado"]["calculado_em"] == str(agora[nome])
        assert int(blocos[nome]["esperado"]["consumo_ms"]) > 0


def test_troca_de_categoria_usa_sla_vigente_sem_reiniciar_referencia():
    bloco = blocos_teste()["troca de categoria usa sla vigente"]
    eventos = mocks_eventos()["troca de categoria usa sla vigente"]
    assert any(e["anterior"] is None for e in eventos)  # evento só de Categoria, sem status
    assert bloco["esperado"]["sla_horas_aplicado"] == "4"
    assert bloco["esperado"]["consumo_ms"] == str(3 * HORA_MS)
    assert bloco["esperado"]["faixa"] == "risco"
