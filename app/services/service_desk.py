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
    {
        "comentario",
        "atribuicao",
        "reatribuicao",
        "liberacao",
        "alteracao_chamado",
    }
)


@dataclass(frozen=True, slots=True)
class AtivoServiceDesk:
    id: int
    nome_ativo: str
    tipo: str
    status_atual: str


@dataclass(frozen=True, slots=True)
class AtivoMonitoramento:
    """Resumo operacional persistido de um Totem."""

    id: int
    nome_ativo: str
    tipo: str
    loja: ReferenciaLoja | None
    status_atual: str
    ultima_telemetria_em: int | None
    ultima_transicao_disponibilidade_em: int | None


@dataclass(frozen=True, slots=True)
class TelemetriaMonitoramento:
    id: int
    evento_timestamp: int
    uso_cpu: float
    uso_memoria: float
    temperatura: float
    status_rede: str


@dataclass(frozen=True, slots=True)
class TransicaoDisponibilidade:
    id: int
    status: str
    detectado_em: int
    heartbeat_limite_minutos: int


@dataclass(frozen=True, slots=True)
class IncidenteAutomaticoHeartbeat:
    id: int
    titulo: str
    status: str
    prioridade: str
    criado_em: int
    ultima_atualizacao_em: int
    categoria: ReferenciaCategoria


@dataclass(frozen=True, slots=True)
class DetalheMonitoramento:
    totem: AtivoMonitoramento
    ultima_telemetria: TelemetriaMonitoramento | None
    telemetrias: list[TelemetriaMonitoramento]
    transicoes_disponibilidade: list[TransicaoDisponibilidade]
    incidentes_automaticos: list[IncidenteAutomaticoHeartbeat]


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
    criador_sistema: str | None = None


@dataclass(frozen=True, slots=True)
class ListaChamadosGerente:
    """Resposta estruturada da consulta operacional, ainda sem paginação."""

    items: list[ChamadoResumo]
    total: int


@dataclass(frozen=True, slots=True)
class PreferenciaFilaTecnica:
    """Filtro e ordenação confirmados para um usuário e escopo da fila."""

    escopo: str
    numero: int | None
    status: str | None
    ativo_id: int | None
    data_inicio: int | None
    data_fim: int | None
    prioridade: str | None
    ordenar_por: str
    direcao: str
    responsavel_id: int | None = None
    somente_nao_atribuido: bool = False


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
    alteracoes: dict[str, Any] | None = None


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


def _ativo_monitoramento(dados: Any, campo: str = "totem") -> AtivoMonitoramento:
    ativo = _objeto(dados, campo)
    return AtivoMonitoramento(
        id=_inteiro(ativo.get("id"), f"{campo}.id"),
        nome_ativo=_texto(ativo.get("nome_ativo"), f"{campo}.nome_ativo"),
        tipo=_texto(ativo.get("tipo"), f"{campo}.tipo"),
        loja=_referencia_loja(ativo.get("loja")),
        status_atual=_texto(ativo.get("status_atual"), f"{campo}.status_atual"),
        ultima_telemetria_em=_timestamp_opcional(
            ativo.get("ultima_telemetria_em"),
            f"{campo}.ultima_telemetria_em",
        ),
        ultima_transicao_disponibilidade_em=_timestamp_opcional(
            ativo.get("ultima_transicao_disponibilidade_em"),
            f"{campo}.ultima_transicao_disponibilidade_em",
        ),
    )


def _telemetria_monitoramento(dados: Any, campo: str = "telemetria") -> TelemetriaMonitoramento:
    telemetria = _objeto(dados, campo)
    return TelemetriaMonitoramento(
        id=_inteiro(telemetria.get("id"), f"{campo}.id"),
        evento_timestamp=_inteiro(
            telemetria.get("evento_timestamp"),
            f"{campo}.evento_timestamp",
        ),
        uso_cpu=_numero(telemetria.get("uso_cpu"), f"{campo}.uso_cpu"),
        uso_memoria=_numero(
            telemetria.get("uso_memoria"),
            f"{campo}.uso_memoria",
        ),
        temperatura=_numero(
            telemetria.get("temperatura"), f"{campo}.temperatura"),
        status_rede=_texto(telemetria.get("status_rede"), f"{campo}.status_rede"),
    )


