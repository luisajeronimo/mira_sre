"""Correção C-1: GETs genéricos de `chamados` autorizam o Gerente pela Loja histórica.

Change `corrigir-gerente-gets-genericos-loja-historica`. Testes locais de
contrato sobre o XanoScript versionado e de coerência dos testes nativos com um
modelo de referência da regra aprovada (spec `autorizacao-perfis`, requisito
"Gerente usa Loja histórica comprovada do chamado"). Não executam o runtime
Xano: a negação efetiva em runtime é verificada pelos testes nativos da função
nova e pelo E2E somente leitura `test_e2e_c1_gets_genericos.py`, ambos
pendentes de publicação autorizada.
"""

import re
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
LISTA = ROOT / "xano/api/apis_from_table_chamados/chamados_GET.xs"
DETALHE = ROOT / "xano/api/apis_from_table_chamados/chamados/chamados_id_GET.xs"
FILTRO = ROOT / "xano/function/service_desk/listar_chamados_loja_historica_gerente.xs"
AUTORIZADOR = ROOT / "xano/function/service_desk/obter_chamado_gerente_autorizado.xs"

LOJA_ATUAL = re.compile(r"\$db\.ativo\.lojas_id|\$ativo\.lojas_id|exigir_escopo_loja")


def fonte(caminho):
    return caminho.read_text(encoding="utf-8")


def logica(caminho):
    """Texto sem comentários e sem blocos de teste."""
    texto = fonte(caminho).split("\n  test ", 1)[0]
    return "\n".join(l for l in texto.splitlines() if not l.strip().startswith("//"))


def compacto(texto):
    return re.sub(r"\s+", "", texto)


def viola_c1(texto):
    """Verdadeiro se o contrato decide o acesso do Gerente pela Loja atual do Totem."""
    return bool(LOJA_ATUAL.search(texto))


# --- Detector de regressão ---------------------------------------------------

VULNERAVEL_LISTA = 'where = $usuario.role == "tecnico" || ($usuario.role == "gerente" && $db.ativo.lojas_id == $usuario.lojas_id)'
VULNERAVEL_DETALHE = 'function.run "autorizacao/exigir_escopo_loja" { input = {usuarios_id: $auth.id, lojas_id: $ativo.lojas_id} }'


@pytest.mark.parametrize("trecho", [VULNERAVEL_LISTA, VULNERAVEL_DETALHE])
def test_detector_reconhece_o_padrao_vulneravel(trecho):
    assert viola_c1(trecho)


@pytest.mark.parametrize("caminho", [LISTA, DETALHE, FILTRO])
def test_contratos_nao_usam_loja_atual_do_totem(caminho):
    assert not viola_c1(logica(caminho)), caminho.name


# --- Lista -------------------------------------------------------------------

def test_lista_exige_perfil_e_mantem_administrador_negado():
    texto = compacto(logica(LISTA))
    assert 'auth="usuarios"' in texto
    assert compacto('function.run "autorizacao/exigir_perfil"') in texto
    assert "gerente:true" in texto and "tecnico:true" in texto and "diretoria:true" in texto
    assert "administrador" not in texto


def test_lista_do_gerente_vem_somente_da_funcao_historica():
    texto = logica(LISTA)
    ramo_gerente = texto.split('if ($usuario.role == "gerente")', 1)[1].split("else {", 1)[0]
    assert 'function.run "service_desk/listar_chamados_loja_historica_gerente"' in ramo_gerente
    assert "db.query" not in ramo_gerente
    # A consulta global existe somente no ramo que exigir_perfil limita a Técnico e Diretoria.
    assert texto.count("db.query chamados") == 1
    assert texto.index("else {") < texto.index("db.query chamados")
    assert "join" not in texto
    assert "response = $chamados" in texto


def test_lista_nao_recebe_parametros_de_paginacao_ou_filtro():
    texto = compacto(logica(LISTA))
    assert "input{}" in texto


# --- Detalhe -----------------------------------------------------------------

def test_detalhe_autoriza_gerente_pela_loja_historica_antes_de_ler_o_registro():
    texto = logica(DETALHE)
    perfil = texto.index('function.run "autorizacao/exigir_perfil"')
    autorizador = texto.index('function.run "service_desk/obter_chamado_gerente_autorizado"')
    leitura = texto.index("db.get chamados")
    assert perfil < autorizador < leitura
    ramo = texto.split('if ($usuario.role == "gerente")', 1)[1].split("db.get chamados", 1)[0]
    assert "chamados_id: $input.chamados_id" in ramo
    assert "db.get ativos_referencia" not in texto
    assert "administrador" not in texto
    assert texto.index("db.get chamados") < texto.index("precondition ($chamados != null)")


