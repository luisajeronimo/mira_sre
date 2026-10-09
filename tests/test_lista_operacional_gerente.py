"""Contratos locais da lista operacional do Gerente.

O harness espelha somente as regras determinísticas aprovadas para a consulta
no Xano. Ele não chama rede, não usa credenciais e não substitui a validação do
XanoScript pelo parser/MCP.
"""

from __future__ import annotations

from pathlib import Path
import re

import pytest

from app.chamados.shared import _resumo_para_dict
from app.services.service_desk import ChamadoResumo, ReferenciaAtivo, ReferenciaCategoria


ROOT = Path(__file__).parents[1]
STATUS_CANONICOS = {
    "Novo",
    "Em Atendimento",
    "Aguardando Solicitante",
    "Aguardando Mudança",
    "Resolvido",
    "Solução Rejeitada",
    "Encerrado",
    "Cancelado",
}
REGISTROS = [
    {
        "id": 4,
        "loja_id": 1,
        "ativo_id": 10,
        "titulo": "Zeta",
        "status": "Novo",
        "prioridade": "Urgente",
        "totem": "TOT-Z",
        "categoria": "Rede",
        "criado_em": 400,
        "ultima_atualizacao_em": 900,
    },
    {
        "id": 3,
        "loja_id": 1,
        "ativo_id": 10,
        "titulo": "Alfa",
        "status": "Encerrado",
        "prioridade": "Alta",
        "totem": "TOT-A",
        "categoria": "Energia",
        "criado_em": 400,
        "ultima_atualizacao_em": 800,
    },
    {
        "id": 2,
        "loja_id": 1,
        "ativo_id": 11,
        "titulo": "Beta",
        "status": "Em Atendimento",
        "prioridade": "Média",
        "totem": "TOT-B",
        "categoria": "Falha",
        "criado_em": 200,
        "ultima_atualizacao_em": 600,
    },
    {
        "id": 1,
        "loja_id": 1,
        "ativo_id": 11,
        "titulo": "Gamma",
        "status": "Cancelado",
        "prioridade": "Baixa",
        "totem": "TOT-C",
        "categoria": "Acesso",
        "criado_em": 100,
        "ultima_atualizacao_em": 500,
    },
    {
        "id": 9,
        "loja_id": 2,
        "ativo_id": 20,
        "titulo": "Externo",
        "status": "Novo",
        "prioridade": "Urgente",
        "totem": "TOT-X",
        "categoria": "Rede",
        "criado_em": 999,
        "ultima_atualizacao_em": 999,
    },
]


def consultar(
    registros: list[dict],
    *,
    loja_id: int = 1,
    numero: int | None = None,
    status: str | None = None,
    ativo_id: int | None = None,
    data_inicio: int | None = None,
    data_fim: int | None = None,
    ordenar_por: str | None = None,
    direcao: str | None = None,
) -> tuple[list[dict], int]:
    """Modelo local do contrato whitelistado da função Xano."""

    # A fronteira Xano aceita inputs textuais opcionais. O cliente pode omiti-los,
    # enviá-los como null ou serializá-los como string vazia; os três casos têm a
    # semântica do default aprovado antes da validação da whitelist.
    ordenar_por = "criado_em" if ordenar_por in {None, ""} else ordenar_por
    direcao = "DESC" if direcao in {None, ""} else direcao

    campos = {
        "numero",
        "titulo",
        "status",
        "prioridade",
        "totem",
        "categoria",
        "criado_em",
        "ultima_atualizacao_em",
    }
    # A fronteira pública textual preserva ausência distinta de zero explícito.
    if numero is not None and numero <= 0:
        raise ValueError("número inválido")
    status = None if status in {None, ""} else status
    if status is not None and status not in STATUS_CANONICOS:
        raise ValueError("status inválido")
    if ativo_id is not None and ativo_id <= 0:
        raise ValueError("Totem inválido")
    if ordenar_por not in campos or direcao not in {"ASC", "DESC"}:
        raise ValueError("ordenação inválida")
    if data_inicio is not None and data_fim is not None and data_inicio >= data_fim:
        raise ValueError("período inválido")

    todos_ativos = {item["ativo_id"]: item["loja_id"] for item in registros}
    if ativo_id is not None and todos_ativos.get(ativo_id) != loja_id:
        raise PermissionError("Totem fora da Loja")

    itens = [item for item in registros if item["loja_id"] == loja_id]
    if numero is not None:
        itens = [item for item in itens if item["id"] == numero]
    if status is not None:
        itens = [item for item in itens if item["status"] == status]
    if ativo_id is not None:
        itens = [item for item in itens if item["ativo_id"] == ativo_id]
    if data_inicio is not None:
        itens = [item for item in itens if item["criado_em"] >= data_inicio]
    if data_fim is not None:
        itens = [item for item in itens if item["criado_em"] < data_fim]
    total = len(itens)

    if ordenar_por == "numero":
        chave = lambda item: item["id"]
    elif ordenar_por in {"criado_em", "ultima_atualizacao_em"}:
        chave = lambda item: item[ordenar_por]
    else:
        chave = lambda item: item[ordenar_por].casefold()

    itens.sort(key=lambda item: (chave(item), item["id"]), reverse=direcao == "DESC")
    return itens, total