def _transicao_disponibilidade(dados: Any) -> TransicaoDisponibilidade:
    transicao = _objeto(dados, "transicao_disponibilidade")
    status = _texto(transicao.get("status"), "transicao_disponibilidade.status")
    if status not in {"online", "offline"}:
        raise XanoContratoInvalido(
            "Campo inválido na resposta: transicao_disponibilidade.status."
        )
    return TransicaoDisponibilidade(
        id=_inteiro(transicao.get("id"), "transicao_disponibilidade.id"),
        status=status,
        detectado_em=_inteiro(
            transicao.get("detectado_em"),
            "transicao_disponibilidade.detectado_em",
        ),
        heartbeat_limite_minutos=_inteiro(
            transicao.get("heartbeat_limite_minutos"),
            "transicao_disponibilidade.heartbeat_limite_minutos",
        ),
    )


def _incidente_automatico_heartbeat(dados: Any) -> IncidenteAutomaticoHeartbeat:
    incidente = _objeto(dados, "incidente_automatico")
    return IncidenteAutomaticoHeartbeat(
        id=_inteiro(incidente.get("id"), "incidente_automatico.id"),
        titulo=_texto(incidente.get("titulo"), "incidente_automatico.titulo"),
        status=_texto(incidente.get("status"), "incidente_automatico.status"),
        prioridade=_texto(
            incidente.get("prioridade"), "incidente_automatico.prioridade"
        ),
        criado_em=_inteiro(incidente.get("criado_em"), "incidente_automatico.criado_em"),
        ultima_atualizacao_em=_inteiro(
            incidente.get("ultima_atualizacao_em"),
            "incidente_automatico.ultima_atualizacao_em",
        ),
        categoria=_referencia_categoria(incidente.get("categoria")),
    )