def test_autorizador_reutilizado_decide_pela_loja_resolvida_no_instante_de_abertura():
    texto = compacto(logica(AUTORIZADOR))
    assert compacto('function.run "administracao/resolver_loja_totem_no_instante"') in texto
    assert compacto("instante: $registro.criado_em") in texto
    assert compacto("precondition ($historico.lojas_id != null && $historico.lojas_id == $usuario.lojas_id)") in texto
    assert compacto('error_type = "accessdenied"') in texto
    nomes = re.findall(r'^  test "([^"]+)"', fonte(AUTORIZADOR), re.M)
    assert {"rejeita chamado de outra loja", "rejeita gerente sem loja", "rejeita chamado inexistente"} <= set(nomes)


# --- Função nova: contrato ----------------------------------------------------

def test_filtro_usa_resolvedor_com_criado_em_e_igualdade_nao_nula():
    texto = compacto(logica(FILTRO))
    assert compacto('function.run "autorizacao/exigir_perfil"') in texto and "gerente:true" in texto
    assert compacto("precondition ($usuario.lojas_id != null)") in texto
    assert "join" not in texto and "ativos_referencia{" not in texto
    assert compacto("instante: $chamado.criado_em") in texto
    assert compacto("if ($chamado.ativos_referencia_id != null && $chamado.ativos_referencia_id != 0 && $chamado.criado_em != null)") in texto
    assert compacto("if ($loja_historica_id != null && $loja_historica_id == $usuario.lojas_id)") in texto
    assert compacto("response = $autorizados") in texto


# --- Função nova: testes nativos coerentes com o modelo de referência ----------

def _mocks(trecho_inicio, trecho_fim):
    corpo = fonte(FILTRO).split(trecho_inicio, 1)[1].split(trecho_fim, 1)[0]
    return dict(re.findall(r'^\s*"([^"]+)"\s*:\s*(.+)$', corpo, re.M))


def _valor(texto):
    texto = texto.strip()
    if texto == "null":
        return None
    if texto == "[]":
        return []
    lojas = re.search(r"lojas_id: (\w+)", texto)
    if lojas and not texto.startswith("["):
        return None if lojas.group(1) == "null" else int(lojas.group(1))
    itens = []
    for item in re.findall(r"\{([^}]*)\}", texto):
        campos = dict(re.findall(r"(\w+): (\"[^\"]*\"|\w+)", item))
        itens.append({k: (None if v == "null" else v.strip('"') if v.startswith('"') else int(v)) for k, v in campos.items()})
    return itens


def modelo(loja_usuario, chamados, resolver):
    """Regra aprovada: somente Loja comprovada na abertura igual à do Gerente."""
    if loja_usuario is None:
        raise PermissionError("Acesso não autorizado.")
    autorizados = []
    for chamado in chamados:
        if not chamado.get("ativos_referencia_id") or chamado.get("criado_em") is None:
            continue
        loja = resolver(chamado)
        if loja is not None and loja == loja_usuario:
            autorizados.append(chamado)
    return autorizados


def blocos():
    return dict(re.findall(r'^  test "([^"]+)" \{(.*?)^  \}', fonte(FILTRO), re.M | re.S))


@pytest.mark.parametrize("nome", sorted(blocos()))
def test_esperados_nativos_decorrem_da_regra(nome):
    usuarios = {k: _valor(v) for k, v in _mocks('function.run "autorizacao/exigir_perfil"', "} as $usuario").items()}
    consultas = {k: _valor(v) for k, v in _mocks("db.query chamados", "} as $chamados").items()}
    historicos = {k: _valor(v) for k, v in _mocks('function.run "administracao/resolver_loja_totem_no_instante"', "} as $historico").items()}
    corpo = blocos()[nome]
    chamados = consultas.get(nome, [])

    def resolver(_chamado):
        assert nome in historicos, f"resolvedor chamado sem mock em {nome!r}"
        return historicos[nome]

    if "expect.to_throw" in corpo:
        with pytest.raises(PermissionError):
            modelo(usuarios[nome], chamados, resolver)
        return
    resultado = modelo(usuarios[nome], chamados, resolver)
    if "expect.to_be_empty ($response)" in corpo:
        assert resultado == []
    else:
        esperado = _valor(re.search(r"value = (\[.*\])", corpo).group(1))
        assert resultado == esperado


def test_testes_nativos_cobrem_a_matriz_da_c1():
    nomes = set(blocos())
    assert {
        "inclui chamado da loja historica com totem transferido",
        "exclui chamado de outra loja historica",
        "exclui chamado sem vinculo historico",
        "exclui chamado sem totem",
        "rejeita gerente sem loja",
    } <= nomes


def test_cenario_de_regressao_tem_loja_historica_diferente_da_do_gerente():
    usuarios = _mocks('function.run "autorizacao/exigir_perfil"', "} as $usuario")
    historicos = _mocks('function.run "administracao/resolver_loja_totem_no_instante"', "} as $historico")
    nome = "exclui chamado de outra loja historica"
    assert _valor(usuarios[nome]) == 1 and _valor(historicos[nome]) == 2