def test_escopo_filtros_combinados_e_total_filtrado():
    itens, total = consultar(
        REGISTROS,
        status="Novo",
        ativo_id=10,
        data_inicio=300,
        data_fim=500,
    )

    assert [item["id"] for item in itens] == [4]
    assert total == 1


def test_numero_e_status_invalidos_nao_criam_consulta_livre():
    with pytest.raises(ValueError):
        consultar(REGISTROS, numero=0)
    with pytest.raises(ValueError):
        consultar(REGISTROS, ativo_id=0)
    with pytest.raises(ValueError):
        consultar(REGISTROS, status="Qualquer")
    with pytest.raises(ValueError):
        consultar(REGISTROS, ordenar_por="created_at")
    with pytest.raises(ValueError):
        consultar(REGISTROS, direcao="RAND")


def test_filtros_numericos_omissos_zero_e_positivos_tem_semanticas_distintas():
    controle = [
        {
            "id": 34,
            "loja_id": 1,
            "ativo_id": 2,
            "titulo": "Controle",
            "status": "Novo",
            "prioridade": "Alta",
            "totem": "Totem 02",
            "categoria": "Categoria",
            "criado_em": 1_780_000_000_000,
            "ultima_atualizacao_em": 1_780_000_000_000,
        },
        {
            "id": 35,
            "loja_id": 1,
            "ativo_id": 3,
            "titulo": "Outro",
            "status": "Novo",
            "prioridade": "Média",
            "totem": "Totem 03",
            "categoria": "Categoria",
            "criado_em": 1_780_000_001_000,
            "ultima_atualizacao_em": 1_780_000_001_000,
        },
    ]

    todos, total_todos = consultar(controle)
    por_numero, total_numero = consultar(controle, numero=34)
    por_ativo, total_ativo = consultar(controle, ativo_id=2)

    assert [item["id"] for item in todos] == [35, 34]
    assert total_todos == 2
    assert [item["id"] for item in por_numero] == [34]
    assert total_numero == 1
    assert [item["id"] for item in por_ativo] == [34]
    assert total_ativo == 1
    with pytest.raises(ValueError, match="número"):
        consultar(controle, numero=0)
    with pytest.raises(ValueError, match="Totem"):
        consultar(controle, ativo_id=0)


def test_controle_equivalente_ao_chamado_34_permanece_selecionavel():
    controle = [
        {
            "id": 34,
            "loja_id": 1,
            "ativo_id": 2,
            "titulo": "Controle",
            "status": "Novo",
            "prioridade": "Alta",
            "totem": "Totem 02",
            "categoria": "Categoria",
            "criado_em": 1_780_000_000_000,
            "ultima_atualizacao_em": 1_780_000_000_000,
        }
    ]

    for filtros in (
        {},
        {"numero": 34},
        {"numero": 34, "status": "Novo"},
        {"numero": 34, "status": "Novo", "ativo_id": 2},
        {
            "numero": 34,
            "status": "Novo",
            "ativo_id": 2,
            "data_inicio": 1_700_000_000_000,
            "data_fim": 1_800_000_000_000,
        },
    ):
        itens, total = consultar(controle, **filtros)
        assert [item["id"] for item in itens] == [34]
        assert total == 1


