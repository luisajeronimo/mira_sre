"""Contrato estático dos contratos de leitura do solicitante e do histórico.

Os testes leem o XanoScript versionado. Eles não executam o runtime Xano e não
substituem os testes XanoScript (blocos ``test``) nem os testes HTTP integrados.
"""

import re
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
FUNCOES = ROOT / "xano/function/service_desk"
API = ROOT / "xano/api/mira_service_desk"

HISTORICO = FUNCOES / "listar_historico_status.xs"
HISTORICO_GERENTE = FUNCOES / "listar_historico_status_gerente.xs"
HISTORICO_SOLICITANTE = FUNCOES / "listar_historico_status_solicitante.xs"
AUTORIZADO_SOLICITANTE = FUNCOES / "obter_chamado_solicitante_autorizado.xs"
LISTA_SOLICITANTE = FUNCOES / "listar_chamados_solicitante.xs"
DETALHE_SOLICITANTE = FUNCOES / "obter_chamado_solicitante.xs"
COMENTARIOS_SOLICITANTE = FUNCOES / "listar_comentarios_publicos_solicitante.xs"
COMENTARIOS_GERENTE = FUNCOES / "listar_comentarios_publicos_gerente.xs"
DETALHE_GERENTE = FUNCOES / "obter_chamado_gerente.xs"
LISTA_GERENTE = FUNCOES / "listar_chamados_gerente.xs"

ENDPOINTS = {
    API / "gerente/chamados/chamados_id_historico-status_GET.xs": "service_desk/listar_historico_status_gerente",
    API / "solicitante/chamados_GET.xs": "service_desk/listar_chamados_solicitante",
    API / "solicitante/chamados/chamados_id_GET.xs": "service_desk/obter_chamado_solicitante",
    API / "solicitante/chamados/chamados_id_comentarios_GET.xs": "service_desk/listar_comentarios_publicos_solicitante",
    API / "solicitante/chamados/chamados_id_historico-status_GET.xs": "service_desk/listar_historico_status_solicitante",
}

NOVOS = [
    HISTORICO,
    HISTORICO_GERENTE,
    HISTORICO_SOLICITANTE,
    AUTORIZADO_SOLICITANTE,
    LISTA_SOLICITANTE,
    DETALHE_SOLICITANTE,
    COMENTARIOS_SOLICITANTE,
    *ENDPOINTS,
]


def fonte(caminho):
    return caminho.read_text(encoding="utf-8")


def sem_mocks(texto):
    """Remove blocos ``mock = {...}`` para analisar somente a lógica."""
    resultado, profundidade, i = [], 0, 0
    while i < len(texto):
        if profundidade == 0 and texto.startswith("mock = {", i):
            profundidade, i = 1, i + len("mock = {")
            continue
        if profundidade:
            profundidade += {"{": 1, "}": -1}.get(texto[i], 0)
            i += 1
            continue
        resultado.append(texto[i])
        i += 1
    return "".join(resultado)


def logica(caminho):
    texto = sem_mocks(fonte(caminho))
    texto = "\n".join(linha for linha in texto.splitlines() if not linha.lstrip().startswith("//"))
    fim = texto.find("\n  response =")
    return texto[: fim if fim >= 0 else len(texto)]


def where(texto):
    return re.findall(r"where = (.+)", texto)


@pytest.mark.parametrize("caminho", NOVOS, ids=lambda p: p.stem)
def test_contratos_novos_sao_somente_leitura(caminho):
    assert not re.search(r"\bdb\.(add|edit|patch|del|bulk|transaction)\b", logica(caminho))
    assert "alteracao_status" not in fonte(caminho)


@pytest.mark.parametrize("endpoint,funcao", ENDPOINTS.items(), ids=lambda v: getattr(v, "stem", v))
def test_endpoints_delegam_com_identidade_da_sessao(endpoint, funcao):
    texto = fonte(endpoint)
    assert 'api_group = "MIRA Service Desk"' in texto
    assert 'auth = "usuarios"' in texto
    assert f'function.run "{funcao}"' in texto
    assert "usuarios_id: $auth.id" in texto
    entradas = re.search(r"input \{(.*?)\n  \}", texto, re.DOTALL).group(1).split()
    assert entradas in ([], ["int", "chamados_id", "filters=min:1"])


def test_guids_novos_sao_unicos_no_repositorio():
    guids = re.findall(r'guid = "([^"]+)"', "".join(fonte(p) for p in (ROOT / "xano").rglob("*.xs")))
    novos = [re.search(r'guid = "([^"]+)"', fonte(p)).group(1) for p in NOVOS]
    for guid in novos:
        assert guids.count(guid) == 1, guid


