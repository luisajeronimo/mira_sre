"""Páginas da fila e detalhe de chamados do Técnico."""

import reflex as rx

from app.chamados.shared import cabecalho, erro
from app.chamados.tecnico.state import ChamadosTecnicoState
from app.components.layout import casca_conteudo, estado_carregamento, estado_revalidacao
from app.states.auth import AuthState


def _fila_tecnico() -> rx.Component:
    return rx.vstack(
        cabecalho("Fila técnica", "Consulte chamados elegíveis para assumir."),
        rx.hstack(
            rx.button(
                "Não atribuídos",
                variant=rx.cond(ChamadosTecnicoState.visao == "nao_atribuidos", "solid", "outline"),
                on_click=ChamadosTecnicoState.selecionar_visao("nao_atribuidos"),
            ),
            rx.button(
                "Atribuídos a mim",
                variant=rx.cond(ChamadosTecnicoState.visao == "atribuidos_a_mim", "solid", "outline"),
                on_click=ChamadosTecnicoState.selecionar_visao("atribuidos_a_mim"),
            ),
            spacing="3",
        ),
        erro(ChamadosTecnicoState.mensagem_fila),
        erro(ChamadosTecnicoState.mensagem_assuncao),
        rx.cond(
            ChamadosTecnicoState.carregando_fila,
            rx.center(rx.spinner(size="3"), width="100%", padding="4rem"),
            rx.cond(
                ChamadosTecnicoState.chamados.length() == 0,
                rx.callout("Nenhum chamado elegível encontrado.", icon="info"),
                rx.vstack(
                    rx.foreach(
                        ChamadosTecnicoState.chamados,
                        lambda item: rx.card(
                            rx.vstack(
                                rx.hstack(
                                    rx.vstack(
                                        rx.text("Chamado #" + item["id"].to_string(), weight="bold"),
                                        rx.heading(item["titulo"], size="4"),
                                        align="start",
                                        spacing="1",
                                    ),
                                    rx.badge(item["status"]),
                                    justify="between",
                                    width="100%",
                                ),
                                rx.text("Prioridade: " + item["prioridade"]),
                                rx.text("Categoria: " + item["categoria_nome"], color="gray"),
                                rx.text("Técnico: " + item["tecnico_nome"], color="gray"),
                                rx.hstack(
                                    rx.link("Ver detalhe", href="/tecnico/chamados/" + item["id"].to_string()),
                                    rx.cond(
                                        item["pode_assumir"],
                                        rx.button(
                                            rx.cond(ChamadosTecnicoState.assumindo_id == item["id"], "Assumindo...", "Assumir"),
                                            on_click=ChamadosTecnicoState.assumir(item["id"]),
                                            disabled=ChamadosTecnicoState.assumindo_id != None,
                                        ),
                                        rx.fragment(),
                                    ),
                                    spacing="3",
                                ),
                                align="start",
                                width="100%",
                            ),
                            width="100%",
                        ),
                    ),
                    width="100%",
                    spacing="3",
                ),
            ),
        ),
        spacing="5",
        width="100%",
    )


def _detalhe_tecnico() -> rx.Component:
    return rx.vstack(
        cabecalho("Detalhe técnico", "Consulta somente leitura, com autoatribuição aprovada."),
        erro(ChamadosTecnicoState.mensagem_detalhe_tecnico),
        erro(ChamadosTecnicoState.mensagem_assuncao),
        rx.cond(
            ChamadosTecnicoState.carregando_detalhe_tecnico,
            rx.spinner(size="3"),
            rx.card(
                rx.vstack(
                    rx.text("Chamado #" + ChamadosTecnicoState.chamado["id"].to_string(), weight="bold"),
                    rx.heading(ChamadosTecnicoState.chamado["titulo"], size="5"),
                    rx.text(ChamadosTecnicoState.chamado["descricao"], white_space="pre-wrap"),
                    rx.text("Status: " + ChamadosTecnicoState.chamado["status"]),
                    rx.text("Prioridade: " + ChamadosTecnicoState.chamado["prioridade"]),
                    rx.text("Origem: " + ChamadosTecnicoState.chamado["origem"]),
                    rx.cond(
                        ChamadosTecnicoState.chamado["criador_sistema_nome"] != "",
                        rx.text(
                            "Criado por: "
                            + ChamadosTecnicoState.chamado["criador_sistema_nome"]
                        ),
                    ),
                    rx.text("SLA aplicado: " + ChamadosTecnicoState.chamado["sla_horas_texto"]),
                    rx.text("Técnico: " + ChamadosTecnicoState.chamado["tecnico_nome"]),
                    rx.text("Atribuído em: " + ChamadosTecnicoState.chamado["atribuido_em_texto"]),
                    rx.cond(
                        ChamadosTecnicoState.chamado["pode_assumir"],
                        rx.button(
                            rx.cond(ChamadosTecnicoState.assumindo_id != None, "Assumindo...", "Assumir"),
                            on_click=ChamadosTecnicoState.assumir(ChamadosTecnicoState.chamado["id"]),
                            disabled=ChamadosTecnicoState.assumindo_id != None,
                        ),
                        rx.fragment(),
                    ),
                    align="start",
                    spacing="2",
                ),
                width="100%",
            ),
        ),
        rx.link("Voltar à fila", href="/tecnico"),
        spacing="5",
        width="100%",
    )


def _protegida_tecnico(conteudo: rx.Component, evento) -> rx.Component:
    return rx.cond(
        AuthState.carregando,
        estado_carregamento(),
        rx.cond(
            AuthState.sessao_confirmada & (AuthState.role == "tecnico"),
            casca_conteudo(conteudo, "/tecnico"),
            estado_revalidacao(evento),
        ),
    )


def tecnico_chamados() -> rx.Component:
    return _protegida_tecnico(_fila_tecnico(), ChamadosTecnicoState.carregar_fila)


def detalhe_chamado_tecnico() -> rx.Component:
    return _protegida_tecnico(
        _detalhe_tecnico(),
        ChamadosTecnicoState.carregar_detalhe_tecnico,
    )