def test_totem_de_outra_loja_e_negado_sem_ampliar_escopo():
    with pytest.raises(PermissionError):
        consultar(REGISTROS, ativo_id=20)


def test_default_e_datas_funcionais_usam_ordem_cronologica_com_desempate():
    itens, _ = consultar(REGISTROS)
    assert [item["id"] for item in itens] == [4, 3, 2, 1]

    asc, _ = consultar(REGISTROS, ordenar_por="criado_em", direcao="ASC")
    desc, _ = consultar(REGISTROS, ordenar_por="criado_em", direcao="DESC")
    assert [item["id"] for item in asc] == [1, 2, 3, 4]
    assert [item["id"] for item in desc] == [4, 3, 2, 1]


def test_ordenar_por_ausente_usa_default_aprovado():
    itens, _ = consultar(REGISTROS, direcao="DESC")
    assert [item["id"] for item in itens] == [4, 3, 2, 1]


def test_ordenar_por_null_usa_default_aprovado():
    itens, _ = consultar(REGISTROS, ordenar_por=None, direcao="DESC")
    assert [item["id"] for item in itens] == [4, 3, 2, 1]


def test_ordenar_por_vazio_usa_default_aprovado():
    itens, _ = consultar(REGISTROS, ordenar_por="", direcao="DESC")
    assert [item["id"] for item in itens] == [4, 3, 2, 1]


def test_direcao_ausente_usa_default_aprovado():
    itens, _ = consultar(REGISTROS, ordenar_por="criado_em")
    assert [item["id"] for item in itens] == [4, 3, 2, 1]


def test_direcao_null_usa_default_aprovado():
    itens, _ = consultar(REGISTROS, ordenar_por="criado_em", direcao=None)
    assert [item["id"] for item in itens] == [4, 3, 2, 1]


def test_direcao_vazia_usa_default_aprovado():
    itens, _ = consultar(REGISTROS, ordenar_por="criado_em", direcao="")
    assert [item["id"] for item in itens] == [4, 3, 2, 1]


def test_ambos_criterios_ausentes_usam_default_aprovado():
    itens, _ = consultar(REGISTROS)
    assert [item["id"] for item in itens] == [4, 3, 2, 1]


@pytest.mark.parametrize(
    ("ordenar_por", "direcao"),
    [
        ("", ""),
        (None, None),
    ],
)
def test_ambos_criterios_ausentes_ou_vazios_usam_default_aprovado(ordenar_por, direcao):
    itens, _ = consultar(REGISTROS, ordenar_por=ordenar_por, direcao=direcao)
    assert [item["id"] for item in itens] == [4, 3, 2, 1]


def test_xanoscript_normaliza_vazios_antes_da_whitelist_de_ordenacao():
    fonte = (ROOT / "xano/function/service_desk/listar_chamados_gerente.xs").read_text()

    normalizacao_ordenar = '$ordenar_por == null || $ordenar_por == ""'
    normalizacao_direcao = '$direcao == null || $direcao == ""'
    whitelist = 'var $ordenacao_valida {'

    assert normalizacao_ordenar in fonte
    assert normalizacao_direcao in fonte
    assert fonte.index(normalizacao_ordenar) < fonte.index(whitelist)
    assert fonte.index(normalizacao_direcao) < fonte.index(whitelist)


def test_ultima_atualizacao_tem_ordem_cronologica_com_desempate():
    asc, _ = consultar(REGISTROS, ordenar_por="ultima_atualizacao_em", direcao="ASC")
    desc, _ = consultar(REGISTROS, ordenar_por="ultima_atualizacao_em", direcao="DESC")
    assert [item["id"] for item in asc] == [1, 2, 3, 4]
    assert [item["id"] for item in desc] == [4, 3, 2, 1]


