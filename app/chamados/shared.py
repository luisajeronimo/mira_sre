"""Transformações puras e componentes apresentacionais comuns de chamados."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, TypedDict

import reflex as rx

from app.components.visual import FOCO_VISIVEL, TEXTO, TEXTO_SECUNDARIO, rotulo_campo

from app.services.service_desk import (
    ChamadoDetalhe,
    ChamadoDetalheSolicitante,
    ChamadoResumo,
    ComentarioPublico,
    ConsumoSLADTO,
    EventoTimelineChamado,
    HistoricoStatusItem,
)


_STATUS_ATRIBUICAO_PERMITIDA = frozenset(
    {
        "Novo",
        "Em Atendimento",
        "Aguardando Solicitante",
        "Aguardando Mudança",
        "Resolvido",
        "Solução Rejeitada",
    }
)


def _status_permite_atribuicao(status: str | None) -> bool:
    return status in _STATUS_ATRIBUICAO_PERMITIDA


def _timestamp_para_texto(valor: int | None) -> str:
    if valor is None:
        return "Não informado"
    try:
        return datetime.fromtimestamp(valor / 1000, tz=timezone.utc).astimezone().strftime(
            "%d/%m/%Y %H:%M"
        )
    except (OverflowError, OSError, TypeError, ValueError):
        return "Não informado"


def _timestamp_funcional_para_texto(valor: int) -> str:
    """Formata timestamp obrigatório já validado pelo contrato do chamado."""

    return datetime.fromtimestamp(valor / 1000, tz=timezone.utc).astimezone().strftime(
        "%d/%m/%Y %H:%M"
    )


def _numero_para_texto(valor: float | None) -> str:
    if valor is None:
        return "Não informado"
    return f"{valor:g} h"


def _resumo_para_dict(chamado: ChamadoResumo) -> dict[str, Any]:
    descricao = chamado.descricao or ""
    ocorrencia = descricao
    if len(descricao) > 80:
        ocorrencia = descricao[:80] + "…"
    return {
        "id": chamado.id,
        "titulo": chamado.titulo,
        "descricao": descricao,
        "ocorrencia": ocorrencia or "Não informado",
        "status": chamado.status,
        "prioridade": chamado.prioridade,
        "origem": chamado.origem or "Não informado",
        "criado_em_texto": _timestamp_funcional_para_texto(chamado.criado_em),
        "ultima_atualizacao_em_texto": _timestamp_funcional_para_texto(
            chamado.ultima_atualizacao_em
        ),
        "ativo_nome": chamado.ativo.nome_ativo,
        "loja_nome": chamado.loja.nome if chamado.loja is not None else "Não informado",
        "categoria_nome": chamado.categoria.nome,
    }


def _detalhe_para_dict(chamado: ChamadoDetalhe | ChamadoDetalheSolicitante) -> dict[str, Any]:
    dados = asdict(chamado)
    resumo_totem = dados.get("resumo_totem")
    if resumo_totem is not None and resumo_totem["status_atual"] is None:
        resumo_totem["status_atual"] = "Sem telemetria"
    if resumo_totem is not None and resumo_totem["ultima_telemetria"] is not None:
        resumo_totem["ultima_telemetria"]["evento_timestamp_texto"] = _timestamp_para_texto(
            resumo_totem["ultima_telemetria"]["evento_timestamp"]
        )
    dados["status"] = chamado.status or "Não informado"
    dados["criado_em_texto"] = _timestamp_funcional_para_texto(chamado.criado_em)
    dados["ultima_atualizacao_em_texto"] = _timestamp_funcional_para_texto(
        chamado.ultima_atualizacao_em
    )
    dados["sla_horas_texto"] = _numero_para_texto(chamado.sla_horas_aplicado)
    dados["atribuido_em_texto"] = _timestamp_para_texto(chamado.atribuido_em)
    dados["tecnico_nome"] = (
        chamado.tecnico.nome if chamado.tecnico is not None else "Não atribuído"
    )
    dados["ativo_nome"] = chamado.ativo.nome_ativo
    dados["loja_nome"] = chamado.loja.nome if chamado.loja is not None else "Não informado"
    dados["categoria_nome"] = chamado.categoria.nome
    dados["solicitante_nome"] = (
        chamado.solicitante.nome if chamado.solicitante is not None else "Não informado"
    )
    dados["criador_sistema_nome"] = (
        "Bot de Fiscalização"
        if chamado.criador_sistema == "bot_fiscalizacao"
        else ""
    )
    dados["pode_assumir"] = (
        _status_permite_atribuicao(chamado.status) and chamado.tecnico is None
    )
    dados["pode_atribuir"] = _status_permite_atribuicao(chamado.status)
    return dados


def comentario_publico_para_dict(comentario: ComentarioPublico) -> dict[str, Any]:
    return {
        "id": comentario.id,
        "conteudo": comentario.conteudo,
        "criado_em_texto": _timestamp_para_texto(comentario.criado_em),
        "autor_nome": comentario.autor.nome if comentario.autor is not None else "Não informado",
    }


def historico_status_para_dict(item: HistoricoStatusItem) -> HistoricoStatusView:
    autor = item.autor
    return {
        "id": item.id,
        "status_anterior": item.status_anterior,
        "status_resultante": item.status_resultante,
        "criado_em_texto": _timestamp_funcional_para_texto(item.criado_em),
        "autor_nome": autor.nome if autor is not None else "Autor não identificado",
        "autor_perfil": (autor.perfil or "") if autor is not None else "",
    }


def consumo_sla_para_dict(consumo: ConsumoSLADTO) -> dict[str, str]:
    if not consumo.calculavel:
        return {"situacao": "Não calculável", "percentual": "", "prazo": "",
                "motivo": consumo.motivo or "Motivo não informado."}
    faixas = {"normal": "Dentro do SLA", "risco": "Próximo do vencimento",
              "critico": "Próximo do vencimento", "violado": "Vencido"}
    situacao = {"pausada": "Pausado", "encerrada": "Encerrado"}.get(
        consumo.estado_contagem or "", faixas.get(consumo.faixa or "", "Não calculável")
    )
    percentual = f"{(consumo.fracao_consumida or 0) * 100:.1f}% consumido"
    prazo = ""
    if consumo.estado_contagem == "em_contagem" and consumo.sla_horas_aplicado is not None and consumo.consumo_ms is not None:
        restante = consumo.sla_horas_aplicado * 3600000 - consumo.consumo_ms
        prazo = f"{abs(restante) / 3600000:.1f} h {'restantes' if restante >= 0 else 'excedidas'}"
    return {"situacao": situacao, "percentual": percentual, "prazo": prazo, "motivo": ""}


def campo_sla_com_consumo(
    sla_aplicado: Any,
    consumo: Any,
    carregando: Any,
    mensagem_erro: Any,
) -> rx.Component:
    """Mantém o valor aplicado visível e revela o consumo sob demanda."""
    return rx.vstack(
        rx.hstack(
            rotulo_campo("SLA aplicado"),
            rx.popover.root(
                rx.popover.trigger(
                    rx.icon_button(
                        rx.icon("info", size=16),
                        variant="ghost",
                        size="2",
                        radius="full",
                        color=TEXTO_SECUNDARIO,
                        aria_label="Ver consumo de SLA",
                        title="Ver consumo de SLA",
                        _focus_visible=FOCO_VISIVEL,
                    )
                ),
                rx.popover.content(
                    rx.vstack(
                        rx.text("Consumo de SLA", size="2", weight="bold"),
                        rx.cond(
                            carregando,
                            rx.hstack(rx.spinner(size="1"), rx.text("Calculando consumo...", size="2")),
                            rx.cond(
                                mensagem_erro != "",
                                rx.text(mensagem_erro, size="2", color="#B42318"),
                                rx.cond(
                                    consumo.length() > 0,
                                    rx.vstack(
                                        rx.text(consumo["situacao"], weight="medium"),
                                        rx.cond(consumo["percentual"] != "", rx.text(consumo["percentual"], size="2"), rx.fragment()),
                                        rx.cond(consumo["prazo"] != "", rx.text(consumo["prazo"], size="2"), rx.fragment()),
                                        rx.cond(consumo["motivo"] != "", rx.text(consumo["motivo"], size="2"), rx.fragment()),
                                        align="start", spacing="1",
                                    ),
                                    rx.text("Consumo indisponível.", size="2"),
                                ),
                            ),
                        ),
                        align="start", spacing="2", width="100%",
                    ),
                    side="top",
                    align="start",
                    width="20rem",
                    max_width="90vw",
                ),
            ),
            align="center", spacing="1",
        ),
        rx.box(sla_aplicado, color=TEXTO, width="100%"),
        spacing="1",
        align="start",
        padding_y="0.25rem",
        width="100%",
    )


def evento_timeline_para_dict(
    evento: EventoTimelineChamado,
    *,
    tecnicos: dict[int, str] | None = None,
    categorias: dict[int, str] | None = None,
) -> dict[str, Any]:
    titulos = {
        "comentario": "Comentário",
        "atribuicao": "Atribuição",
        "reatribuicao": "Reatribuição",
        "liberacao": "Liberação",
        "alteracao_chamado": "Alteração do chamado",
    }
    alteracoes = evento.alteracoes or {}
    rotulos = {
        "responsavel": "Responsável",
        "status": "Status",
        "prioridade": "Prioridade",
        "categoria": "Categoria",
        "sla_horas_aplicado": "SLA aplicado",
    }

    def valor(campo: str, dado: Any) -> str:
        if campo == "responsavel":
            if dado is None:
                return "Não atribuído"
            return (tecnicos or {}).get(dado, f"Técnico #{dado}")
        if campo == "categoria":
            return (categorias or {}).get(dado, f"Categoria #{dado}")
        if campo == "sla_horas_aplicado":
            return _numero_para_texto(dado if isinstance(dado, (int, float)) else None)
        return str(dado) if dado is not None else "Não informado"

    detalhes = [
        {
            "campo": rotulos[campo],
            "anterior": valor(campo, par.get("anterior")),
            "resultante": valor(campo, par.get("resultante")),
        }
        for campo in rotulos
        if isinstance(alteracoes.get(campo), dict)
        for par in [alteracoes[campo]]
    ]
    return {
        "id": evento.id,
        "tipo": evento.tipo,
        "titulo": titulos[evento.tipo],
        "conteudo": evento.conteudo or "",
        "visibilidade": (evento.visibilidade or "") if evento.tipo == "comentario" else "",
        "visibilidade_texto": (
            "Público" if evento.visibilidade == "publica" and evento.tipo == "comentario" else ("Interno" if evento.visibilidade == "interna" and evento.tipo == "comentario" else "")
        ),
        "criado_em_texto": _timestamp_funcional_para_texto(evento.criado_em),
        "autor_nome": (
            evento.autor.nome if evento.autor is not None else "Não informado"
        ),
        "tecnico_anterior_nome": (
            evento.tecnico_anterior.nome
            if evento.tecnico_anterior is not None
            else ""
        ),
        "tecnico_novo_nome": (
            evento.tecnico_novo.nome if evento.tecnico_novo is not None else ""
        ),
        "alteracoes": evento.alteracoes,
        "alteracoes_detalhadas": detalhes,
        "comentario_interacao_id": (
            alteracoes.get("comentario_interacao_id")
            if isinstance(alteracoes.get("comentario_interacao_id"), int)
            else None
        ),
        "comentario_conteudo": "",
        "comentario_visibilidade_texto": "",
        "comentario_autor_nome": "",
        "comentario_criado_em_texto": "",
    }


def _tecnico_para_dict(chamado: ChamadoResumo) -> dict[str, Any]:
    tecnico = chamado.tecnico
    descricao = chamado.descricao or ""
    ocorrencia = descricao
    if len(descricao) > 80:
        ocorrencia = descricao[:80] + "…"
    aberto_por = "Não informado"
    if chamado.origem == "automatico":
        aberto_por = "Bot de Fiscalização"
    elif chamado.solicitante is not None:
        aberto_por = chamado.solicitante.nome
    return {
        "id": chamado.id,
        "titulo": chamado.titulo,
        "descricao": descricao,
        "ocorrencia": ocorrencia or "Não informado",
        "status": chamado.status or "Não informado",
        "prioridade": chamado.prioridade,
        "origem": chamado.origem or "Não informado",
        "criado_em_texto": _timestamp_funcional_para_texto(chamado.criado_em),
        "ultima_atualizacao_em_texto": _timestamp_funcional_para_texto(
            chamado.ultima_atualizacao_em
        ),
        "sla_horas_texto": _numero_para_texto(chamado.sla_horas_aplicado),
        "atribuido_em_texto": _timestamp_para_texto(chamado.atribuido_em),
        "ativo_nome": chamado.ativo.nome_ativo,
        "categoria_nome": chamado.categoria.nome,
        "aberto_por": aberto_por,
        "loja_nome": chamado.loja.nome if chamado.loja is not None else "Não informado",
        "tecnico_nome": tecnico.nome if tecnico is not None else "Não atribuído",
        "pode_assumir": (
            _status_permite_atribuicao(chamado.status) and tecnico is None
        ),
    }


class ChamadoView(TypedDict):
    id: int
    titulo: str
    descricao: str
    ocorrencia: str
    status: str
    prioridade: str
    origem: str
    criado_em_texto: str
    ultima_atualizacao_em_texto: str
    ativo_nome: str
    loja_nome: str
    categoria_nome: str


class DetalheView(TypedDict, total=False):
    id: int
    titulo: str
    descricao: str
    status: str
    prioridade: str
    origem: str
    criado_em_texto: str
    ultima_atualizacao_em_texto: str
    sla_horas_texto: str
    atribuido_em_texto: str
    tecnico_nome: str
    ativo_nome: str
    loja_nome: str
    categoria_nome: str
    solicitante_nome: str
    criador_sistema_nome: str
    pode_assumir: bool
    pode_atribuir: bool
    pode_liberar: bool
    resumo_totem: "ResumoTotemChamadoView | None"


class TelemetriaResumoTotemView(TypedDict):
    evento_timestamp_texto: str
    uso_cpu: float
    uso_memoria: float
    temperatura: float
    status_rede: str


class ReferenciaLojaView(TypedDict):
    id: int
    nome: str


class ResumoTotemChamadoView(TypedDict):
    id: int
    nome_ativo: str
    loja: ReferenciaLojaView
    status_atual: str
    ultima_telemetria: TelemetriaResumoTotemView | None


class ComentarioView(TypedDict):
    id: int
    conteudo: str
    criado_em_texto: str
    autor_nome: str


class HistoricoStatusView(TypedDict):
    id: int
    status_anterior: str
    status_resultante: str
    criado_em_texto: str
    autor_nome: str
    autor_perfil: str


class TimelineView(TypedDict):
    id: int
    tipo: str
    titulo: str
    conteudo: str
    visibilidade: str
    visibilidade_texto: str
    criado_em_texto: str
    autor_nome: str
    tecnico_anterior_nome: str
    tecnico_novo_nome: str
    alteracoes: dict[str, Any] | None
    alteracoes_detalhadas: list[dict[str, str]]
    comentario_interacao_id: int | None
    comentario_conteudo: str
    comentario_visibilidade_texto: str
    comentario_autor_nome: str
    comentario_criado_em_texto: str


class TecnicoOpcaoView(TypedDict):
    id: int
    nome: str


class TecnicoView(TypedDict, total=False):
    id: int
    titulo: str
    descricao: str
    ocorrencia: str
    status: str
    prioridade: str
    origem: str
    criado_em_texto: str
    ultima_atualizacao_em_texto: str
    sla_horas_texto: str
    atribuido_em_texto: str
    ativo_nome: str
    loja_nome: str
    categoria_nome: str
    aberto_por: str
    tecnico_nome: str
    pode_assumir: bool


def erro(mensagem: rx.Var) -> rx.Component:
    return rx.cond(
        mensagem != "",
        rx.callout(mensagem, icon="triangle_alert", color_scheme="red"),
    )


def cabecalho(titulo: str, descricao: str) -> rx.Component:
    return rx.vstack(
        rx.heading(titulo, size="7", color=TEXTO, letter_spacing="-0.03em"),
        rx.text(descricao, color=TEXTO_SECUNDARIO, size="2", max_width="46rem", line_height="1.7"),
        align="start",
        spacing="2",
        width="100%",
    )


def botao_criar_chamado() -> rx.Component:
    return rx.link(
        rx.button(rx.icon("plus", size=17), "Criar chamado", color_scheme="ruby"),
        href="/chamados/novo",
    )


def cabecalho_lista_chamados(
    titulo: str, descricao: str, acao: rx.Component
) -> rx.Component:
    return rx.hstack(
        rx.box(cabecalho(titulo, descricao), flex="1", min_width="0"),
        acao,
        justify="between",
        align="center",
        width="100%",
    )
