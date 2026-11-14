"""Página de monitoramento dos Totens."""

import reflex as rx

from app.components.layout import casca_conteudo, estado_carregamento, estado_revalidacao
from app.components.visual import (
    BORDA, CANVAS, FOCO_VISIVEL, RAIO_CONTROLE, RAIO_SUPERFICIE,
    SUPERFICIE, TEXTO, TEXTO_SECUNDARIO, badge_status,
)
from app.monitoramento.state import MonitoramentoState
from app.states.auth import AuthState


def _cabecalho() -> rx.Component:
    return rx.vstack(
        rx.heading("Monitoramento dos Totens", size="7", color=TEXTO),
        rx.text("Acompanhe o status dos Totens da sua operação.",
                color=TEXTO_SECUNDARIO, size="2", line_height="1.7"),
        align="start", width="100%", spacing="1",
    )


def _indicador(rotulo: str, valor, icone: str, cor: str) -> rx.Component:
    return rx.hstack(
        rx.icon(icone, size=20, color=cor, flex_shrink="0"),
        rx.text(valor, size="6", weight="bold", color=TEXTO),
        rx.text(rotulo, size="2", color=TEXTO_SECUNDARIO),
        align="center", spacing="3", padding="1.25rem 1.5rem",
        class_name="mira-monitoring-count",
    )


def _resumo() -> rx.Component:
    return rx.grid(
        _indicador("Total de Totens", MonitoramentoState.total_totens, "monitor", TEXTO_SECUNDARIO),
        _indicador("Online", MonitoramentoState.totens_online, "wifi", "var(--green-11)"),
        _indicador("Offline", MonitoramentoState.totens_offline, "wifi-off", "var(--red-11)"),
        columns="3", width="100%", background=SUPERFICIE,
        border=f"1px solid {BORDA}", border_radius=RAIO_SUPERFICIE,
        class_name="mira-monitoring-summary",
        aria_label="Resumo dos estados persistidos dos Totens",
    )


def _vazio(icone: str, titulo: str, descricao: str = "") -> rx.Component:
    return rx.vstack(
        rx.center(rx.icon(icone, size=26, color=TEXTO_SECUNDARIO),
                  width="3.5rem", height="3.5rem", background=CANVAS, border_radius="12px"),
        rx.text(titulo, size="2", weight="medium", color=TEXTO, text_align="center"),
        *([rx.text(descricao, size="2", color=TEXTO_SECUNDARIO, text_align="center",
                   line_height="1.7", max_width="32ch")] if descricao else []),
        align="center", justify="center", width="100%", padding="2.5rem 1rem", spacing="3",
    )


def _opcao_totem(totem) -> rx.Component:
    selecionado = MonitoramentoState.totem_selecionado_id == totem["id"]
    return rx.button(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("monitor", size=17, flex_shrink="0"),
                    rx.text(totem["nome_ativo"], weight="bold", size="2"),
                    align="center", spacing="2", min_width="0",
                ),
                badge_status(totem["status_atual"]),
                align="center", justify="between", width="100%", spacing="2",
            ),
            rx.text(totem["loja_nome"], size="2", color=TEXTO_SECUNDARIO),
            rx.grid(
                rx.vstack(
                    rx.text("Última telemetria", size="1", color=TEXTO_SECUNDARIO),
                    rx.text(totem["ultima_telemetria_em_texto"], size="1", color=TEXTO),
                    align="start", spacing="1",
                ),
                rx.vstack(
                    rx.text("Última transição", size="1", color=TEXTO_SECUNDARIO),
                    rx.text(totem["ultima_transicao_disponibilidade_em_texto"], size="1", color=TEXTO),
                    align="start", spacing="1",
                ),
                columns="2", gap="0.75rem", width="100%", margin_top="0.25rem",
            ),
            width="100%", align="start", spacing="2",
        ),
        on_click=MonitoramentoState.selecionar_totem(totem["id"]),
        disabled=MonitoramentoState.carregando_detalhe, aria_pressed=selecionado,
        aria_label="Ver detalhes de " + totem["nome_ativo"] + ", " + totem["loja_nome"],
        variant="ghost", width="100%", height="auto", margin="0", padding="1rem",
        box_sizing="border-box",
        text_align="left", white_space="normal",
        color=rx.cond(selecionado, "var(--accent-11)", TEXTO),
        background=rx.cond(selecionado, "var(--accent-2)", "transparent"),
        border=rx.cond(selecionado, "1px solid var(--accent-6)", "1px solid transparent"),
        border_radius=RAIO_CONTROLE,
        _hover={"background": rx.cond(selecionado, "var(--accent-3)", CANVAS)},
        _focus_visible=FOCO_VISIVEL, class_name="mira-totem-option",
    )