def _detalhe_monitoramento(dados: dict[str, Any]) -> DetalheMonitoramento:
    campos = {
        "totem",
        "ultima_telemetria",
        "telemetrias",
        "transicoes_disponibilidade",
        "incidentes_automaticos",
    }
    dados = _objeto_exato(dados, "detalhe_monitoramento", campos)
    telemetrias = dados["telemetrias"]
    transicoes = dados["transicoes_disponibilidade"]
    incidentes = dados["incidentes_automaticos"]
    if not all(isinstance(colecao, list) for colecao in (telemetrias, transicoes, incidentes)):
        raise XanoContratoInvalido(
            "O Xano retornou históricos de monitoramento incompatíveis."
        )
    if any(len(colecao) > 10 for colecao in (telemetrias, transicoes, incidentes)):
        raise XanoContratoInvalido(
            "O Xano retornou mais registros de monitoramento que o limite aprovado."
        )
    ultima = dados["ultima_telemetria"]
    return DetalheMonitoramento(
        totem=_ativo_monitoramento(dados["totem"]),
        ultima_telemetria=(
            _telemetria_monitoramento(ultima, "ultima_telemetria")
            if ultima is not None
            else None
        ),
        telemetrias=[_telemetria_monitoramento(item) for item in telemetrias],
        transicoes_disponibilidade=[
            _transicao_disponibilidade(item) for item in transicoes
        ],
        incidentes_automaticos=[
            _incidente_automatico_heartbeat(item) for item in incidentes
        ],
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
        criador_sistema=_criador_sistema(dados.get("criador_sistema")),
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


def _preferencia_fila_tecnica(dados: dict[str, Any]) -> PreferenciaFilaTecnica:
    """Valida a preferência já normalizada pelo contrato autenticado do Xano."""

    campos = {
        "escopo", "numero", "status", "ativo_id", "data_inicio", "data_fim",
        "prioridade", "responsavel_id", "somente_nao_atribuido", "ordenar_por", "direcao",
    }
    dados = _objeto_exato(dados, "preferencia", campos)
    escopo = dados.get("escopo")
    ordenar_por = dados.get("ordenar_por")
    direcao = dados.get("direcao")
    if escopo not in {"todos", "atribuidos_a_mim"}:
        raise XanoContratoInvalido("Campo inválido na resposta: preferencia.escopo.")
    if ordenar_por not in {
        "numero", "titulo", "status", "prioridade", "totem", "categoria", "aberto_por", "responsavel",
        "criado_em", "ultima_atualizacao_em",
    } or direcao not in {"ASC", "DESC"}:
        raise XanoContratoInvalido("Campo inválido na resposta: preferencia.ordenacao.")
    return PreferenciaFilaTecnica(
        escopo=escopo,
        numero=_inteiro(dados["numero"], "preferencia.numero") if dados["numero"] is not None else None,
        status=_texto(dados["status"], "preferencia.status") if dados["status"] is not None else None,
        ativo_id=_inteiro(dados["ativo_id"], "preferencia.ativo_id") if dados["ativo_id"] is not None else None,
        data_inicio=_inteiro(dados["data_inicio"], "preferencia.data_inicio") if dados["data_inicio"] is not None else None,
        data_fim=_inteiro(dados["data_fim"], "preferencia.data_fim") if dados["data_fim"] is not None else None,
        prioridade=_texto(dados["prioridade"], "preferencia.prioridade") if dados["prioridade"] is not None else None,
        responsavel_id=_inteiro(dados["responsavel_id"], "preferencia.responsavel_id") if dados["responsavel_id"] is not None else None,
        somente_nao_atribuido=dados["somente_nao_atribuido"] is True,
        ordenar_por=ordenar_por,
        direcao=direcao,
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
        or (
            conteudo == ""
            and tipo
            in {
                "atribuicao",
                "reatribuicao",
                "liberacao",
                "alteracao_chamado",
            }
        )
        else _texto(conteudo, "timeline.conteudo")
    )
    alteracoes = evento.get("alteracoes")
    if alteracoes is not None and not isinstance(alteracoes, dict):
        raise XanoContratoInvalido(
            "Campo inválido na resposta: timeline.alteracoes."
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
        alteracoes=alteracoes,
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
    """Adaptador tipado dos contratos funcionais do Service Desk."""

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
    ) -> list[AtivoMonitoramento]:
        dados = await self._requisitar(
            "GET",
            "/monitoramento/ativos",
            token=token,
        )
        return [
            _ativo_monitoramento(item, "item")
            for item in _colecao(dados)
        ]

    async def obter_detalhe_ativo_monitoramento(
        self,
        token: str,
        ativos_referencia_id: int,
    ) -> DetalheMonitoramento:
        dados = await self._requisitar(
            "GET",
            f"/monitoramento/ativos/{ativos_referencia_id}",
            token=token,
        )
        return _detalhe_monitoramento(dados)

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

    async def listar_categorias_tratativa(
        self,
        token: str,
    ) -> list[CategoriaServiceDesk]:
        """Lista somente categorias ativas disponíveis para nova seleção.

        A Categoria persistida no chamado é lida do detalhe canônico e pode
        ser inativa. Este catálogo não decide regras de abertura manual.
        """

        dados = await self._requisitar(
            "GET",
            "/tecnico/categorias",
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
            erro_400_como_entrada=True,
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
        prioridade: str | None = None,
        responsavel_id: int | None = None,
        ordenar_por: str = "numero",
        direcao: str = "DESC",
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
            ("prioridade", prioridade),
            ("responsavel_id", responsavel_id),
        ):
            if valor is not None and valor != "":
                params[campo] = valor
        if somente_atribuidos_a_mim:
            params["somente_atribuidos_a_mim"] = True
        # O contrato possui o mesmo padrão inicial; omiti-lo preserva URLs
        # concisas sem deixar o frontend decidir a ordenação no servidor.
        if ordenar_por != "numero":
            params["ordenar_por"] = ordenar_por
        if direcao != "DESC":
            params["direcao"] = direcao
        dados = await self._requisitar(
            "GET",
            "/tecnico/chamados",
            token=token,
            params=params,
        )
        return _lista_chamados_gerente(dados)

    async def obter_preferencia_fila_tecnica(
        self, token: str, *, escopo: str
    ) -> PreferenciaFilaTecnica:
        dados = await self._requisitar(
            "GET", "/tecnico/preferencias-fila", token=token,
            params={"escopo": escopo},
        )
        return _preferencia_fila_tecnica(dados.get("preferencia"))

    async def salvar_preferencia_fila_tecnica(
        self,
        token: str,
        *,
        escopo: str,
        numero: int | None,
        status: str | None,
        ativo_id: int | None,
        data_inicio: int | None,
        data_fim: int | None,
        prioridade: str | None,
        responsavel_id: int | None,
        somente_nao_atribuido: bool,
        ordenar_por: str,
        direcao: str,
    ) -> PreferenciaFilaTecnica:
        dados = await self._requisitar(
            "PUT", "/tecnico/preferencias-fila", token=token,
            json={
                "escopo": escopo, "numero": numero, "status": status,
                "ativo_id": ativo_id, "data_inicio": data_inicio,
                "data_fim": data_fim, "prioridade": prioridade,
                "responsavel_id": responsavel_id,
                "somente_nao_atribuido": somente_nao_atribuido,
                "ordenar_por": ordenar_por, "direcao": direcao,
            },
            erro_400_como_entrada=True,
        )
        return _preferencia_fila_tecnica(dados.get("preferencia"))

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

    async def salvar_tratativa_chamado(
        self,
        token: str,
        chamado_id: int,
        *,
        tecnico_id: int | None,
        status: str,
        prioridade: str,
        categorias_servico_id: int,
        ultima_atualizacao_em: int,
        comentario_status: str | None = None,
        visibilidade_comentario_status: str | None = None,
    ) -> DetalheChamadoTecnico:
        """Envia o rascunho completo ao único Save transacional do Xano.

        O cliente mantém ``tecnico_id: null`` explícito para representar a
        liberação. Validações de status, perfil, Categoria, comentário e
        versão pertencem exclusivamente ao contrato Xano.
        """

        payload: dict[str, Any] = {
            "tecnico_id": tecnico_id,
            "status": status,
            "prioridade": prioridade,
            "categorias_servico_id": categorias_servico_id,
            "ultima_atualizacao_em": ultima_atualizacao_em,
        }
        if comentario_status is not None:
            payload["comentario_status"] = comentario_status
        if visibilidade_comentario_status is not None:
            payload["visibilidade_comentario_status"] = (
                visibilidade_comentario_status
            )
        dados = await self._requisitar(
            "POST",
            f"/tecnico/chamados/{chamado_id}/tratativa",
            token=token,
            json=payload,
            erro_400_como_entrada=True,
        )
        return _detalhe_tecnico(dados)

    async def criar_comentario_operacional(
        self,
        token: str,
        chamado_id: int,
        *,
        conteudo: str,
        visibilidade: str,
    ) -> DetalheChamadoTecnico:
        """Cria comentário independente e devolve o detalhe pós-operação."""

        dados = await self._requisitar(
            "POST",
            f"/tecnico/chamados/{chamado_id}/comentarios",
            token=token,
            json={"conteudo": conteudo, "visibilidade": visibilidade},
            erro_400_como_entrada=True,
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
