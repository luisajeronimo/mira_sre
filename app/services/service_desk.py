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
TIPOS_EVENTO_TIMELINE = frozenset(
    {"comentario", "atribuicao", "reatribuicao", "liberacao"}
)


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
class ReferenciaLoja:
    id: int
    nome: str


@dataclass(frozen=True, slots=True)
class AutorComentarioPublico:
    nome: str


@dataclass(frozen=True, slots=True)
class ComentarioPublico:
    id: int
    conteudo: str
    criado_em: int
    autor: AutorComentarioPublico | None


@dataclass(frozen=True, slots=True)
class ChamadoResumo:
    id: int
    titulo: str
    status: str | None
    prioridade: str
    origem: str | None
    criado_em: int
    ultima_atualizacao_em: int
    ativo: ReferenciaAtivo
    categoria: ReferenciaCategoria
    descricao: str | None = None
    sla_horas_aplicado: float | None = None
    atribuido_em: int | None = None
    solicitante: ReferenciaUsuario | None = None
    tecnico: ReferenciaUsuario | None = None


@dataclass(frozen=True, slots=True)
class ListaChamadosGerente:
    """Resposta estruturada da consulta operacional, ainda sem paginação."""

    items: list[ChamadoResumo]
    total: int


@dataclass(frozen=True, slots=True)
class ChamadoDetalhe:
    id: int
    titulo: str
    descricao: str | None
    status: str | None
    prioridade: str
    origem: str | None
    criado_em: int
    ultima_atualizacao_em: int
    sla_horas_aplicado: float | None
    ativo: ReferenciaAtivo
    categoria: ReferenciaCategoria
    solicitante: ReferenciaUsuario | None
    tecnico: ReferenciaUsuario | None
    atribuido_em: int | None = None
    criador_sistema: str | None = None
    loja: ReferenciaLoja | None = None


@dataclass(frozen=True, slots=True)
class EventoTimelineChamado:
    id: int
    tipo: str
    conteudo: str | None
    visibilidade: str
    criado_em: int
    autor: ReferenciaUsuario | None
    tecnico_anterior: ReferenciaUsuario | None
    tecnico_novo: ReferenciaUsuario | None


@dataclass(frozen=True, slots=True)
class DetalheChamadoTecnico:
    chamado: ChamadoDetalhe
    timeline: list[EventoTimelineChamado]
    tecnicos: list[ReferenciaUsuario]


def _inteiro(valor: Any, campo: str) -> int:
    if not isinstance(valor, int) or isinstance(valor, bool) or valor <= 0:
        raise XanoContratoInvalido(f"Campo inválido na resposta: {campo}.")
    return valor


def _contagem(valor: Any, campo: str) -> int:
    if not isinstance(valor, int) or isinstance(valor, bool) or valor < 0:
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


def _objeto_exato(valor: Any, campo: str, campos: set[str]) -> dict[str, Any]:
    dados = _objeto(valor, campo)
    if set(dados) != campos:
        raise XanoContratoInvalido(f"Campo inválido na resposta: {campo}.")
    return dados


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