def _lista_totens() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.heading("Totens", size="4", color=TEXTO),
            rx.text("Selecione para ver os detalhes.", size="2", color=TEXTO_SECUNDARIO),
            align="start", spacing="1", padding="1.25rem 1.25rem 0.75rem",
        ),
        rx.cond(
            MonitoramentoState.carregando,
            rx.center(rx.spinner(size="3"), width="100%", padding="3rem", aria_label="Carregando Totens"),
            rx.cond(
                MonitoramentoState.ativos.length() == 0,
                _vazio("monitor", "Nenhum Totem encontrado."),
                rx.vstack(
                    rx.foreach(MonitoramentoState.ativos, _opcao_totem),
                    width="100%", spacing="2", padding="0.5rem",
                    max_height="42rem", overflow_y="auto",
                    aria_label="Totens disponíveis", role="group", class_name="mira-totem-options",
                ),
            ),
        ),
        align="start", width="100%", spacing="0", background=SUPERFICIE,
        border=f"1px solid {BORDA}", border_radius=RAIO_SUPERFICIE, overflow="hidden",
    )


def _valor_telemetria(rotulo: str, valor, icone: str) -> rx.Component:
    return rx.vstack(
        rx.hstack(rx.icon(icone, size=16), rx.text(rotulo, size="2"),
                  color=TEXTO_SECUNDARIO, align="center", spacing="2"),
        rx.text(valor, size="6", weight="bold", color=TEXTO, class_name="mira-telemetry-value"),
        align="start", spacing="2", min_width="0",
    )


def _telemetria_atual() -> rx.Component:
    ultima = MonitoramentoState.detalhe_totem["ultima_telemetria"]
    return rx.vstack(
        rx.hstack(
            rx.heading("Última telemetria", size="3", color=TEXTO),
            rx.cond(
                MonitoramentoState.detalhe_totem["tem_ultima_telemetria"],
                rx.hstack(rx.icon("clock-3", size=14),
                          rx.text(ultima["evento_timestamp_texto"], size="1"),
                          align="center", spacing="2", color=TEXTO_SECUNDARIO),
            ),
            width="100%", justify="between", align="center", flex_wrap="wrap", gap="0.75rem",
        ),
        rx.cond(
            MonitoramentoState.detalhe_totem["tem_ultima_telemetria"],
            rx.vstack(
                rx.grid(
                    _valor_telemetria("CPU", ultima["uso_cpu"], "cpu"),
                    _valor_telemetria("Memória", ultima["uso_memoria"], "memory-stick"),
                    _valor_telemetria("Temperatura", ultima["temperatura"], "thermometer"),
                    columns="3", gap="1rem", width="100%",
                ),
                rx.hstack(
                    rx.icon("network", size=16, color=TEXTO_SECUNDARIO),
                    rx.text("Rede", size="2", color=TEXTO_SECUNDARIO),
                    badge_status(ultima["status_rede"]),
                    align="center", spacing="2", width="100%",
                    border_top=f"1px solid {BORDA}", padding_top="1rem",
                ),
                background=CANVAS, padding="1.25rem", border_radius="12px",
                width="100%", spacing="4", align="start",
            ),
            _vazio("activity", "Nenhuma telemetria registrada."),
        ),
        width="100%", align="start", spacing="3",
    )


