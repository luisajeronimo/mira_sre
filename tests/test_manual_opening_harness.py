"""Harness local do contrato de abertura manual.

O harness modela apenas as decisões já implementadas no Xano. Ele não chama
rede, não usa credenciais e não persiste dados fora da memória do teste.
"""

from dataclasses import dataclass, field

import pytest


PRIORIDADES = ("Baixa", "Média", "Alta", "Urgente")


class ErroContrato(Exception):
    def __init__(self, status: int, mensagem: str):
        super().__init__(mensagem)
        self.status = status


@dataclass(frozen=True)
class Usuario:
    id: int
    role: str
    loja_id: int | None


@dataclass(frozen=True)
class Ativo:
    id: int
    loja_id: int
    nome: str


@dataclass(frozen=True)
class Categoria:
    id: int
    nome: str
    permite_abertura_manual: bool
    sla_horas: float | None


@dataclass
class BancoFalso:
    chamados: list[dict] = field(default_factory=list)

    def add(self, chamado: dict) -> dict:
        registro = {"id": len(self.chamados) + 1, **chamado}
        self.chamados.append(registro)
        return registro


def abrir_chamado_isolado(
    banco: BancoFalso,
    usuario: Usuario,
    ativo: Ativo | None,
    categoria: Categoria | None,
    *,
    prioridade: str | None,
    titulo: str | None,
    descricao: str | None,
    criado_em: int = 1_700_000_000_000,
    **campos_extras,
) -> tuple[int, dict]:
    """Reproduz as validações/derivações do contrato, sem rede."""

    if usuario.role != "gerente" or usuario.loja_id is None:
        raise ErroContrato(403, "Acesso não autorizado.")
    if ativo is None:
        raise ErroContrato(404, "Recurso não encontrado.")
    if ativo.loja_id != usuario.loja_id:
        raise ErroContrato(403, "Acesso não autorizado.")
    if categoria is None:
        raise ErroContrato(404, "Recurso não encontrado.")
    if not categoria.permite_abertura_manual or categoria.sla_horas is None:
        raise ErroContrato(422, "Entrada inválida.")
    if prioridade not in PRIORIDADES:
        raise ErroContrato(422, "Entrada inválida.")
    if titulo is None or not titulo.strip():
        raise ErroContrato(422, "Entrada inválida.")
    if descricao is None or not descricao.strip():
        raise ErroContrato(422, "Entrada inválida.")

    # Campos de autoridade não vêm do cliente, inclusive se foram enviados
    # como extras. A gravação ocorre somente depois de todas as validações.
    registro = banco.add(
        {
            "titulo": titulo.strip(),
            "descricao": descricao.strip(),
            "status": "Novo",
            "prioridade": prioridade,
            "origem": "manual",
            "criado_em": criado_em,
            "sla_horas_aplicado": categoria.sla_horas,
            "solicitante_id": usuario.id,
            "tecnico_id": None,
            "categorias_servico_id": categoria.id,
            "ativos_referencia_id": ativo.id,
        }
    )
    dto = {
        "id": registro["id"],
        "titulo": registro["titulo"],
        "descricao": registro["descricao"],
        "status": registro["status"],
        "prioridade": registro["prioridade"],
        "origem": registro["origem"],
        "criado_em": registro["criado_em"],
        "sla_horas_aplicado": registro["sla_horas_aplicado"],
        "ativo": {"id": ativo.id, "nome_ativo": ativo.nome},
        "categoria": {"id": categoria.id, "nome": categoria.nome},
        "solicitante": {"id": usuario.id, "nome": "Gerente"},
        "tecnico": None,
    }
    return 201, dto


USUARIO = Usuario(id=8, role="gerente", loja_id=1)
ATIVO_PROPRIO = Ativo(id=1, loja_id=1, nome="TOT-PAU-001")
ATIVO_EXTERNO = Ativo(id=8, loja_id=2, nome="TOT-VMA-002")
CATEGORIA_PERMITIDA = Categoria(2, "Falha de Rede", True, 2)
CATEGORIA_BLOQUEADA = Categoria(8, "Alta Temperatura", False, 2)
CATEGORIA_SEM_SLA = Categoria(2, "Falha de Rede", True, None)


@pytest.mark.parametrize("prioridade", PRIORIDADES)
def test_quatro_prioridades_criam_chamado_novo(prioridade):
    banco = BancoFalso()

    status, dto = abrir_chamado_isolado(
        banco,
        USUARIO,
        ATIVO_PROPRIO,
        CATEGORIA_PERMITIDA,
        prioridade=prioridade,
        titulo="T",
        descricao="D",
    )

    assert status == 201
    assert dto["prioridade"] == prioridade
    assert dto["status"] == "Novo"
    assert dto["origem"] == "manual"


