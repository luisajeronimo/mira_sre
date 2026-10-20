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
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Totem"),
                                rx.table.column_header_cell("Loja"),
                                rx.table.column_header_cell("Estado"),
                                rx.table.column_header_cell("Última telemetria"),
                                rx.table.column_header_cell("Última transição"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                MonitoramentoState.ativos,
                                lambda totem: rx.table.row(
                                    rx.table.cell(
                                        rx.button(
                                            totem["nome_ativo"],
                                            variant="ghost",
                                            on_click=MonitoramentoState.selecionar_totem(
                                                totem["id"]
                                            ),
                                            disabled=MonitoramentoState.carregando_detalhe,
                                        )
                                    ),
                                    rx.table.cell(totem["loja_nome"]),
                                    rx.table.cell(rx.badge(totem["status_atual"])),
                                    rx.table.cell(totem["ultima_telemetria_em_texto"]),
                                    rx.table.cell(
                                        totem["ultima_transicao_disponibilidade_em_texto"]
                                    ),
                                ),
                            )
                        ),
                        width="100%",
                    ),
                    width="100%",
                    overflow_x="auto",
                ),
            ),
        ),
        align="start",
        width="100%",
        spacing="3",
    )


def _telemetria_atual() -> rx.Component:
    return rx.cond(
        MonitoramentoState.detalhe_totem["tem_ultima_telemetria"],
        rx.grid(
            rx.vstack(
                rx.text("Data e hora", size="2", color="gray"),
                rx.text(
                    MonitoramentoState.detalhe_totem["ultima_telemetria"][
                        "evento_timestamp_texto"
                    ]
                ),
                align="start",
            ),
            rx.vstack(
                rx.text("CPU", size="2", color="gray"),
                rx.text(
                    MonitoramentoState.detalhe_totem["ultima_telemetria"]["uso_cpu"]
                ),
                align="start",
            ),
            rx.vstack(
                rx.text("Memória", size="2", color="gray"),
                rx.text(
                    MonitoramentoState.detalhe_totem["ultima_telemetria"][
                        "uso_memoria"
                    ]
                ),
                align="start",
            ),
            rx.vstack(
                rx.text("Temperatura", size="2", color="gray"),
                rx.text(
                    MonitoramentoState.detalhe_totem["ultima_telemetria"][
                        "temperatura"
                    ]
                ),
                align="start",
            ),
            rx.vstack(
                rx.text("Rede", size="2", color="gray"),
                rx.text(
                    MonitoramentoState.detalhe_totem["ultima_telemetria"]["status_rede"]
                ),
                align="start",
            ),
            columns="2",
            spacing="3",
            width="100%",
        ),
        rx.callout("Nenhuma telemetria registrada.", icon="info"),
    )


def _historico_telemetrias() -> rx.Component:
    return rx.cond(
        MonitoramentoState.detalhe_totem["telemetrias"].length() > 0,
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Data e hora"),
                        rx.table.column_header_cell("CPU"),
                        rx.table.column_header_cell("Memória"),
                        rx.table.column_header_cell("Temperatura"),
                        rx.table.column_header_cell("Rede"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        MonitoramentoState.detalhe_totem["telemetrias"],
                        lambda telemetria: rx.table.row(
                            rx.table.cell(telemetria["evento_timestamp_texto"]),
                            rx.table.cell(telemetria["uso_cpu"]),
                            rx.table.cell(telemetria["uso_memoria"]),
                            rx.table.cell(telemetria["temperatura"]),
                            rx.table.cell(telemetria["status_rede"]),
                        ),
                    )
                ),
                width="100%",
            ),
            overflow_x="auto",
            width="100%",
        ),
        rx.callout("Nenhuma telemetria registrada.", icon="info"),
    )