def test_ordenacoes_textuais_status_e_prioridade_sao_alfabeticas():
    status_asc, _ = consultar(REGISTROS, ordenar_por="status", direcao="ASC")
    prioridade_asc, _ = consultar(REGISTROS, ordenar_por="prioridade", direcao="ASC")
    prioridade_desc, _ = consultar(REGISTROS, ordenar_por="prioridade", direcao="DESC")

    assert [item["status"] for item in status_asc] == [
        "Cancelado",
        "Em Atendimento",
        "Encerrado",
        "Novo",
    ]
    assert [item["prioridade"] for item in prioridade_asc] == [
        "Alta",
        "Baixa",
        "Média",
        "Urgente",
    ]
    assert [item["prioridade"] for item in prioridade_desc] == [
        "Urgente",
        "Média",
        "Baixa",
        "Alta",
    ]


@pytest.mark.parametrize(
    ("campo", "asc", "desc"),
    [
        ("titulo", ["abacate", "Banana", "casa"], ["casa", "Banana", "abacate"]),
        ("status", ["aberto", "Bloqueado", "novo"], ["novo", "Bloqueado", "aberto"]),
        ("prioridade", ["Alta", "baixa", "URGENTE"], ["URGENTE", "baixa", "Alta"]),
        ("totem", ["alpha", "Beta", "zulu"], ["zulu", "Beta", "alpha"]),
        ("categoria", ["acesso", "Banco", "rede"], ["rede", "Banco", "acesso"]),
    ],
)
def test_ordenacoes_textuais_ignoram_maiusculas_e_minusculas(campo, asc, desc):
    registros = [
        {
            "id": indice,
            "loja_id": 1,
            "ativo_id": indice,
            "titulo": "abacate" if indice == 1 else "Banana" if indice == 2 else "casa",
            "status": "aberto" if indice == 1 else "Bloqueado" if indice == 2 else "novo",
            "prioridade": "Alta" if indice == 1 else "baixa" if indice == 2 else "URGENTE",
            "totem": "alpha" if indice == 1 else "Beta" if indice == 2 else "zulu",
            "categoria": "acesso" if indice == 1 else "Banco" if indice == 2 else "rede",
            "criado_em": indice,
            "ultima_atualizacao_em": indice,
        }
        for indice in range(1, 4)
    ]

    asc_itens, _ = consultar(registros, ordenar_por=campo, direcao="ASC")
    desc_itens, _ = consultar(registros, ordenar_por=campo, direcao="DESC")

    assert [item[campo] for item in asc_itens] == asc
    assert [item[campo] for item in desc_itens] == desc


def test_periodo_semiaberto_preserva_semantica_inclusiva_da_interface():
    itens, total = consultar(REGISTROS, data_inicio=200, data_fim=401)
    assert [item["id"] for item in itens] == [4, 3, 2]
    assert total == 3

    with pytest.raises(ValueError):
        consultar(REGISTROS, data_inicio=401, data_fim=200)


@pytest.mark.parametrize(
    ("descricao", "ocorrencia"),
    [
        ("x" * 80, "x" * 80),
        ("x" * 81, "x" * 80 + "…"),
        (None, "Não informado"),
    ],
)
def test_ocorrencia_e_apenas_apresentacao_local(descricao, ocorrencia):
    resumo = ChamadoResumo(
        id=1,
        titulo="Título",
        descricao=descricao,
        status="Novo",
        prioridade="Alta",
        origem="manual",
        criado_em=1_780_000_000_000,
        ultima_atualizacao_em=1_780_000_000_000,
        ativo=ReferenciaAtivo(id=1, nome_ativo="Totem"),
        categoria=ReferenciaCategoria(id=1, nome="Categoria"),
    )

    visual = _resumo_para_dict(resumo)
    assert visual["ocorrencia"] == ocorrencia
    assert visual["descricao"] == (descricao or "")
    assert visual["criado_em_texto"] != "Não informado"
    assert visual["ultima_atualizacao_em_texto"] != "Não informado"


