"""Transformações puras e componentes apresentacionais comuns de chamados."""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, TypedDict

import reflex as rx

from app.services.service_desk import ChamadoDetalhe, ChamadoResumo, ComentarioPublico


def _timestamp_para_texto(valor: int | None) -> str:
    if valor is None:
        return "Não informado"
    try:
        return datetime.fromtimestamp(valor / 1000, tz=timezone.utc).astimezone().strftime(
            "%d/%m/%Y %H:%M"
        )
    except (OverflowError, OSError, TypeError, ValueError):
        return "Não informado"


def _numero_para_texto(valor: float | None) -> str:
    if valor is None:
        return "Não informado"
    return f"{valor:g} h"


def _resumo_para_dict(chamado: ChamadoResumo) -> dict[str, Any]:
    return {
        "id": chamado.id,
        "titulo": chamado.titulo,
        "status": chamado.status,
        "prioridade": chamado.prioridade,
        "origem": chamado.origem or "Não informado",
        "criado_em_texto": _timestamp_para_texto(chamado.criado_em),
        "categoria_nome": chamado.categoria.nome,
    }


def _detalhe_para_dict(chamado: ChamadoDetalhe) -> dict[str, Any]:
    dados = asdict(chamado)
    dados["criado_em_texto"] = _timestamp_para_texto(chamado.criado_em)
    dados["ultima_atualizacao_em_texto"] = _timestamp_para_texto(
        chamado.ultima_atualizacao_em
    )
    dados["sla_horas_texto"] = _numero_para_texto(chamado.sla_horas_aplicado)
    dados["atribuido_em_texto"] = _timestamp_para_texto(chamado.atribuido_em)
    dados["tecnico_nome"] = (
        chamado.tecnico.nome if chamado.tecnico is not None else "Não atribuído"
    )
    dados["ativo_nome"] = chamado.ativo.nome_ativo
    dados["categoria_nome"] = chamado.categoria.nome
    dados["solicitante_nome"] = (
        chamado.solicitante.nome if chamado.solicitante is not None else "Não informado"
    )
    dados["criador_sistema_nome"] = (
        "Bot de Fiscalização"
        if chamado.criador_sistema == "bot_fiscalizacao"
        else ""
    )
    dados["pode_assumir"] = chamado.status == "Novo" and chamado.tecnico is None
    return dados


def comentario_publico_para_dict(comentario: ComentarioPublico) -> dict[str, Any]:
    return {
        "id": comentario.id,
        "conteudo": comentario.conteudo,
        "criado_em_texto": _timestamp_para_texto(comentario.criado_em),
        "autor_nome": comentario.autor.nome if comentario.autor is not None else "Não informado",
    }


def _tecnico_para_dict(chamado: ChamadoResumo) -> dict[str, Any]:
    tecnico = chamado.tecnico
    return {
        "id": chamado.id,
        "titulo": chamado.titulo,
        "descricao": chamado.descricao or "",
        "status": chamado.status,
        "prioridade": chamado.prioridade,
        "origem": chamado.origem or "Não informado",
        "criado_em_texto": _timestamp_para_texto(chamado.criado_em),
        "sla_horas_texto": _numero_para_texto(chamado.sla_horas_aplicado),
        "atribuido_em_texto": _timestamp_para_texto(chamado.atribuido_em),
        "categoria_nome": chamado.categoria.nome,
        "tecnico_nome": tecnico.nome if tecnico is not None else "Não atribuído",
        "pode_assumir": chamado.status == "Novo" and tecnico is None,
    }


class ChamadoView(TypedDict):
    id: int
    titulo: str
    status: str
    prioridade: str
    origem: str
    criado_em_texto: str
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
    categoria_nome: str
    solicitante_nome: str
    criador_sistema_nome: str
    pode_assumir: bool


class ComentarioView(TypedDict):
    id: int
    conteudo: str
    criado_em_texto: str
    autor_nome: str


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
