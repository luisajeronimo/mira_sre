"""Cliente tipado dos contratos funcionais do Service Desk no Xano."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx

from app.services.xano import (
    TIMEOUT_PADRAO_SEGUNDOS,
    XanoCliente,
    XanoContratoInvalido,
    _ler_timeout,
)


ORIGENS_CHAMADO = frozenset({"manual", "automatico"})
CRIADORES_SISTEMA_CHAMADO = frozenset({"bot_fiscalizacao"})
PRIORIDADES_CHAMADO = ("Baixa", "Média", "Alta", "Urgente")


@dataclass(frozen=True, slots=True)
class AtivoServiceDesk:
    id: int
    nome_ativo: str
    tipo: str
    status_atual: str


@dataclass(frozen=True, slots=True)
class CategoriaServiceDesk:
    id: int
    nome: str
    tipo_itil: str
    descricao: str
    sla_horas: float


@dataclass(frozen=True, slots=True)
class ReferenciaAtivo:
    id: int
    nome_ativo: str


@dataclass(frozen=True, slots=True)
class ReferenciaCategoria:
    id: int
    nome: str


@dataclass(frozen=True, slots=True)
class ReferenciaUsuario:
    id: int
    nome: str


@dataclass(frozen=True, slots=True)
class ChamadoResumo:
    id: int
    titulo: str
    status: str
    prioridade: str
    origem: str | None
    criado_em: int | None
    ativo: ReferenciaAtivo
    categoria: ReferenciaCategoria
    descricao: str | None = None
    sla_horas_aplicado: float | None = None
    atribuido_em: int | None = None
    solicitante: ReferenciaUsuario | None = None
    tecnico: ReferenciaUsuario | None = None


@dataclass(frozen=True, slots=True)
class ChamadoDetalhe:
    id: int
    titulo: str
    descricao: str | None
    status: str
    prioridade: str
    origem: str | None
    criado_em: int | None
    sla_horas_aplicado: float | None
    ativo: ReferenciaAtivo
    categoria: ReferenciaCategoria
    solicitante: ReferenciaUsuario | None
    tecnico: ReferenciaUsuario | None
    atribuido_em: int | None = None
    criador_sistema: str | None = None


def _inteiro(valor: Any, campo: str) -> int:
    if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
        raise XanoContratoInvalido(f"Campo inválido na resposta: {campo}.")
    return valor


def _texto(valor: Any, campo: str) -> str:
    if not isinstance(valor, str) or not valor.strip():
        raise XanoContratoInvalido(f"Campo inválido na resposta: {campo}.")
    return valor


def _texto_opcional(valor: Any, campo: str) -> str | None:
    if valor is None:
        return None
    return _texto(valor, campo)


def _numero(valor: Any, campo: str) -> float:
    if (
        not isinstance(valor, (int, float))
        or isinstance(valor, bool)
    ):
        raise XanoContratoInvalido(f"Campo inválido na resposta: {campo}.")
    return float(valor)


def _numero_opcional(valor: Any, campo: str) -> float | None:
    if valor is None:
        return None
    return _numero(valor, campo)


def _timestamp_opcional(valor: Any, campo: str) -> int | None:
    if valor in (None, 0):
        return None
    return _inteiro(valor, campo)


def _objeto(valor: Any, campo: str) -> dict[str, Any]:
    if not isinstance(valor, dict):
        raise XanoContratoInvalido(f"Campo inválido na resposta: {campo}.")
    return valor


def _colecao(dados: dict[str, Any]) -> list[dict[str, Any]]:
    items = dados.get("items")
    if not isinstance(items, list) or any(
        not isinstance(item, dict) for item in items
    ):
        raise XanoContratoInvalido(
            "O Xano retornou uma coleção inválida."
        )
    return items


def _referencia_ativo(valor: Any) -> ReferenciaAtivo:
    dados = _objeto(valor, "ativo")
    return ReferenciaAtivo(
        id=_inteiro(dados.get("id"), "ativo.id"),
        nome_ativo=_texto(dados.get("nome_ativo"), "ativo.nome_ativo"),
    )


def _referencia_categoria(valor: Any) -> ReferenciaCategoria:
    dados = _objeto(valor, "categoria")
    return ReferenciaCategoria(
        id=_inteiro(dados.get("id"), "categoria.id"),
        nome=_texto(dados.get("nome"), "categoria.nome"),
    )


def _referencia_usuario(
    valor: Any,
    campo: str,
) -> ReferenciaUsuario | None:
    if valor is None:
        return None
    dados = _objeto(valor, campo)
    if dados.get("id") is None and dados.get("nome") is None:
        return None
    return ReferenciaUsuario(
        id=_inteiro(dados.get("id"), f"{campo}.id"),
        nome=_texto(dados.get("nome"), f"{campo}.nome"),
    )


def _origem(valor: Any) -> str | None:
    if valor is None:
        return None
    if valor not in ORIGENS_CHAMADO:
        raise XanoContratoInvalido(
            "Campo inválido na resposta: origem."
        )
    return valor


def _criador_sistema(valor: Any) -> str | None:
    if valor is None:
        return None
    if (
        not isinstance(valor, str)
        or valor not in CRIADORES_SISTEMA_CHAMADO
    ):
        raise XanoContratoInvalido(
            "Campo inválido na resposta: criador_sistema."
        )
    return valor


def _resumo(dados: dict[str, Any]) -> ChamadoResumo:
    return ChamadoResumo(
        id=_inteiro(dados.get("id"), "id"),
        titulo=_texto(dados.get("titulo"), "titulo"),
        status=_texto(dados.get("status"), "status"),
        prioridade=_texto(dados.get("prioridade"), "prioridade"),
        origem=_origem(dados.get("origem")),
        criado_em=_timestamp_opcional(dados.get("criado_em"), "criado_em"),
        ativo=_referencia_ativo(dados.get("ativo")),
        categoria=_referencia_categoria(dados.get("categoria")),
        descricao=_texto_opcional(dados.get("descricao"), "descricao"),
        sla_horas_aplicado=_numero_opcional(
            dados.get("sla_horas_aplicado"),
            "sla_horas_aplicado",
        ),
        atribuido_em=_timestamp_opcional(
            dados.get("atribuido_em"),
            "atribuido_em",
        ),
        solicitante=_referencia_usuario(
            dados.get("solicitante"),
            "solicitante",
        ),
        tecnico=_referencia_usuario(dados.get("tecnico"), "tecnico"),
    )


def _detalhe(dados: dict[str, Any]) -> ChamadoDetalhe:
    return ChamadoDetalhe(
        id=_inteiro(dados.get("id"), "id"),
        titulo=_texto(dados.get("titulo"), "titulo"),
        descricao=_texto_opcional(dados.get("descricao"), "descricao"),
        status=_texto(dados.get("status"), "status"),
        prioridade=_texto(dados.get("prioridade"), "prioridade"),
        origem=_origem(dados.get("origem")),
        criado_em=_timestamp_opcional(dados.get("criado_em"), "criado_em"),
        sla_horas_aplicado=_numero_opcional(
            dados.get("sla_horas_aplicado"),
            "sla_horas_aplicado",
        ),
        ativo=_referencia_ativo(dados.get("ativo")),
        categoria=_referencia_categoria(dados.get("categoria")),
        solicitante=_referencia_usuario(
            dados.get("solicitante"),
            "solicitante",
        ),
        tecnico=_referencia_usuario(dados.get("tecnico"), "tecnico"),
        atribuido_em=_timestamp_opcional(
            dados.get("atribuido_em"),
            "atribuido_em",
        ),
        criador_sistema=_criador_sistema(dados.get("criador_sistema")),
    )


class XanoServiceDeskCliente(XanoCliente):
    """Adaptador dos cinco contratos funcionais do Gerente."""

    def __init__(
        self,
        base_url: str,
        timeout_segundos: float = TIMEOUT_PADRAO_SEGUNDOS,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        super().__init__(
            base_url,
            timeout_segundos,
            transport,
            nome_configuracao="XANO_SERVICE_DESK_BASE_URL",
        )

    async def listar_ativos(self, token: str) -> list[AtivoServiceDesk]:
        dados = await self._requisitar("GET", "/gerente/ativos", token=token)
        return [
            AtivoServiceDesk(
                id=_inteiro(item.get("id"), "id"),
                nome_ativo=_texto(item.get("nome_ativo"), "nome_ativo"),
                tipo=_texto(item.get("tipo"), "tipo"),
                status_atual=_texto(
                    item.get("status_atual"),
                    "status_atual",
                ),
            )
            for item in _colecao(dados)
        ]

    async def listar_categorias(
        self,
        token: str,
    ) -> list[CategoriaServiceDesk]:
        dados = await self._requisitar(
            "GET",
            "/gerente/categorias",
            token=token,
        )
        return [
            CategoriaServiceDesk(
                id=_inteiro(item.get("id"), "id"),
                nome=_texto(item.get("nome"), "nome"),
                tipo_itil=_texto(item.get("tipo_itil"), "tipo_itil"),
                descricao=_texto(item.get("descricao"), "descricao"),
                sla_horas=_numero(item.get("sla_horas"), "sla_horas"),
            )
            for item in _colecao(dados)
        ]

    async def abrir_chamado(
        self,
        token: str,
        *,
        ativos_referencia_id: int,
        categorias_servico_id: int,
        prioridade: str,
        titulo: str,
        descricao: str,
    ) -> ChamadoDetalhe:
        dados = await self._requisitar(
            "POST",
            "/gerente/chamados",
            token=token,
            json={
                "ativos_referencia_id": ativos_referencia_id,
                "categorias_servico_id": categorias_servico_id,
                "prioridade": prioridade,
                "titulo": titulo,
                "descricao": descricao,
            },
        )
        return _detalhe(_objeto(dados.get("chamado"), "chamado"))

    async def listar_chamados(self, token: str) -> list[ChamadoResumo]:
        dados = await self._requisitar(
            "GET",
            "/gerente/chamados",
            token=token,
        )
        return [_resumo(item) for item in _colecao(dados)]

    async def obter_chamado(
        self,
        token: str,
        chamado_id: int,
    ) -> ChamadoDetalhe:
        dados = await self._requisitar(
            "GET",
            f"/gerente/chamados/{chamado_id}",
            token=token,
        )
        return _detalhe(_objeto(dados.get("chamado"), "chamado"))

    async def listar_chamados_tecnico(
        self,
        token: str,
        visao: str,
    ) -> list[ChamadoResumo]:
        dados = await self._requisitar(
            "GET",
            f"/tecnico/chamados?visao={visao}",
            token=token,
        )
        return [_resumo(item) for item in _colecao(dados)]

    async def obter_chamado_tecnico(
        self,
        token: str,
        chamado_id: int,
    ) -> ChamadoDetalhe:
        dados = await self._requisitar(
            "GET",
            f"/tecnico/chamados/{chamado_id}",
            token=token,
        )
        return _detalhe(_objeto(dados.get("chamado"), "chamado"))

    async def assumir_chamado_tecnico(
        self,
        token: str,
        chamado_id: int,
    ) -> ChamadoDetalhe:
        dados = await self._requisitar(
            "POST",
            f"/tecnico/chamados/{chamado_id}/assumir",
            token=token,
            json={},
        )
        return _detalhe(_objeto(dados.get("chamado"), "chamado"))


def criar_cliente_service_desk() -> XanoServiceDeskCliente:
    """Cria o cliente do Service Desk com base exclusiva do ambiente."""

    return XanoServiceDeskCliente(
        base_url=os.getenv("XANO_SERVICE_DESK_BASE_URL", ""),
        timeout_segundos=_ler_timeout(
            os.getenv("XANO_REQUEST_TIMEOUT_SECONDS")
        ),
    )