def _historico_telemetrias() -> rx.Component:
    return rx.cond(
        MonitoramentoState.detalhe_totem["telemetrias"].length() > 0,
        rx.box(
            rx.table.root(
                rx.table.header(rx.table.row(
                    rx.table.column_header_cell("Data e hora"),
                    rx.table.column_header_cell("CPU"),
                    rx.table.column_header_cell("Memória"),
                    rx.table.column_header_cell("Temperatura"),
                    rx.table.column_header_cell("Rede"),
                    rx.table.column_header_cell("Loja na ocorrência"),
                )),
                rx.table.body(rx.foreach(
                    MonitoramentoState.detalhe_totem["telemetrias"],
                    lambda telemetria: rx.table.row(
                        rx.table.cell(telemetria["evento_timestamp_texto"]),
                        rx.table.cell(telemetria["uso_cpu"]),
                        rx.table.cell(telemetria["uso_memoria"]),
                        rx.table.cell(telemetria["temperatura"]),
                        rx.table.cell(badge_status(telemetria["status_rede"])),
                        rx.table.cell(telemetria["loja_nome"]),
                    ),
                )),
                width="100%",
            ),
            overflow_x="auto", width="100%", border=f"1px solid {BORDA}", border_radius="10px",
        ),
        _vazio("activity", "Nenhuma telemetria registrada."),
    )


def _transicoes() -> rx.Component:
    return rx.cond(
        MonitoramentoState.detalhe_totem["transicoes"].length() > 0,
        rx.vstack(
            rx.foreach(
                MonitoramentoState.detalhe_totem["transicoes"],
                lambda transicao: rx.hstack(
                    rx.center(
                        rx.cond(transicao["status"] == "online",
                                rx.icon("wifi", size=18, color="var(--green-11)"),
                                rx.icon("wifi-off", size=18, color="var(--red-11)")),
                        width="2.5rem", height="2.5rem", background=CANVAS,
                        border_radius="10px", flex_shrink="0",
                    ),
                    rx.vstack(
                        rx.hstack(
                            badge_status(transicao["status"]),
                            rx.text(transicao["detectado_em_texto"], size="2", color=TEXTO),
                            align="center", spacing="3", flex_wrap="wrap",
                        ),
                        rx.text(transicao["loja_nome"], size="2", color=TEXTO_SECUNDARIO),
                        rx.text("Limite de heartbeat: " + transicao["heartbeat_limite_minutos"],
                                size="1", color=TEXTO_SECUNDARIO),
                        align="start", spacing="2", min_width="0",
                    ),
                    align="start", spacing="3", width="100%", padding_y="1rem",
                    class_name="mira-availability-event",
                ),
            ),
            align="start", spacing="0", width="100%",
        ),
        _vazio("history", "Nenhuma transição de disponibilidade registrada."),
    )


def _incidentes() -> rx.Component:
    return rx.cond(
        MonitoramentoState.detalhe_totem["incidentes"].length() > 0,
        rx.vstack(
            rx.foreach(
                MonitoramentoState.detalhe_totem["incidentes"],
                lambda incidente: rx.vstack(
                    rx.hstack(
                        rx.link(
                            incidente["titulo"],
                            rx.icon("arrow-up-right", size=16, flex_shrink="0", aria_hidden=True),
                            href="/chamados/" + incidente["id"].to_string(),
                            display="inline-flex", align_items="center", gap="0.5rem",
                            size="2", weight="bold", min_width="0",
                        ),
                        badge_status(incidente["status"]),
                        align="start", justify="between", width="100%", gap="1rem", flex_wrap="wrap",
                    ),
                    rx.hstack(
                        rx.text("Prioridade: " + incidente["prioridade"], size="2", color=TEXTO_SECUNDARIO),
                        rx.text("Abertura: " + incidente["criado_em_texto"], size="2", color=TEXTO_SECUNDARIO),
                        spacing="4", flex_wrap="wrap", row_gap="0.5rem",
                    ),
                    width="100%", align="start", spacing="3", padding_y="1rem",
                    class_name="mira-heartbeat-incident",
                ),
            ),
            align="start", spacing="0", width="100%",
        ),
        _vazio("ticket", "Nenhum incidente automático de heartbeat registrado."),
    )


def _aba_historico(rotulo: str, valor: str, colecao: str) -> rx.Component:
    return rx.tabs.trigger(
        rotulo,
        rx.text(MonitoramentoState.detalhe_totem[colecao].length(), as_="span", class_name="mira-history-count"),
        value=valor, gap="0.5rem", padding_x="0.75rem",
    )