def test_xanoscript_mantem_filtros_e_ordenacao_dentro_da_funcao_da_loja():
    fonte = (ROOT / "xano/function/service_desk/listar_chamados_gerente.xs").read_text()
    endpoint = (ROOT / "xano/api/mira_service_desk/gerente/chamados_GET.xs").read_text()

    predicado_loja = "$db.ativo.lojas_id == $usuario.lojas_id"
    consultas = re.findall(
        r"db\.query chamados \{(.*?)\n        \} as \$[A-Za-z_][A-Za-z0-9_]*",
        fonte,
        re.DOTALL,
    )

    assert consultas
    assert "$filtros" not in fonte
    assert "where = $filtros == true" not in fonte
    assert "$db.$db" not in fonte
    for consulta in consultas:
        assert f"where = {predicado_loja}" in consulta

    assert "$db.ativo.lojas_id == $usuario.lojas_id" in fonte
    assert 'sort = {status_ordenavel: "asc", chamados.id: "asc"}' in fonte
    assert "total: ($items|count)" in fonte
    assert "timestamp data_inicio?" in endpoint
    assert "timestamp data_fim?" in endpoint
    assert "text numero? filters=trim" in endpoint
    assert "text ativo_id? filters=trim" in endpoint
    assert "text numero? filters=trim" in fonte
    assert "text ativo_id? filters=trim" in fonte
    assert "($input.numero|to_int)" in fonte
    assert "($input.ativo_id|to_int)" in fonte
    assert "($numero_convertido|to_text) == $input.numero" in fonte
    assert "($ativo_convertido|to_text) == $input.ativo_id" in fonte
    assert "where = $db.ativo.lojas_id == $usuario.lojas_id && ($input.numero" not in fonte
    assert "where = $db.ativo.lojas_id == $usuario.lojas_id && ($db.chamados.id ==? $numero_normalizado)" in fonte
    assert "where = $db.ativo.lojas_id == $usuario.lojas_id && (!$aplicar_numero" not in fonte


def test_xanoscript_nao_usa_eval_booleano_para_ordenacao_composta():
    fonte = (ROOT / "xano/function/service_desk/listar_chamados_gerente.xs").read_text()

    # O runtime remoto materializava essas expressões como nomes de coluna
    # inválidos. A proteção estrutural impede a reintrodução desse padrão.
    assert "criado_em_nulo:" not in fonte
    assert "ultima_atualizacao_em_nula:" not in fonte
    assert "prioridade_eh_" not in fonte
    assert '$db.chamados.criado_em == null|as(' not in fonte
    assert '$db.chamados.ultima_atualizacao_em == null|as(' not in fonte
    assert "$db.$db" not in fonte

    # Projeções de join são permitidas; condições booleanas em eval não são.
    # Isso detecta a reintrodução do padrão que o parser aceitou, mas o runtime
    # remoto materializou como um nome de coluna inválido.
    for bloco_eval in re.findall(r"eval = \{(.*?)\n          \}", fonte, re.DOTALL):
        assert "==" not in bloco_eval
        assert "!=" not in bloco_eval

    # Timestamps funcionais são obrigatórios: cada ramo temporal é consulta
    # direta, sem partição ou merge exclusivo de null.
    assert "$resultado_com_data" not in fonte
    assert "$resultado_sem_data" not in fonte
    assert "$db.chamados.criado_em != null" not in fonte
    assert "$db.chamados.criado_em == null" not in fonte
    assert "$db.chamados.ultima_atualizacao_em != null" not in fonte
    assert "$db.chamados.ultima_atualizacao_em == null" not in fonte
    assert len(re.findall(r"db\.query chamados \{", fonte)) == 17
    assert "|merge:" not in fonte
    assert 'prioridade == "Baixa"' not in fonte
    assert 'prioridade == "Média"' not in fonte
    assert 'prioridade == "Alta"' not in fonte
    assert 'prioridade == "Urgente"' not in fonte

    for campo in (
        "titulo_ordenavel",
        "status_ordenavel",
        "prioridade_ordenavel",
        "totem_ordenavel",
        "categoria_ordenavel",
    ):
        assert f"{campo}:" in fonte
        assert f"sort = {{{campo}: \"asc\"" in fonte
        assert f"sort = {{{campo}: \"desc\"" in fonte
