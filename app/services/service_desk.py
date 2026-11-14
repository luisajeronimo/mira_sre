"""Cliente tipado dos contratos funcionais do Service Desk no Xano."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

import httpx

from app.indicadores.contrato import (
    CatalogoIndicadores,
    ResultadoConfiabilidade,
    ler_catalogo,
    ler_resultado,
)
from app.indicadores.contrato_causas import (
    CatalogoCausas, ResultadoCausas, ler_catalogo_causas, ler_resultado_causas,
)
from app.indicadores.contrato_operacao import (
    CatalogoOperacao,
    ResultadoOperacao,
    ler_catalogo_operacao,
    ler_resultado_operacao,
)
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
    status_atual: str | None
    loja: ReferenciaLoja | None = None


@dataclass(frozen=True, slots=True)
class AtivoMonitoramento:
    """Resumo operacional persistido de um Totem."""

    id: int
    nome_ativo: str
    tipo: str
    loja: ReferenciaLoja | None
    status_atual: str | None
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
    loja: ReferenciaLoja | None = None


@dataclass(frozen=True, slots=True)
class TransicaoDisponibilidade:
    id: int
    status: str
    detectado_em: int
    heartbeat_limite_minutos: int
    loja: ReferenciaLoja | None = None


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
    loja: ReferenciaLoja | None = None


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
    status: list[str]
    ativo_ids: list[int]
    data_inicio: int | None
    data_fim: int | None
    prioridades: list[str]
    ordenar_por: str
    direcao: str
    responsavel_ids: list[int] = field(default_factory=list)
    incluir_nao_atribuido: bool = False
    ultima_atualizacao_inicio: int | None = None
    ultima_atualizacao_fim: int | None = None
    loja_ids: list[int] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class PreferenciaFiltrosGerente:
    numero: int | None
    status: list[str]
    ativo_ids: list[int]
    data_inicio: int | None
    data_fim: int | None
    ultima_atualizacao_inicio: int | None
    ultima_atualizacao_fim: int | None


@dataclass(frozen=True, slots=True)
class ResumoTotemGerente:
    id: int
    nome_ativo: str
    loja: ReferenciaLoja
    status_atual: str | None
    ultima_telemetria: TelemetriaMonitoramento | None


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
    resumo_totem: ResumoTotemGerente | None = None


@dataclass(frozen=True, slots=True)
class EventoTimelineChamado:
    id: int
    tipo: str
    conteudo: str | None
    visibilidade: str | None
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


@dataclass(frozen=True, slots=True)
class HistoricoStatusItem:
    id: int
    status_anterior: str
    status_resultante: str
    criado_em: int
    autor: AutorHistoricoStatus | None


@dataclass(frozen=True, slots=True)
class AutorHistoricoStatus:
    nome: str
    perfil: str | None


@dataclass(frozen=True, slots=True)
class ReferenciaUsuarioPublico:
    nome: str


@dataclass(frozen=True, slots=True)
class ChamadoDetalheSolicitante(ChamadoDetalhe):
    solicitante: ReferenciaUsuarioPublico | None
    tecnico: ReferenciaUsuarioPublico | None
    resumo_totem: None = None


@dataclass(frozen=True, slots=True)
class ConsumoSLADTO:
    chamados_id: int
    calculavel: bool
    motivo: str | None
    consumo_ms: int | None
    sla_horas_aplicado: float | None
    fracao_consumida: float | None
    faixa: str | None
    estado_contagem: str | None
    calculado_em: int


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


def _estado_totem_opcional(valor: Any, campo: str) -> str | None:
    # O Xano Free retorna texto vazio quando o Totem ainda não tem estado
    # materializado. Isso não equivale a Online nem a Offline.
    if valor is None or valor == "":
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
        status_atual=_estado_totem_opcional(ativo.get("status_atual"), f"{campo}.status_atual"),
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
        loja=_referencia_loja(telemetria.get("loja")),
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
        loja=_referencia_loja(transicao.get("loja")),
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
        loja=_referencia_loja(dados.get("loja")),
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


def _lista_preferencia(valor: Any, campo: str, *, ids: bool = False) -> list:
    if not isinstance(valor, list):
        raise XanoContratoInvalido(f"Campo inválido na resposta: preferencia.{campo}.")
    resultado = []
    for item in valor:
        if ids:
            if isinstance(item, bool) or not isinstance(item, int) or item <= 0:
                raise XanoContratoInvalido(f"Campo inválido na resposta: preferencia.{campo}.")
        elif not isinstance(item, str) or not item:
            raise XanoContratoInvalido(f"Campo inválido na resposta: preferencia.{campo}.")
        elif campo == "status" and item not in {"Novo", "Em Atendimento", "Aguardando Solicitante", "Aguardando Mudança", "Resolvido", "Solução Rejeitada", "Encerrado", "Cancelado"}:
            raise XanoContratoInvalido("Campo inválido na resposta: preferencia.status.")
        elif campo == "prioridades" and item not in PRIORIDADES_CHAMADO:
            raise XanoContratoInvalido("Campo inválido na resposta: preferencia.prioridades.")
        if item not in resultado:
            resultado.append(item)
    return resultado


def _normalizar_preferencia_legada(dados: dict[str, Any], *, global_: bool) -> dict[str, Any]:
    # A forma legada somente é reconhecida por seus nomes escalares. Um objeto
    # canônico malformado jamais deve fazer fallback para esses campos.
    dados = dict(dados)
    if "ativo_id" not in dados:
        return dados
    if "ativo_ids" in dados:
        raise XanoContratoInvalido("Campo inválido na resposta: preferencia.")
    def lista(valor):
        return [] if valor is None or valor == "" else [valor]
    dados["status"] = lista(dados.get("status"))
    dados["ativo_ids"] = lista(dados.pop("ativo_id"))
    if global_:
        dados.setdefault("ultima_atualizacao_inicio", None)
        dados.setdefault("ultima_atualizacao_fim", None)
        dados["loja_ids"] = lista(dados.pop("loja_id", None))
        dados["prioridades"] = lista(dados.pop("prioridade", None))
        dados["responsavel_ids"] = lista(dados.pop("responsavel_id", None))
        dados["incluir_nao_atribuido"] = dados.pop("somente_nao_atribuido", False)
    return dados


def _preferencia_fila_tecnica(dados: dict[str, Any]) -> PreferenciaFilaTecnica:
    dados = _normalizar_preferencia_legada(_objeto(dados, "preferencia"), global_=True)
    campos = {"escopo", "numero", "status", "ativo_ids", "data_inicio", "data_fim", "ultima_atualizacao_inicio", "ultima_atualizacao_fim", "loja_ids", "prioridades", "responsavel_ids", "incluir_nao_atribuido", "ordenar_por", "direcao"}
    dados = _objeto_exato(dados, "preferencia", campos)
    if not isinstance(dados["escopo"], str) or not isinstance(dados["ordenar_por"], str) or not isinstance(dados["direcao"], str) or dados["escopo"] not in {"todos", "atribuidos_a_mim"} or dados["ordenar_por"] not in {"numero", "titulo", "status", "prioridade", "totem", "loja", "categoria", "aberto_por", "responsavel", "criado_em", "ultima_atualizacao_em"} or dados["direcao"] not in {"ASC", "DESC"} or not isinstance(dados["incluir_nao_atribuido"], bool):
        raise XanoContratoInvalido("Campo inválido na resposta: preferencia.")
    def inteiro_opcional(nome):
        return _inteiro(dados[nome], f"preferencia.{nome}") if dados[nome] is not None else None
    return PreferenciaFilaTecnica(
        escopo=dados["escopo"], numero=inteiro_opcional("numero"),
        status=_lista_preferencia(dados["status"], "status"),
        ativo_ids=_lista_preferencia(dados["ativo_ids"], "ativo_ids", ids=True),
        data_inicio=inteiro_opcional("data_inicio"), data_fim=inteiro_opcional("data_fim"),
        ultima_atualizacao_inicio=inteiro_opcional("ultima_atualizacao_inicio"), ultima_atualizacao_fim=inteiro_opcional("ultima_atualizacao_fim"),
        loja_ids=_lista_preferencia(dados["loja_ids"], "loja_ids", ids=True),
        prioridades=_lista_preferencia(dados["prioridades"], "prioridades"),
        responsavel_ids=_lista_preferencia(dados["responsavel_ids"], "responsavel_ids", ids=True),
        incluir_nao_atribuido=dados["incluir_nao_atribuido"], ordenar_por=dados["ordenar_por"], direcao=dados["direcao"],
    )


def _preferencia_filtros_gerente(dados: dict[str, Any]) -> PreferenciaFiltrosGerente:
    dados = _normalizar_preferencia_legada(_objeto(dados, "preferencia"), global_=False)
    dados = _objeto_exato(dados, "preferencia", {"numero", "status", "ativo_ids", "data_inicio", "data_fim", "ultima_atualizacao_inicio", "ultima_atualizacao_fim"})
    def inteiro_opcional(nome):
        return _inteiro(dados[nome], f"preferencia.{nome}") if dados[nome] is not None else None
    return PreferenciaFiltrosGerente(
        numero=inteiro_opcional("numero"), status=_lista_preferencia(dados["status"], "status"),
        ativo_ids=_lista_preferencia(dados["ativo_ids"], "ativo_ids", ids=True),
        data_inicio=inteiro_opcional("data_inicio"), data_fim=inteiro_opcional("data_fim"),
        ultima_atualizacao_inicio=inteiro_opcional("ultima_atualizacao_inicio"), ultima_atualizacao_fim=inteiro_opcional("ultima_atualizacao_fim"),
    )


def _resumo_totem_gerente(valor: Any) -> ResumoTotemGerente | None:
    if valor is None:
        return None
    dados = _objeto_exato(
        valor,
        "resumo_totem",
        {"id", "nome_ativo", "loja", "status_atual", "ultima_telemetria"},
    )
    loja = _referencia_loja(dados["loja"])
    if loja is None:
        raise XanoContratoInvalido("Campo inválido na resposta: resumo_totem.loja.")
    return ResumoTotemGerente(
        id=_inteiro(dados["id"], "resumo_totem.id"),
        nome_ativo=_texto(dados["nome_ativo"], "resumo_totem.nome_ativo"),
        loja=loja,
        status_atual=_estado_totem_opcional(dados["status_atual"], "resumo_totem.status_atual"),
        ultima_telemetria=(
            _telemetria_monitoramento(dados["ultima_telemetria"], "resumo_totem.ultima_telemetria")
            if dados["ultima_telemetria"] is not None else None
        ),
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
        resumo_totem=_resumo_totem_gerente(dados.get("resumo_totem")),
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
    visibilidade = evento.get("visibilidade")
    if tipo == "comentario":
        if not isinstance(visibilidade, str) or visibilidade not in {"publica", "interna"}:
            raise XanoContratoInvalido("Campo inválido na resposta: timeline.visibilidade.")
    else:
        visibilidade = None
    return EventoTimelineChamado(
        id=_inteiro(evento.get("id"), "timeline.id"),
        tipo=tipo,
        conteudo=conteudo_normalizado,
        visibilidade=visibilidade,
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


def _referencia_usuario_publico(valor: Any, campo: str) -> ReferenciaUsuarioPublico | None:
    if valor is None:
        return None
    dados = _objeto_exato(valor, campo, {"nome"})
    return ReferenciaUsuarioPublico(nome=_texto(dados["nome"], f"{campo}.nome"))


def _detalhe_solicitante(dados: dict[str, Any]) -> ChamadoDetalheSolicitante:
    campos = {"id", "titulo", "descricao", "status", "prioridade", "origem",
              "criador_sistema", "criado_em", "ultima_atualizacao_em",
              "ativo", "categoria", "solicitante",
              "tecnico", "loja", "resumo_totem"}
    dados = _objeto_exato(dados, "chamado", campos)
    if dados["resumo_totem"] is not None:
        raise XanoContratoInvalido("O detalhe do solicitante contém telemetria.")
    return ChamadoDetalheSolicitante(
        id=_inteiro(dados["id"], "chamado.id"),
        titulo=_texto(dados["titulo"], "chamado.titulo"),
        descricao=_texto_opcional(dados["descricao"], "chamado.descricao"),
        status=_texto(dados["status"], "chamado.status"),
        prioridade=_texto(dados["prioridade"], "chamado.prioridade"),
        origem=_origem(dados["origem"]),
        criado_em=_inteiro(dados["criado_em"], "chamado.criado_em"),
        ultima_atualizacao_em=_inteiro(dados["ultima_atualizacao_em"], "chamado.ultima_atualizacao_em"),
        sla_horas_aplicado=None,
        ativo=_referencia_ativo(dados["ativo"]),
        categoria=_referencia_categoria(dados["categoria"]),
        solicitante=_referencia_usuario_publico(dados["solicitante"], "chamado.solicitante"),
        tecnico=_referencia_usuario_publico(dados["tecnico"], "chamado.tecnico"),
        criador_sistema=_criador_sistema(dados["criador_sistema"]),
        loja=_referencia_loja(dados["loja"]),
    )


def _historico_status(dados: dict[str, Any]) -> list[HistoricoStatusItem]:
    if set(dados) != {"items"} or not isinstance(dados["items"], list):
        raise XanoContratoInvalido("O histórico de status é incompatível.")
    resultado = []
    for valor in dados["items"]:
        item = _objeto_exato(valor, "historico", {"id", "status_anterior", "status_resultante", "criado_em", "autor"})
        anterior = _texto(item["status_anterior"], "historico.status_anterior")
        resultante = _texto(item["status_resultante"], "historico.status_resultante")
        if anterior == resultante:
            raise XanoContratoInvalido("O histórico contém transição inválida.")
        autor = None
        if item["autor"] is not None:
            dados_autor = _objeto_exato(item["autor"], "historico.autor", {"nome", "perfil"})
            perfil = dados_autor["perfil"]
            if perfil is not None and perfil not in {"Gerente", "Técnico", "Diretoria", "Administrador"}:
                raise XanoContratoInvalido("O histórico contém perfil inválido.")
            autor = AutorHistoricoStatus(_texto(dados_autor["nome"], "historico.autor.nome"), perfil)
        resultado.append(HistoricoStatusItem(
            _inteiro(item["id"], "historico.id"), anterior, resultante,
            _inteiro(item["criado_em"], "historico.criado_em"), autor,
        ))
    return resultado


def _consumo_sla(dados: dict[str, Any]) -> ConsumoSLADTO:
    consumo = _objeto_exato(dados.get("consumo_sla"), "consumo_sla", {
        "chamados_id", "calculavel", "motivo", "consumo_ms", "sla_horas_aplicado",
        "fracao_consumida", "faixa", "estado_contagem", "calculado_em",
    })
    if not isinstance(consumo["calculavel"], bool):
        raise XanoContratoInvalido("O consumo de SLA é incompatível.")
    calculavel = consumo["calculavel"]
    motivo = _texto_opcional(consumo["motivo"], "consumo_sla.motivo")
    consumo_ms = _contagem(consumo["consumo_ms"], "consumo_sla.consumo_ms") if calculavel else None
    fracao = _numero(consumo["fracao_consumida"], "consumo_sla.fracao_consumida") if calculavel else None
    faixa = consumo["faixa"]
    estado = consumo["estado_contagem"]
    if (calculavel and (motivo is not None or faixa not in {"normal", "risco", "critico", "violado"}
                       or estado not in {"em_contagem", "pausada", "encerrada"} or fracao < 0)
        or not calculavel and (motivo is None or any(consumo[c] is not None for c in ("consumo_ms", "fracao_consumida", "faixa", "estado_contagem")))):
        raise XanoContratoInvalido("O consumo de SLA é incompatível.")
    return ConsumoSLADTO(
        chamados_id=_inteiro(consumo["chamados_id"], "consumo_sla.chamados_id"),
        calculavel=calculavel, motivo=motivo, consumo_ms=consumo_ms,
        sla_horas_aplicado=_numero_opcional(consumo["sla_horas_aplicado"], "consumo_sla.sla_horas_aplicado"),
        fracao_consumida=fracao, faixa=faixa, estado_contagem=estado,
        calculado_em=_inteiro(consumo["calculado_em"], "consumo_sla.calculado_em"),
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

    async def catalogo_indicadores_disponibilidade(self, token: str) -> CatalogoIndicadores:
        dados = await self._requisitar(
            "GET", "/indicadores/disponibilidade-confiabilidade/filtros", token=token
        )
        return ler_catalogo(dados)

    async def consultar_indicadores_disponibilidade(
        self,
        token: str,
        *,
        t0: int,
        t1: int,
        lojas_id: int | None = None,
        ativos_referencia_id: int | None = None,
        visao: str | None = None,
    ) -> ResultadoConfiabilidade:
        params: dict[str, int | str] = {"t0": t0, "t1": t1}
        if visao is not None:
            params["visao"] = visao
        if lojas_id is not None:
            params["lojas_id"] = lojas_id
        if ativos_referencia_id is not None:
            params["ativos_referencia_id"] = ativos_referencia_id
        dados = await self._requisitar(
            "GET", "/indicadores/disponibilidade-confiabilidade", token=token, params=params
        )
        return ler_resultado(dados, visao=visao)

    async def catalogo_indicadores_operacao(self, token: str) -> CatalogoOperacao:
        dados = await self._requisitar("GET", "/indicadores/operacao-sla/filtros", token=token)
        return ler_catalogo_operacao(dados)

    async def consultar_indicadores_operacao(
        self,
        token: str,
        *,
        t0: int,
        t1: int,
        lojas_id: int | None = None,
        categorias_servico_id: int | None = None,
        visao: str | None = None,
    ) -> ResultadoOperacao:
        params: dict[str, int | str] = {"t0": t0, "t1": t1}
        if lojas_id is not None:
            params["lojas_id"] = lojas_id
        if categorias_servico_id is not None:
            params["categorias_servico_id"] = categorias_servico_id
        if visao is not None:
            params["visao"] = visao
        dados = await self._requisitar("GET", "/indicadores/operacao-sla", token=token, params=params)
        return ler_resultado_operacao(dados)

    async def catalogo_indicadores_causas(self, token: str) -> CatalogoCausas:
        dados = await self._requisitar("GET", "/indicadores/causas-recorrencia/filtros", token=token)
        return ler_catalogo_causas(dados)

    async def consultar_indicadores_causas(
        self, token: str, *, t0: int, t1: int,
        lojas_id: int | None = None, ativos_referencia_id: int | None = None,
        categorias_servico_id: int | None = None, visao: str | None = None,
    ) -> ResultadoCausas:
        params: dict[str, int | str] = {"t0": t0, "t1": t1}
        for campo, valor in (("lojas_id", lojas_id), ("ativos_referencia_id", ativos_referencia_id),
                             ("categorias_servico_id", categorias_servico_id), ("visao", visao)):
            if valor is not None:
                params[campo] = valor
        dados = await self._requisitar("GET", "/indicadores/causas-recorrencia", token=token, params=params)
        return ler_resultado_causas(dados)

    async def listar_ativos(self, token: str) -> list[AtivoServiceDesk]:
        return await self._listar_ativos_gerente_em(token, "/gerente/ativos")

    async def listar_ativos_historicos_gerente(self, token: str) -> list[AtivoServiceDesk]:
        return await self._listar_ativos_gerente_em(token, "/gerente/ativos-historicos")

    async def _listar_ativos_gerente_em(self, token: str, caminho: str) -> list[AtivoServiceDesk]:
        dados = await self._requisitar("GET", caminho, token=token)
        return [
            AtivoServiceDesk(
                id=_inteiro(item.get("id"), "id"),
                nome_ativo=_texto(item.get("nome_ativo"), "nome_ativo"),
                tipo=_texto(item.get("tipo"), "tipo"),
                status_atual=_estado_totem_opcional(item.get("status_atual"), "status_atual"),
                loja=_referencia_loja(item.get("loja")),
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
                status_atual=_estado_totem_opcional(item.get("status_atual"), "status_atual"),
                loja=_referencia_loja(item.get("loja")),
            )
            for item in _colecao(dados)
        ]

    async def listar_tecnicos_fila(self, token: str) -> list[ReferenciaUsuario]:
        dados = await self._requisitar("GET", "/tecnico/ativos", token=token)
        tecnicos = dados.get("tecnicos")
        if not isinstance(tecnicos, list):
            raise XanoContratoInvalido("O Xano retornou um catálogo de Técnicos incompatível.")
        resultado = []
        for item in tecnicos:
            tecnico = _referencia_usuario(item, "tecnicos")
            if tecnico is None:
                raise XanoContratoInvalido("O Xano retornou um Técnico inválido no catálogo.")
            resultado.append(tecnico)
        return resultado

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

    async def opcoes_abertura_global(self, token: str) -> dict[str, list[dict[str, Any]]]:
        dados = await self._requisitar("GET", "/chamados/abertura/filtros", token=token)
        if set(dados) != {"ativos", "categorias"}:
            raise XanoContratoInvalido("O Xano retornou opções de abertura inválidas.")
        opcoes = {}
        for campo in ("ativos", "categorias"):
            if not isinstance(dados[campo], list):
                raise XanoContratoInvalido("O Xano retornou opções de abertura inválidas.")
            opcoes[campo] = []
            for valor in dados[campo]:
                item = _objeto_exato(valor, campo, {"id", "nome"})
                opcoes[campo].append({"id": _inteiro(item["id"], "id"), "nome": _texto(item["nome"], "nome")})
        return opcoes

    async def abrir_chamado_global(
        self, token: str, *, ativos_referencia_id: int, categorias_servico_id: int,
        prioridade: str, titulo: str, descricao: str,
    ) -> dict[str, Any]:
        dados = await self._requisitar(
            "POST", "/chamados", token=token,
            json={"ativos_referencia_id": ativos_referencia_id, "categorias_servico_id": categorias_servico_id,
                  "prioridade": prioridade, "titulo": titulo, "descricao": descricao},
        )
        chamado = _objeto(dados.get("chamado"), "chamado")
        _inteiro(chamado.get("id"), "chamado.id")
        return chamado

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
        self, token: str, *, numero: int | None = None,
        status: list[str] | None = None, ativo_ids: list[int] | None = None,
        data_inicio: int | None = None, data_fim: int | None = None,
        ultima_atualizacao_inicio: int | None = None, ultima_atualizacao_fim: int | None = None,
        ordenar_por: str = "criado_em", direcao: str = "DESC",
    ) -> ListaChamadosGerente:
        params = {"ordenar_por": ordenar_por, "direcao": direcao}
        for campo, valor in (("numero", numero), ("data_inicio", data_inicio), ("data_fim", data_fim),
                             ("ultima_atualizacao_inicio", ultima_atualizacao_inicio), ("ultima_atualizacao_fim", ultima_atualizacao_fim),
                             ("status", status), ("ativo_ids", ativo_ids)):
            if valor is not None and valor != "" and valor != []:
                params[campo] = json.dumps(valor, ensure_ascii=False) if isinstance(valor, list) else valor
        dados = await self._requisitar("GET", "/gerente/chamados", token=token, params=params)
        return _lista_chamados_gerente(dados)

    async def obter_preferencia_filtros_gerente(
        self, token: str
    ) -> PreferenciaFiltrosGerente:
        dados = await self._requisitar("GET", "/gerente/preferencias-fila", token=token)
        return _preferencia_filtros_gerente(dados.get("preferencia"))

    async def salvar_preferencia_filtros_gerente(
        self, token: str, **filtros: int | str | None
    ) -> PreferenciaFiltrosGerente:
        dados = await self._requisitar(
            "PUT", "/gerente/preferencias-fila", token=token, json=filtros,
            erro_400_como_entrada=True,
        )
        return _preferencia_filtros_gerente(dados.get("preferencia"))

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

    async def rejeitar_solucao(
        self, token: str, chamado_id: int, *, justificativa: str,
        ultima_atualizacao_em: int,
    ) -> ChamadoDetalhe:
        dados = await self._requisitar(
            "POST", f"/gerente/chamados/{chamado_id}/rejeitar-solucao",
            token=token,
            json={"justificativa": justificativa, "ultima_atualizacao_em": ultima_atualizacao_em},
            erro_400_como_entrada=True,
        )
        if set(dados) != {"sucesso", "chamado"} or dados["sucesso"] is not True:
            raise XanoContratoInvalido("A rejeição não foi confirmada pelo Xano.")
        return _detalhe_gerente(_objeto(dados["chamado"], "chamado"))

    async def listar_historico_status_gerente(self, token: str, chamado_id: int) -> list[HistoricoStatusItem]:
        dados = await self._requisitar("GET", f"/gerente/chamados/{chamado_id}/historico-status", token=token)
        return _historico_status(dados)

    async def obter_consumo_sla_gerente(self, token: str, chamado_id: int) -> ConsumoSLADTO:
        dados = await self._requisitar("GET", f"/gerente/chamados/{chamado_id}/consumo-sla", token=token)
        return _consumo_sla(dados)

    async def obter_consumo_sla_tecnico(self, token: str, chamado_id: int) -> ConsumoSLADTO:
        dados = await self._requisitar("GET", f"/tecnico/chamados/{chamado_id}/consumo-sla", token=token)
        return _consumo_sla(dados)

    async def listar_chamados_solicitante(self, token: str) -> list[ChamadoResumo]:
        dados = await self._requisitar("GET", "/solicitante/chamados", token=token)
        if set(dados) != {"items"}:
            raise XanoContratoInvalido("A lista do solicitante é incompatível.")
        campos = {"id", "titulo", "descricao", "status", "prioridade", "origem",
                  "criado_em", "ultima_atualizacao_em", "ativo", "categoria"}
        return [_resumo_gerente(_objeto_exato(item, "item", campos)) for item in _colecao(dados)]

    async def obter_chamado_solicitante(self, token: str, chamado_id: int) -> ChamadoDetalheSolicitante:
        dados = await self._requisitar("GET", f"/solicitante/chamados/{chamado_id}", token=token)
        if set(dados) != {"chamado"}:
            raise XanoContratoInvalido("O detalhe do solicitante é incompatível.")
        return _detalhe_solicitante(dados["chamado"])

    async def listar_comentarios_publicos_solicitante(self, token: str, chamado_id: int) -> list[ComentarioPublico]:
        dados = await self._requisitar("GET", f"/solicitante/chamados/{chamado_id}/comentarios", token=token)
        if set(dados) != {"items"}:
            raise XanoContratoInvalido("Os comentários do solicitante são incompatíveis.")
        return [_comentario_publico(item) for item in _colecao(dados)]

    async def listar_historico_status_solicitante(self, token: str, chamado_id: int) -> list[HistoricoStatusItem]:
        dados = await self._requisitar("GET", f"/solicitante/chamados/{chamado_id}/historico-status", token=token)
        return _historico_status(dados)

    async def listar_chamados_tecnico(
        self, token: str, *, numero: int | None = None,
        status: list[str] | None = None, ativo_ids: list[int] | None = None,
        data_inicio: int | None = None, data_fim: int | None = None,
        ultima_atualizacao_inicio: int | None = None, ultima_atualizacao_fim: int | None = None,
        loja_ids: list[int] | None = None, prioridades: list[str] | None = None,
        responsavel_ids: list[int] | None = None, incluir_nao_atribuido: bool = False,
        ordenar_por: str = "numero", direcao: str = "DESC", somente_atribuidos_a_mim: bool = False,
    ) -> ListaChamadosGerente:
        params = {}
        for campo, valor in (("numero", numero), ("status", status), ("ativo_ids", ativo_ids),
                             ("data_inicio", data_inicio), ("data_fim", data_fim),
                             ("ultima_atualizacao_inicio", ultima_atualizacao_inicio), ("ultima_atualizacao_fim", ultima_atualizacao_fim),
                             ("loja_ids", loja_ids), ("prioridades", prioridades), ("responsavel_ids", responsavel_ids)):
            if valor is not None and valor != "" and valor != []:
                params[campo] = json.dumps(valor, ensure_ascii=False) if isinstance(valor, list) else valor
        if incluir_nao_atribuido:
            params["incluir_nao_atribuido"] = True
        if somente_atribuidos_a_mim:
            params["somente_atribuidos_a_mim"] = True
        if ordenar_por != "numero":
            params["ordenar_por"] = ordenar_por
        if direcao != "DESC":
            params["direcao"] = direcao
        dados = await self._requisitar("GET", "/tecnico/chamados", token=token, params=params)
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
        self, token: str, *, escopo: str, numero: int | None,
        status: list[str], ativo_ids: list[int], data_inicio: int | None, data_fim: int | None,
        prioridades: list[str], responsavel_ids: list[int], incluir_nao_atribuido: bool,
        ordenar_por: str, direcao: str, ultima_atualizacao_inicio: int | None = None,
        ultima_atualizacao_fim: int | None = None, loja_ids: list[int] | None = None,
    ) -> PreferenciaFilaTecnica:
        dados = await self._requisitar(
            "PUT", "/tecnico/preferencias-fila", token=token,
            json={"escopo": escopo, "numero": numero, "status": status, "ativo_ids": ativo_ids,
                  "data_inicio": data_inicio, "data_fim": data_fim,
                  "ultima_atualizacao_inicio": ultima_atualizacao_inicio, "ultima_atualizacao_fim": ultima_atualizacao_fim,
                  "loja_ids": loja_ids or [], "prioridades": prioridades, "responsavel_ids": responsavel_ids,
                  "incluir_nao_atribuido": incluir_nao_atribuido, "ordenar_por": ordenar_por, "direcao": direcao},
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
