"""Página de monitoramento dos Totens."""

import reflex as rx

from app.components.layout import (
    casca_conteudo,
    estado_carregamento,
    estado_revalidacao,
)
from app.monitoramento.state import MonitoramentoState
from app.states.auth import AuthState


def _cabecalho() -> rx.Component:
    return rx.vstack(
        rx.heading("Monitoramento dos Totens", size="7"),
        rx.text(
            "Acompanhe o status dos Totens da sua operação.",
            color="gray",
        ),
        align="start",
        width="100%",
        spacing="1",
    )


def _resumo() -> rx.Component:
    return rx.grid(
        rx.card(
            rx.vstack(
                rx.text("Total de Totens", color="gray"),
                rx.heading(
                    MonitoramentoState.total_totens,
                    size="7",
                ),
                align="start",
            ),
        ),
        rx.card(
            rx.vstack(
                rx.text("Online", color="gray"),
                rx.heading(
                    MonitoramentoState.totens_online,
                    size="7",
                ),
                align="start",
            ),
        ),
        rx.card(
            rx.vstack(
                rx.text("Offline", color="gray"),
                rx.heading(
                    MonitoramentoState.totens_offline,
                    size="7",
                ),
                align="start",
            ),
        ),
        columns="3",
        spacing="4",
        width="100%",
    )


def _lista_totens() -> rx.Component:
    return rx.vstack(
        rx.heading("Totens", size="5"),
        rx.cond(
            MonitoramentoState.carregando,
            rx.center(
                rx.spinner(size="3"),
                width="100%",
                padding="3rem",
            ),
            rx.cond(
                MonitoramentoState.ativos.length() == 0,
                rx.callout(
                    "Nenhum Totem encontrado.",
                    icon="info",
                ),
                rx.vstack(
                    rx.foreach(
                        MonitoramentoState.ativos,
                        lambda totem: rx.card(
                            rx.hstack(
                                rx.vstack(
                                    rx.text(
                                        totem["nome_ativo"],
                                        weight="bold",
                                    ),
                                    rx.text(
                                        totem["tipo"],
                                        color="gray",
                                    ),
                                    align="start",
                                    spacing="1",
                                ),
                                rx.badge(
                                    totem["status_atual"],
                                ),
                                justify="between",
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
        align="start",
        width="100%",
        spacing="3",
    )


def _conteudo() -> rx.Component:
    return rx.vstack(
        _cabecalho(),
        _resumo(),
        rx.cond(
            MonitoramentoState.mensagem_erro != "",
            rx.callout(
                MonitoramentoState.mensagem_erro,
                icon="triangle_alert",
                color_scheme="red",
            ),
        ),
        _lista_totens(),
        width="100%",
        spacing="5",
    )


def _protegida() -> rx.Component:
    return rx.cond(
        AuthState.carregando,
        estado_carregamento(),
        rx.cond(
            AuthState.sessao_confirmada,
            casca_conteudo(
                _conteudo(),
                "/monitoramento",
            ),
            estado_revalidacao(MonitoramentoState.carregar),
        ),
    )


def monitoramento() -> rx.Component:
    return _protegida()