def test_historico_seleciona_por_tipo_e_chamado_sem_visibilidade():
    texto = logica(HISTORICO)
    assert where(texto) == [
        '$db.interacoes_chamado.chamados_id == $input.chamados_id && $db.interacoes_chamado.tipo_evento == "alteracao_chamado"'
    ]
    assert "visibilidade" not in "".join(where(texto))
    assert 'sort = {interacoes_chamado.criado_em: "desc", interacoes_chamado.id: "desc"}' in texto


def test_historico_exige_transicao_valida_sem_completar_valores():
    texto = logica(HISTORICO)
    for condicao in (
        "($evento.alteracoes|is_object)",
        '$evento.alteracoes|get:"status":null',
        "($par|is_object)",
        '$par|get:"anterior":null',
        '$par|get:"resultante":null',
        "($anterior|is_text)",
        "($resultante|is_text)",
        '$anterior != ""',
        '$resultante != ""',
        "$anterior != $resultante",
        "$evento.criado_em != null",
    ):
        assert condicao in texto
    assert "created_at" not in texto
    # Sem acesso por ponto a chaves possivelmente ausentes do campo `json`.
    assert "$evento.alteracoes.status" not in texto
    assert "$par.anterior" not in texto and "$par.resultante" not in texto


def test_xanoscript_test_blocks_sem_construcoes_rejeitadas_pelo_parser():
    """O parser do Developer MCP 2.2.6 rejeita filtros e índices dentro de ``expect``."""
    for caminho in NOVOS:
        for argumento in re.findall(r"expect\.[a-z_]+ \(([^)]*)\)", fonte(caminho)):
            assert "|" not in argumento and "[" not in argumento, (caminho.name, argumento)


def test_historico_projeta_dto_fechado_sem_dados_internos():
    texto = logica(HISTORICO)
    projecao = texto[texto.index("array.push $items"):]
    for campo in ("id", "status_anterior", "status_resultante", "criado_em", "autor"):
        assert re.search(rf"\b{campo}\s*:", projecao), campo
    for proibido in ("alteracoes", "usuarios_id", "email", "lojas_id", "visibilidade", "responsavel", "comentario_interacao_id"):
        assert proibido not in projecao, proibido


def test_historico_rotula_autor_sem_inferir():
    texto = logica(HISTORICO)
    assert '{nome: "Sistema", perfil: null}' in texto
    assert "$evento.usuarios_id == null" in texto
    assert "$evento.autor_id != null && $evento.autor_id != 0" in texto
    for role, rotulo in (("gerente", "Gerente"), ("tecnico", "Técnico"), ("diretoria", "Diretoria"), ("administrador", "Administrador")):
        assert f'$evento.autor_role == "{role}"' in texto
        assert f'value = "{rotulo}"' in texto


@pytest.mark.parametrize(
    "caminho,autorizacao",
    [
        (HISTORICO_GERENTE, "service_desk/obter_chamado_gerente_autorizado"),
        (HISTORICO_SOLICITANTE, "service_desk/obter_chamado_solicitante_autorizado"),
        (DETALHE_SOLICITANTE, "service_desk/obter_chamado_solicitante_autorizado"),
        (COMENTARIOS_SOLICITANTE, "service_desk/obter_chamado_solicitante_autorizado"),
    ],
    ids=lambda v: getattr(v, "stem", v),
)
def test_autorizacao_precede_qualquer_leitura(caminho, autorizacao):
    texto = logica(caminho)
    posicao = texto.index(f'function.run "{autorizacao}"')
    leituras = [m.start() for m in re.finditer(r"\bdb\.(get|query)\b|function\.run \"service_desk/listar_historico_status\"", texto)]
    assert leituras
    assert all(p > posicao for p in leituras)


def test_vinculo_do_solicitante_integra_o_filtro_com_404_uniforme():
    texto = logica(AUTORIZADO_SOLICITANTE)
    autorizacao = texto[texto.index('function.run "autorizacao/exigir_perfil"'):texto.index("} as $usuario")]
    for perfil in ("gerente", "tecnico", "diretoria", "administrador"):
        assert re.search(rf"\b{perfil}\s*: true", autorizacao)
    assert where(texto) == ["$db.chamados.id == $input.chamados_id && $db.chamados.solicitante_id == $usuario.id"]
    assert "lojas_id" not in texto
    assert 'error_type = "accessdenied"' not in texto
    assert texto.count('error_type = "notfound"') == 2
    assert "$registro.solicitante_id != null && $registro.solicitante_id == $usuario.id" in texto