def _historicos() -> rx.Component:
    return rx.tabs.root(
        rx.tabs.list(
            _aba_historico("Telemetrias", "telemetrias", "telemetrias"),
            _aba_historico("Disponibilidade", "disponibilidade", "transicoes"),
            _aba_historico("Incidentes", "incidentes", "incidentes"),
            width="100%", aria_label="Históricos do Totem",
        ),
        rx.tabs.content(
            rx.vstack(
                rx.heading("Histórico recente de telemetrias", size="3", color=TEXTO),
                _historico_telemetrias(), align="start", spacing="4", width="100%",
            ),
            value="telemetrias", padding_top="1.5rem",
        ),
        rx.tabs.content(
            rx.vstack(
                rx.heading("Eventos de disponibilidade registrados", size="3", color=TEXTO),
                rx.text("Histórico das mudanças de disponibilidade.", size="2", color=TEXTO_SECUNDARIO),
                _transicoes(), align="start", spacing="2", width="100%",
            ),
            value="disponibilidade", padding_top="1.5rem",
        ),
        rx.tabs.content(
            rx.vstack(
                rx.heading("Incidentes automáticos de heartbeat", size="3", color=TEXTO),
                _incidentes(), align="start", spacing="3", width="100%",
            ),
            value="incidentes", padding_top="1.5rem",
        ),
        default_value="telemetrias", width="100%", class_name="mira-monitoring-history",
    )


def _painel_detalhe() -> rx.Component:
    return rx.vstack(
        rx.cond(
            MonitoramentoState.mensagem_erro_detalhe != "",
            rx.callout(MonitoramentoState.mensagem_erro_detalhe,
                       icon="triangle_alert", color_scheme="red", width="100%"),
        ),
        rx.cond(
            MonitoramentoState.carregando_detalhe,
            rx.center(rx.spinner(size="3"), width="100%", min_height="24rem", aria_label="Carregando detalhe do Totem"),
            rx.cond(
                MonitoramentoState.detalhe_carregado,
                rx.vstack(
                    rx.hstack(
                        rx.hstack(
                            rx.center(rx.icon("monitor", size=24), width="3rem", height="3rem",
                                      background=CANVAS, border_radius="12px", flex_shrink="0"),
                            rx.vstack(
                                rx.heading(MonitoramentoState.detalhe_totem["nome_ativo"], size="6", color=TEXTO),
                                rx.hstack(rx.icon("store", size=14),
                                          rx.text(MonitoramentoState.detalhe_totem["loja_nome"], size="2"),
                                          align="center", spacing="2", color=TEXTO_SECUNDARIO),
                                align="start", spacing="2", min_width="0",
                            ),
                            align="center", spacing="3", min_width="0",
                        ),
                        badge_status(MonitoramentoState.detalhe_totem["status_atual"]),
                        justify="between", align="center", width="100%", flex_wrap="wrap", gap="1rem",
                    ),
                    rx.separator(width="100%", color_scheme="gray"),
                    _telemetria_atual(), _historicos(),
                    align="start", width="100%", spacing="5",
                ),
                rx.center(
                    _vazio("monitor", "Selecione um Totem", "Consulte a última telemetria, os eventos de disponibilidade e os incidentes registrados."),
                    min_height="28rem", width="100%",
                ),
            ),
        ),
        align="start", width="100%", spacing="3", min_width="0", padding="1.5rem",
        background=SUPERFICIE, border=f"1px solid {BORDA}", border_radius=RAIO_SUPERFICIE,
        aria_busy=MonitoramentoState.carregando_detalhe, aria_label="Detalhe do Totem", role="region",
    )


def _conteudo() -> rx.Component:
    return rx.vstack(
        _cabecalho(), _resumo(),
        rx.cond(
            MonitoramentoState.mensagem_erro != "",
            rx.callout(MonitoramentoState.mensagem_erro, icon="triangle_alert", color_scheme="red", width="100%"),
        ),
        rx.box(_lista_totens(), _painel_detalhe(), display="grid", gap="1.5rem",
               width="100%", align_items="start", class_name="mira-monitoring-grid"),
        width="100%", spacing="5", class_name="mira-monitoring",
    )


def _protegida() -> rx.Component:
    return rx.cond(
        AuthState.carregando, estado_carregamento(),
        rx.cond(AuthState.sessao_confirmada, casca_conteudo(_conteudo(), "/inicio"),
                estado_revalidacao(MonitoramentoState.carregar)),
    )


def monitoramento() -> rx.Component:
    return _protegida()