@pytest.mark.parametrize("campo", ["titulo", "descricao"])
@pytest.mark.parametrize("valor", [None, "", "   "])
def test_titulo_e_descricao_obrigatorios_sem_limite_minimo(campo, valor):
    dados = {"titulo": "T", "descricao": "D"}
    dados[campo] = valor

    with pytest.raises(ErroContrato) as erro:
        abrir_chamado_isolado(
            BancoFalso(),
            USUARIO,
            ATIVO_PROPRIO,
            CATEGORIA_PERMITIDA,
            prioridade="Alta",
            **dados,
        )

    assert erro.value.status == 422


def test_textos_de_um_caractere_e_longos_nao_sofrem_limite_artificial():
    titulo = "T"
    descricao = "D" * 4096

    status, dto = abrir_chamado_isolado(
        BancoFalso(),
        USUARIO,
        ATIVO_PROPRIO,
        CATEGORIA_PERMITIDA,
        prioridade="Alta",
        titulo=titulo,
        descricao=descricao,
    )

    assert status == 201
    assert dto["titulo"] == titulo
    assert dto["descricao"] == descricao


@pytest.mark.parametrize(
    ("ativo", "categoria", "status"),
    [
        (ATIVO_PROPRIO, CATEGORIA_PERMITIDA, 201),
        (ATIVO_EXTERNO, CATEGORIA_PERMITIDA, 403),
        (ATIVO_PROPRIO, None, 404),
        (ATIVO_PROPRIO, CATEGORIA_BLOQUEADA, 422),
        (ATIVO_PROPRIO, CATEGORIA_SEM_SLA, 422),
    ],
)
def test_ativo_e_categoria_respeitam_escopo_e_classificacao(ativo, categoria, status):
    banco = BancoFalso()

    try:
        resultado, _ = abrir_chamado_isolado(
            banco,
            USUARIO,
            ativo,
            categoria,
            prioridade="Alta",
            titulo="T",
            descricao="D",
        )
    except ErroContrato as erro:
        resultado = erro.status

    assert resultado == status
    assert len(banco.chamados) == (1 if status == 201 else 0)


def test_derivacoes_autoritativas_campos_extras_dto_e_timestamp():
    banco = BancoFalso()

    status, dto = abrir_chamado_isolado(
        banco,
        USUARIO,
        ATIVO_PROPRIO,
        CATEGORIA_PERMITIDA,
        prioridade="Alta",
        titulo=" T ",
        descricao=" D ",
        criado_em=123,
        solicitante_id=999,
        status="Resolvido",
        origem="automatico",
        sla_horas_aplicado=999,
        loja_id=999,
    )

    assert status == 201
    assert dto["solicitante"]["id"] == USUARIO.id
    assert dto["status"] == "Novo"
    assert dto["origem"] == "manual"
    assert dto["criado_em"] == 123
    assert dto["sla_horas_aplicado"] == CATEGORIA_PERMITIDA.sla_horas
    assert dto["ativo"]["id"] == ATIVO_PROPRIO.id
    assert dto["categoria"]["id"] == CATEGORIA_PERMITIDA.id
    assert dto["tecnico"] is None
    assert "created_at" not in dto
    assert "token" not in dto
    assert "loja_id" not in dto


def test_duas_submissoes_equivalentes_sao_independentes():
    banco = BancoFalso()
    argumentos = dict(
        usuario=USUARIO,
        ativo=ATIVO_PROPRIO,
        categoria=CATEGORIA_PERMITIDA,
        prioridade="Alta",
        titulo="T",
        descricao="D",
    )

    primeiro, _ = abrir_chamado_isolado(banco, **argumentos)
    segundo, _ = abrir_chamado_isolado(banco, **argumentos)

    assert (primeiro, segundo) == (201, 201)
    assert [item["id"] for item in banco.chamados] == [1, 2]


@pytest.mark.parametrize("campo", ["prioridade", "titulo", "descricao"])
def test_falha_de_validacao_nao_faz_criacao_parcial(campo):
    banco = BancoFalso()
    dados = {"prioridade": "Alta", "titulo": "T", "descricao": "D"}
    dados[campo] = "Crítica" if campo == "prioridade" else "   "

    with pytest.raises(ErroContrato):
        abrir_chamado_isolado(
            banco,
            USUARIO,
            ATIVO_PROPRIO,
            CATEGORIA_PERMITIDA,
            **dados,
        )

    assert banco.chamados == []