def test_lista_do_solicitante_restrita_ao_vinculo_e_ordenada():
    texto = logica(LISTA_SOLICITANTE)
    assert where(texto) == ["$db.chamados.solicitante_id == $usuario.id"]
    assert 'sort = {chamados.ultima_atualizacao_em: "desc", chamados.id: "desc"}' in texto
    assert "lojas_id" not in texto


def campos_projecao(texto, inicio):
    trecho = texto[texto.index(inicio):]
    trecho = trecho[: trecho.index("\n    }\n")]
    # O XanoScript exportado pelo Xano alinha os campos (`campo   : valor`).
    return re.findall(r"^\s+([a-z_]+)\s*:", trecho, re.MULTILINE)


def test_item_da_lista_do_solicitante_tem_os_campos_do_gerente():
    gerente = campos_projecao(logica(LISTA_GERENTE), "var $items")
    solicitante = campos_projecao(logica(LISTA_SOLICITANTE), "var $items")
    assert solicitante == gerente


def test_detalhe_do_solicitante_tem_os_campos_do_gerente_sem_telemetria_nem_ids():
    gerente = campos_projecao(logica(DETALHE_GERENTE), "var $chamado")
    texto = logica(DETALHE_SOLICITANTE)
    assert set(campos_projecao(texto, "var $chamado")) == set(gerente) - {"sla_horas_aplicado"}
    assert "resumo_totem: null" in texto
    assert "telemetria" not in texto
    assert "value = {nome: $registro.solicitante_nome}" in texto
    assert "value = {nome: $registro.tecnico_nome}" in texto
    assert "id: $registro.solicitante_usuario_id" not in texto
    assert "id: $registro.tecnico_usuario_id" not in texto


def test_r1_nenhum_recurso_xano_referencia_alteracao_status():
    referencias = [p for p in (ROOT / "xano").rglob("*.xs") if "alteracao_status" in fonte(p)]
    assert referencias == []
    enum = fonte(ROOT / "xano/table/interacoes_chamado.xs")
    assert 'values = ["comentario", "atribuicao", "reatribuicao", "liberacao", "alteracao_chamado"]' in enum
    save = logica(FUNCOES / "validar_save_tratativa_chamado.xs")
    assert save.count("db.add interacoes_chamado") == 2


def test_comentarios_do_solicitante_tem_filtro_e_dto_identicos_ao_gerente():
    gerente, solicitante = logica(COMENTARIOS_GERENTE), logica(COMENTARIOS_SOLICITANTE)
    assert where(solicitante) == where(gerente)
    projecao = lambda t: t[t.index("var $items"):]
    assert projecao(solicitante) == projecao(gerente)


def test_referencias_db_usam_tabelas_reais_salvo_joins_duplos_em_usuarios():
    """Mesma regra léxica do Language Server oficial (`dbReferenceScanner`).

    O Language Server trata todo `$db.<nome>` como tabela e não conhece aliases
    de join. O detalhe do solicitante precisa de dois joins em `usuarios`
    (`solicitante` e `tecnico`), que exigem chaves distintas.
    """
    tabelas = {re.search(r"^table (\w+)", fonte(p), re.M).group(1) for p in (ROOT / "xano/table").glob("*.xs")}
    permitidos = {DETALHE_SOLICITANTE: {"solicitante", "tecnico"}}
    for caminho in NOVOS + [FUNCOES / "calcular_consumo_sla_chamado.xs"]:
        nomes = set(re.findall(r"\$db\.(\w+)", fonte(caminho)))
        assert nomes - tabelas <= permitidos.get(caminho, set()), (caminho.name, nomes - tabelas)


def test_detalhe_do_solicitante_usa_loja_historica_como_o_gerente_publicado():
    """Mesma regra publicada do detalhe do Gerente: Loja do Totem no instante do chamado."""
    texto = logica(DETALHE_SOLICITANTE)
    chamada = texto[texto.index('function.run "administracao/resolver_loja_totem_no_instante"'):]
    assert "ativos_referencia_id: $registro.ativo_id" in chamada
    assert "instante            : $registro.criado_em" in chamada
    assert "$db.lojas" not in texto and "$db.ativos_referencia.lojas_id" not in texto
    assert "field_value = $historico.lojas_id" in texto
    assert "loja: $loja" in texto