def _referencia_loja(valor: Any) -> ReferenciaLoja | None:
    if valor is None:
        return None
    dados = _objeto(valor, "loja")
    if dados.get("id") is None and dados.get("nome") is None:
        return None
    return ReferenciaLoja(
        id=_inteiro(dados.get("id"), "loja.id"),
        nome=_texto(dados.get("nome"), "loja.nome"),
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


def _resumo(
    dados: dict[str, Any],
    *,
    permitir_status_nulo: bool = False,
) -> ChamadoResumo:
    return ChamadoResumo(
        id=_inteiro(dados.get("id"), "id"),
        titulo=_texto(dados.get("titulo"), "titulo"),
        status=(
            _texto_opcional(dados.get("status"), "status")
            if permitir_status_nulo
            else _texto(dados.get("status"), "status")
        ),
        prioridade=_texto(dados.get("prioridade"), "prioridade"),
        origem=_origem(dados.get("origem")),
        criado_em=_inteiro(dados.get("criado_em"), "criado_em"),
        ultima_atualizacao_em=_inteiro(
            dados.get("ultima_atualizacao_em"),
            "ultima_atualizacao_em",
        ),
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


def _resumo_gerente(dados: dict[str, Any]) -> ChamadoResumo:
    return _resumo(dados)


def _lista_chamados_gerente(dados: dict[str, Any]) -> ListaChamadosGerente:
    """Valida o envelope estruturado, ainda sem paginação, da lista do Gerente."""

    if set(dados) != {"items", "total"}:
        raise XanoContratoInvalido(
            "O Xano retornou uma lista de chamados incompatível."
        )

    items = _colecao(dados)
    for item in items:
        if "descricao" not in item or "ultima_atualizacao_em" not in item:
            raise XanoContratoInvalido(
                "O Xano retornou um resumo de chamado incompatível."
            )

    total = _contagem(dados.get("total"), "total")
    # Nesta change não há paginação: todo item correspondente à consulta vem
    # na resposta. Uma divergência indica contrato remoto incompatível, em vez
    # de uma página parcial que o Reflex poderia interpretar incorretamente.
    if total != len(items):
        raise XanoContratoInvalido(
            "O Xano retornou um total de chamados incompatível."
        )
    return ListaChamadosGerente(
        items=[_resumo_gerente(item) for item in items],
        total=total,
    )


def _detalhe(
    dados: dict[str, Any],
    *,
    permitir_status_nulo: bool = False,
) -> ChamadoDetalhe:
    return ChamadoDetalhe(
        id=_inteiro(dados.get("id"), "id"),
        titulo=_texto(dados.get("titulo"), "titulo"),
        descricao=_texto_opcional(dados.get("descricao"), "descricao"),
        status=(
            _texto_opcional(dados.get("status"), "status")
            if permitir_status_nulo
            else _texto(dados.get("status"), "status")
        ),
        prioridade=_texto(dados.get("prioridade"), "prioridade"),
        origem=_origem(dados.get("origem")),
        criado_em=_inteiro(dados.get("criado_em"), "criado_em"),
        ultima_atualizacao_em=_inteiro(
            dados.get("ultima_atualizacao_em"),
            "ultima_atualizacao_em",
        ),
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
        loja=_referencia_loja(dados.get("loja")),
    )


def _evento_timeline(dados: Any) -> EventoTimelineChamado:
    evento = _objeto(dados, "timeline")
    tipo = _texto(evento.get("tipo"), "timeline.tipo")
    if tipo not in TIPOS_EVENTO_TIMELINE:
        raise XanoContratoInvalido(
            "Campo inválido na resposta: timeline.tipo."
        )
    conteudo = evento.get("conteudo")
    # Eventos operacionais não carregam mensagem. O Xano os representa como
    # texto vazio, enquanto comentários legados podem usar null.
    conteudo_normalizado = (
        None
        if conteudo is None
        or (conteudo == "" and tipo in {"atribuicao", "reatribuicao", "liberacao"})
        else _texto(conteudo, "timeline.conteudo")
    )
    return EventoTimelineChamado(
        id=_inteiro(evento.get("id"), "timeline.id"),
        tipo=tipo,
        conteudo=conteudo_normalizado,
        visibilidade=_texto(evento.get("visibilidade"), "timeline.visibilidade"),
        criado_em=_inteiro(evento.get("criado_em"), "timeline.criado_em"),
        autor=_referencia_usuario(evento.get("autor"), "timeline.autor"),
        tecnico_anterior=_referencia_usuario(
            evento.get("tecnico_anterior"),
            "timeline.tecnico_anterior",
        ),
        tecnico_novo=_referencia_usuario(
            evento.get("tecnico_novo"),
            "timeline.tecnico_novo",
        ),
    )


def _detalhe_tecnico(dados: dict[str, Any]) -> DetalheChamadoTecnico:
    timeline = dados.get("timeline")
    tecnicos = dados.get("tecnicos")
    if not isinstance(timeline, list) or not isinstance(tecnicos, list):
        raise XanoContratoInvalido(
            "O Xano retornou um detalhe técnico incompatível."
        )
    tecnicos_validos: list[ReferenciaUsuario] = []
    for tecnico in tecnicos:
        referencia = _referencia_usuario(tecnico, "tecnicos")
        if referencia is None:
            raise XanoContratoInvalido(
                "O Xano retornou um Técnico inválido no detalhe."
            )
        tecnicos_validos.append(referencia)
    return DetalheChamadoTecnico(
        chamado=_detalhe(
            _objeto(dados.get("chamado"), "chamado"),
            permitir_status_nulo=True,
        ),
        timeline=[_evento_timeline(evento) for evento in timeline],
        tecnicos=tecnicos_validos,
    )


def _detalhe_gerente(dados: dict[str, Any]) -> ChamadoDetalhe:
    return _detalhe(dados)


def _comentario_publico(dados: Any) -> ComentarioPublico:
    comentario = _objeto_exato(
        dados,
        "comentario",
        {"id", "conteudo", "criado_em", "autor"},
    )
    autor_valor = comentario["autor"]
    autor = None
    if autor_valor is not None:
        autor_dados = _objeto_exato(autor_valor, "comentario.autor", {"nome"})
        autor = AutorComentarioPublico(nome=_texto(autor_dados["nome"], "comentario.autor.nome"))
    return ComentarioPublico(
        id=_inteiro(comentario["id"], "comentario.id"),
        conteudo=_texto(comentario["conteudo"], "comentario.conteudo"),
        criado_em=_inteiro(comentario["criado_em"], "comentario.criado_em"),
        autor=autor,
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

    async def listar_ativos_monitoramento(
        self, token: str
    ) -> list[AtivoServiceDesk]:
        dados = await self._requisitar(
            "GET",
            "/ativos_referencia",
            token=token,
        )
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

    async def listar_ativos_tecnico(
        self, token: str
    ) -> list[AtivoServiceDesk]:
        dados = await self._requisitar(
            "GET",
            "/tecnico/ativos",
            token=token,
        )
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
        return _detalhe_gerente(_objeto(dados.get("chamado"), "chamado"))

    async def listar_chamados(
        self,
        token: str,
        *,
        numero: int | None = None,
        status: str | None = None,
        ativo_id: int | None = None,
        data_inicio: int | None = None,
        data_fim: int | None = None,
        ordenar_por: str = "criado_em",
        direcao: str = "DESC",
    ) -> ListaChamadosGerente:
        params: dict[str, str | int] = {
            "ordenar_por": ordenar_por,
            "direcao": direcao,
        }
        for campo, valor in (
            ("numero", numero),
            ("status", status),
            ("ativo_id", ativo_id),
            ("data_inicio", data_inicio),
            ("data_fim", data_fim),
        ):
            if valor is not None and valor != "":
                params[campo] = valor
        dados = await self._requisitar(
            "GET",
            "/gerente/chamados",
            token=token,
            params=params,
        )
        return _lista_chamados_gerente(dados)

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
        return _detalhe_gerente(_objeto(dados.get("chamado"), "chamado"))

    async def listar_comentarios_publicos(
        self,
        token: str,
        chamado_id: int,
    ) -> list[ComentarioPublico]:
        dados = await self._requisitar(
            "GET",
            f"/gerente/chamados/{chamado_id}/comentarios",
            token=token,
        )
        return [_comentario_publico(item) for item in _colecao(dados)]

    async def criar_comentario_publico(
        self,
        token: str,
        chamado_id: int,
        *,
        conteudo: str,
    ) -> ComentarioPublico:
        dados = await self._requisitar(
            "POST",
            f"/gerente/chamados/{chamado_id}/comentarios",
            token=token,
            json={"conteudo": conteudo},
        )
        return _comentario_publico(dados.get("comentario"))

    async def listar_chamados_tecnico(
        self,
        token: str,
        *,
        numero: int | None = None,
        status: str | None = None,
        ativo_id: int | None = None,
        data_inicio: int | None = None,
        data_fim: int | None = None,
        somente_atribuidos_a_mim: bool = False,
    ) -> ListaChamadosGerente:
        """Lista global com o mesmo envelope e filtros da lista do Gerente."""

        params: dict[str, str | int] = {}
        for campo, valor in (
            ("numero", numero),
            ("status", status),
            ("ativo_id", ativo_id),
            ("data_inicio", data_inicio),
            ("data_fim", data_fim),
        ):
            if valor is not None and valor != "":
                params[campo] = valor
        if somente_atribuidos_a_mim:
            params["somente_atribuidos_a_mim"] = True
        dados = await self._requisitar(
            "GET",
            "/tecnico/chamados",
            token=token,
            params=params,
        )
        return _lista_chamados_gerente(dados)

    async def obter_chamado_tecnico(
        self,
        token: str,
        chamado_id: int,
    ) -> DetalheChamadoTecnico:
        dados = await self._requisitar(
            "GET",
            f"/tecnico/chamados/{chamado_id}",
            token=token,
        )
        return _detalhe_tecnico(dados)

    async def alterar_responsavel_tecnico(
        self,
        token: str,
        chamado_id: int,
        acao: str,
        tecnico_id: int | None = None,
    ) -> ChamadoDetalhe:
        payload: dict[str, Any] = {"acao": acao}
        if acao == "atribuir" and tecnico_id is not None:
            payload["tecnico_id"] = tecnico_id
        dados = await self._requisitar(
            "POST",
            f"/tecnico/chamados/{chamado_id}/assumir",
            token=token,
            json=payload,
        )
        return _detalhe(_objeto(dados.get("chamado"), "chamado"))

    async def assumir_chamado_tecnico(
        self,
        token: str,
        chamado_id: int,
    ) -> ChamadoDetalhe:
        return await self.alterar_responsavel_tecnico(
            token,
            chamado_id,
            "assumir",
        )


def criar_cliente_service_desk() -> XanoServiceDeskCliente:
    """Cria o cliente do Service Desk com base exclusiva do ambiente."""

    return XanoServiceDeskCliente(
        base_url=os.getenv("XANO_SERVICE_DESK_BASE_URL", ""),
        timeout_segundos=_ler_timeout(
            os.getenv("XANO_REQUEST_TIMEOUT_SECONDS")
        ),
    )