def _transicoes() -> rx.Component:
    return rx.cond(
        MonitoramentoState.detalhe_totem["transicoes"].length() > 0,
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Estado"),
                        rx.table.column_header_cell("Detectado em"),
                        rx.table.column_header_cell("Limite de heartbeat"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        MonitoramentoState.detalhe_totem["transicoes"],
                        lambda transicao: rx.table.row(
                            rx.table.cell(rx.badge(transicao["status"])),
                            rx.table.cell(transicao["detectado_em_texto"]),
                            rx.table.cell(transicao["heartbeat_limite_minutos"]),
                        ),
                    )
                ),
                width="100%",
            ),
            overflow_x="auto",
            width="100%",
        ),
        rx.callout("Nenhuma transição de disponibilidade registrada.", icon="info"),
    )


def _incidentes() -> rx.Component:
    return rx.cond(
        MonitoramentoState.detalhe_totem["incidentes"].length() > 0,
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Título"),
                        rx.table.column_header_cell("Status"),
                        rx.table.column_header_cell("Prioridade"),
                        rx.table.column_header_cell("Abertura"),
                        rx.table.column_header_cell("Detalhe"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        MonitoramentoState.detalhe_totem["incidentes"],
                        lambda incidente: rx.table.row(
                            rx.table.cell(incidente["titulo"]),
                            rx.table.cell(rx.badge(incidente["status"])),
                            rx.table.cell(incidente["prioridade"]),
                            rx.table.cell(incidente["criado_em_texto"]),
                            rx.table.cell(
                                rx.link(
                                    "Ver chamado",
                                    href="/chamados/" + incidente["id"].to_string(),
                                )
                            ),
                        ),
                    )
                ),
                width="100%",
            ),
            overflow_x="auto",
            width="100%",
        ),
        rx.callout("Nenhum incidente automático de heartbeat registrado.", icon="info"),
    )


def _painel_detalhe() -> rx.Component:
    return rx.vstack(
        rx.heading("Detalhe do Totem", size="5"),
        rx.cond(
            MonitoramentoState.mensagem_erro_detalhe != "",
            rx.callout(
                MonitoramentoState.mensagem_erro_detalhe,
                icon="triangle_alert",
                color_scheme="red",
            ),
        ),
        rx.cond(
            MonitoramentoState.carregando_detalhe,
            rx.center(rx.spinner(size="3"), width="100%", padding="3rem"),
            rx.cond(
                MonitoramentoState.detalhe_carregado,
                rx.vstack(
                    rx.hstack(
                        rx.vstack(
                            rx.heading(MonitoramentoState.detalhe_totem["nome_ativo"], size="5"),
                            rx.text(MonitoramentoState.detalhe_totem["loja_nome"], color="gray"),
                            align="start",
                            spacing="1",
                        ),
                        rx.badge(MonitoramentoState.detalhe_totem["status_atual"]),
                        justify="between",
                        width="100%",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.text("Última telemetria", weight="bold"),
                            _telemetria_atual(),
                            align="start",
                            width="100%",
                        ),
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Histórico recente de telemetrias", weight="bold"),
                        _historico_telemetrias(),
                        align="start",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Eventos de disponibilidade registrados", weight="bold"),
                        rx.text("Transições persistidas pelo Xano.", size="2", color="gray"),
                        _transicoes(),
                        align="start",
                        width="100%",
                    ),
                    rx.vstack(
                        rx.text("Incidentes automáticos de heartbeat", weight="bold"),
                        _incidentes(),
                        align="start",
                        width="100%",
                    ),
                    align="start",
                    width="100%",
                    spacing="4",
                ),
                rx.callout("Selecione um Totem para consultar os dados registrados.", icon="info"),
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
        rx.grid(
            _lista_totens(),
            _painel_detalhe(),
            columns="2",
            spacing="5",
            width="100%",
            align="start",
        ),
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
                "/inicio",
            ),
            estado_revalidacao(MonitoramentoState.carregar),
        ),
    )


def monitoramento() -> rx.Component:
    return _protegida()
