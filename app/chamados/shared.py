"""Transformações puras e componentes apresentacionais comuns de chamados."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, TypedDict

import reflex as rx

from app.services.service_desk import (
    ChamadoDetalhe,
    ChamadoResumo,
    ComentarioPublico,
    EventoTimelineChamado,
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
        "categoria_nome": chamado.categoria.nome,
    }


def _detalhe_para_dict(chamado: ChamadoDetalhe) -> dict[str, Any]:
    dados = asdict(chamado)
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
        "visibilidade": evento.visibilidade,
        "visibilidade_texto": (
            "Público" if evento.visibilidade == "publica" else "Interno"
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
    }


def _tecnico_para_dict(chamado: ChamadoResumo) -> dict[str, Any]:
    tecnico = chamado.tecnico
    return {
        "id": chamado.id,
        "titulo": chamado.titulo,
        "descricao": chamado.descricao or "",
        "status": chamado.status or "Não informado",
        "prioridade": chamado.prioridade,
        "origem": chamado.origem or "Não informado",
        "criado_em_texto": _timestamp_funcional_para_texto(chamado.criado_em),
        "sla_horas_texto": _numero_para_texto(chamado.sla_horas_aplicado),
        "atribuido_em_texto": _timestamp_para_texto(chamado.atribuido_em),
        "ativo_nome": chamado.ativo.nome_ativo,
        "categoria_nome": chamado.categoria.nome,
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


class ComentarioView(TypedDict):
    id: int
    conteudo: str
    criado_em_texto: str
    autor_nome: str


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


class TecnicoOpcaoView(TypedDict):
    id: int
    nome: str


class TecnicoView(TypedDict, total=False):
    id: int
    titulo: str
    descricao: str
    status: str
    prioridade: str
    origem: str
    criado_em_texto: str
    sla_horas_texto: str
    atribuido_em_texto: str
    ativo_nome: str
    categoria_nome: str
    tecnico_nome: str
    pode_assumir: bool


def erro(mensagem: rx.Var) -> rx.Component:
    return rx.cond(
        mensagem != "",
        rx.callout(mensagem, icon="triangle_alert", color_scheme="red"),
    )


def cabecalho(titulo: str, descricao: str) -> rx.Component:
    return rx.vstack(
        rx.heading(titulo, size="7"),
        rx.text(descricao, color="gray"),
        align="start",
        spacing="1",
        width="100%",
    )
