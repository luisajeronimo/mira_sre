"""Dashboard de disponibilidade e confiabilidade da Diretoria."""

import reflex as rx

from app.components.layout import casca_conteudo, estado_carregamento
from app.components.visual import (
    BORDA,
    RAIO_CONTROLE,
    RAIO_SUPERFICIE,
    SOMBRA_BAIXA,
    SUPERFICIE,
    SUPERFICIE_SUAVE,
    TEXTO,
    TEXTO_SECUNDARIO,
    seletor_periodo_calendario,
)
from app.indicadores.paineis_causas import painel_causas
from app.indicadores.state import IndicadoresDiretoriaState
from app.states.auth import AuthState


AZUL_DETECCAO = "#2563EB"
ROSE_RECUPERACAO = "#E11D48"


def _campo_opcoes(rotulo: str, opcoes, valor, evento) -> rx.Component:
    return rx.vstack(
        rx.text(rotulo, size="2", weight="medium", color=TEXTO),
        rx.select.root(
            rx.select.trigger(width="100%", aria_label=rotulo),
            rx.select.content(
                rx.foreach(
                    opcoes,
                    lambda opcao: rx.select.item(opcao["label"], value=opcao["value"]),
                )
            ),
            value=valor,
            on_change=evento,
            width="100%",
        ),
        align="start",
        spacing="1",
        width="100%",
    )


def _botao_periodo(rotulo: str, periodo: str, evento=None) -> rx.Component:
    ativo = IndicadoresDiretoriaState.periodo_rapido == periodo
    return rx.button(
        rotulo,
        on_click=evento,
        aria_pressed=ativo,
        variant="ghost",
        background=rx.cond(ativo, "var(--accent-9)", "transparent"),
        color=rx.cond(ativo, "white", TEXTO),
        _hover={
            "background": rx.cond(ativo, "var(--accent-9)", "transparent"),
            "color": rx.cond(ativo, "white", TEXTO),
            "box_shadow": "none",
        },
        _active={"background": rx.cond(ativo, "var(--accent-9)", "transparent")},
        disabled=IndicadoresDiretoriaState.carregando_indicadores,
        width="100%",
        height="2.5rem",
        padding="0.375rem",
        border_radius="0.5rem",
        font_size="0.75rem",
        font_weight="600",
        white_space="normal",
        text_align="center",
        line_height="1.15",
        cursor="pointer",
    )


def _seletor_periodo() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(
                _botao_periodo(
                    "Últimos 30 dias",
                    "30_dias",
                    lambda: IndicadoresDiretoriaState.selecionar_periodo_rapido("30_dias"),
                ),
                flex="1",
                min_width="0",
            ),
            rx.box(
                _botao_periodo(
                    "Hoje",
                    "hoje",
                    lambda: IndicadoresDiretoriaState.selecionar_periodo_rapido("hoje"),
                ),
                flex="1",
                min_width="0",
            ),
            rx.box(
                _botao_periodo(
                    "Personalizado",
                    "personalizado",
                    IndicadoresDiretoriaState.alternar_periodo_personalizado,
                ),
                flex="1",
                min_width="0",
            ),
            role="group",
            aria_label="Período dos indicadores",
            spacing="1",
            padding="0.25rem",
            width="100%",
            background=SUPERFICIE,
            border=f"1px solid {BORDA}",
            border_radius=RAIO_CONTROLE,
            align="center",
        ),
        rx.cond(
            IndicadoresDiretoriaState.mostrar_periodo_personalizado,
            rx.fragment(
                rx.box(
                    position="fixed",
                    inset="0",
                    z_index="20",
                    on_click=IndicadoresDiretoriaState.alternar_periodo_personalizado,
                    aria_hidden="true",
                ),
                _periodo_personalizado(),
            ),
            rx.fragment(),
        ),
        position="relative",
        width="22rem",
        max_width="100%",
        flex_shrink="0",
    )


def _periodo_personalizado() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.text("Período personalizado", size="2", weight="bold", color=TEXTO),
            seletor_periodo_calendario(
                inicio=IndicadoresDiretoriaState.data_inicio,
                fim=IndicadoresDiretoriaState.data_fim,
                rotulo="indicadores",
                on_change=IndicadoresDiretoriaState.alterar_periodo_personalizado,
                disabled=IndicadoresDiretoriaState.carregando_indicadores,
            ),
            rx.button(
                "Aplicar período",
                on_click=IndicadoresDiretoriaState.aplicar_filtros,
                disabled=IndicadoresDiretoriaState.carregando_indicadores,
                color_scheme="ruby",
                width="100%",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        position="absolute",
        top="calc(100% + 0.5rem)",
        right="0",
        z_index="21",
        width="22rem",
        max_width="100%",
        padding="1rem",
        background=SUPERFICIE,
        border=f"1px solid {BORDA}",
        border_radius=RAIO_SUPERFICIE,
        box_shadow=SOMBRA_BAIXA,
    )


def _cabecalho(aba: str) -> rx.Component:
    disponibilidade = aba == "disponibilidade"
    return rx.hstack(
        rx.vstack(
            rx.heading("Causas e recorrência" if aba == "causas" else "Disponibilidade" if disponibilidade else "Chamados e SLA", size="7", color=TEXTO),
            rx.text(
                "Tempo observado, detecção e recuperação dos Totens."
                if disponibilidade else "Concentração de incidentes, principais Categorias e repetição de chamados." if aba == "causas" else "Volume por status, conformidade do período e risco atual.",
                size="2",
                color=TEXTO_SECUNDARIO,
            ),
            spacing="1",
            align="start",
            min_width="0",
        ),
        _seletor_periodo(),
        align="center",
        justify="between",
        flex_wrap="wrap",
        column_gap="1.5rem",
        row_gap="1rem",
        width="100%",
    )


def _filtros(aba: str) -> rx.Component:
    disponibilidade = aba == "disponibilidade"
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("sliders_horizontal", size=17, color="var(--accent-10)"),
                rx.text("Filtros de causas e recorrência" if aba == "causas" else "Filtros de disponibilidade" if disponibilidade else "Filtros de chamados e SLA", size="2", weight="bold", color=TEXTO),
                align="center",
                width="100%",
            ),
            rx.box(
                rx.grid(
                    _campo_opcoes("Loja histórica", IndicadoresDiretoriaState.lojas_opcoes, IndicadoresDiretoriaState.loja_id, IndicadoresDiretoriaState.alterar_loja),
                    _campo_opcoes(
                        "Totem" if disponibilidade else "Categoria",
                        IndicadoresDiretoriaState.totens_opcoes if disponibilidade else IndicadoresDiretoriaState.categorias_opcoes,
                        IndicadoresDiretoriaState.totem_id if disponibilidade else IndicadoresDiretoriaState.categoria_id,
                        IndicadoresDiretoriaState.alterar_totem if disponibilidade else IndicadoresDiretoriaState.alterar_categoria,
                    ),
                    *([_campo_opcoes("Totem", IndicadoresDiretoriaState.totens_opcoes, IndicadoresDiretoriaState.totem_id, IndicadoresDiretoriaState.alterar_totem)] if aba == "causas" else []),
                    rx.button(
                        "Aplicar filtros",
                        on_click=IndicadoresDiretoriaState.aplicar_filtros,
                        disabled=IndicadoresDiretoriaState.carregando_indicadores,
                        color_scheme="ruby",
                        align_self="end",
                    ),
                    grid_template_columns="repeat(3, minmax(0, 1fr)) auto" if aba == "causas" else "repeat(2, minmax(0, 1fr)) auto",
                    gap="0.75rem",
                    align_items="end",
                    min_width="35rem",
                    width="100%",
                ),
                overflow_x="auto",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        width="100%",
        padding="1rem 1.25rem",
        background=SUPERFICIE,
        border=f"1px solid {BORDA}",
        border_radius=RAIO_SUPERFICIE,
        box_shadow=SOMBRA_BAIXA,
    )


def _cartao_indicador(rotulo: str, valor, explicacao: str, detalhe, cor: str, complemento=None) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text(rotulo, size="2", weight="bold", color=cor),
            rx.heading(
                valor,
                color=TEXTO,
                font_size="2.25rem",
                line_height="1.1",
                font_variant_numeric="tabular-nums",
            ),
            rx.text(explicacao, size="2", color=TEXTO_SECUNDARIO),
            rx.spacer(),
            rx.box(
                rx.vstack(
                    rx.text(detalhe, size="1", weight="medium", color=TEXTO),
                    *([rx.text(complemento, size="1", color=TEXTO_SECUNDARIO)] if complemento is not None else []),
                    spacing="1",
                    align="start",
                ),
                border_top=f"1px solid {BORDA}",
                padding_top="0.75rem",
                width="100%",
            ),
            width="100%",
            min_height="10.5rem",
            height="100%",
            align="start",
            spacing="3",
        ),
        width="100%",
        height="100%",
        min_width="0",
        min_height="13rem",
        padding="1.25rem",
        background=SUPERFICIE,
        border=f"1px solid {BORDA}",
        border_radius=RAIO_SUPERFICIE,
        class_name="mira-metric",
    )


def _legenda(cor: str, sigla: str, significado: str) -> rx.Component:
    return rx.hstack(
        rx.box(
            width="1.25rem",
            height="0.75rem",
            border_top=f"3px solid {cor}",
            background=f"color-mix(in srgb, {cor} 14%, transparent)",
            border_radius="0.125rem",
            flex_shrink="0",
        ),
        rx.text(sigla, size="2", weight="bold", color=TEXTO),
        rx.text(significado, size="2", color=TEXTO_SECUNDARIO),
        spacing="2",
        align="center",
        min_width="0",
    )


def _tooltip_grafico() -> rx.Component:
    return rx.recharts.graphing_tooltip(
        allow_escape_view_box={"x": False, "y": False},
        is_animation_active=False,
        offset=8,
        wrapper_style={"pointerEvents": "none", "zIndex": 2},
        content_style={
            "backgroundColor": "#FFFFFF",
            "border": f"1px solid {BORDA}",
            "borderRadius": "0.625rem",
            "boxShadow": "0 8px 24px rgba(15, 23, 42, 0.12)",
            "padding": "0.5rem 0.75rem",
        },
        label_style={"color": TEXTO, "fontWeight": 700},
        item_style={"fontSize": "0.75rem", "padding": "0.125rem 0"},
    )


def _grafico() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.vstack(
                rx.heading(
                    rx.cond(
                        IndicadoresDiretoriaState.serie.length() == 1,
                        "Detecção e recuperação no dia",
                        "Detecção e recuperação ao longo dos dias",
                    ),
                    size="5",
                    color=TEXTO,
                ),
                rx.text("Tempo médio em horas por dia. Dias sem eventos ficam sem ponto.", size="2", color=TEXTO_SECUNDARIO),
                rx.hstack(
                    _legenda(AZUL_DETECCAO, "MTTD", "tempo até detectar"),
                    _legenda(ROSE_RECUPERACAO, "MTTR", "tempo até recuperar"),
                    spacing="5",
                    flex_wrap="wrap",
                    row_gap="0.5rem",
                    align="center",
                    width="100%",
                ),
                spacing="2",
                align="start",
                width="100%",
            ),
            rx.box(
                rx.recharts.area_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                    rx.recharts.x_axis(data_key="dia", min_tick_gap=36, tick_line=False, axis_line=False),
                    rx.recharts.y_axis(unit=" h", width=56, tick_line=False, axis_line=False),
                    _tooltip_grafico(),
                    rx.recharts.area(
                        data_key="mttd_horas",
                        name="MTTD · Detecção",
                        unit=" h",
                        type_="monotone",
                        stroke=AZUL_DETECCAO,
                        stroke_width=2.5,
                        fill="rgba(37, 99, 235, 0.12)",
                        connect_nulls=False,
                        dot={"r": 3, "fill": "#FFFFFF", "strokeWidth": 2},
                        active_dot={"r": 5},
                    ),
                    rx.recharts.area(
                        data_key="mttr_horas",
                        name="MTTR · Recuperação",
                        unit=" h",
                        type_="monotone",
                        stroke=ROSE_RECUPERACAO,
                        stroke_width=2.5,
                        fill="rgba(225, 29, 72, 0.12)",
                        connect_nulls=False,
                        dot={"r": 3, "fill": "#FFFFFF", "strokeWidth": 2},
                        active_dot={"r": 5},
                    ),
                    data=IndicadoresDiretoriaState.serie,
                    width="100%",
                    height=320,
                    margin={"top": 16, "right": 16, "bottom": 16, "left": 4},
                ),
                width="100%",
                min_width="0",
                overflow="hidden",
            ),
            width="100%",
            align="start",
            spacing="5",
        ),
        width="100%",
        min_width="0",
        padding="1.5rem",
        background=SUPERFICIE,
        border=f"1px solid {BORDA}",
        border_radius=RAIO_SUPERFICIE,
    )


def _grafico_horario() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.vstack(
                rx.heading("Disponibilidade da rede ao longo do dia", size="5", color=TEXTO),
                rx.text(
                    "Cada ponto considera o tempo observado naquela hora. Horas futuras ficam sem valor.",
                    size="2",
                    color=TEXTO_SECUNDARIO,
                ),
                align="start",
                spacing="1",
                width="100%",
            ),
            rx.box(
                rx.recharts.area_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                    rx.recharts.x_axis(
                        data_key="hora",
                        ticks=["00h", "04h", "08h", "12h", "16h", "20h", "23h"],
                        interval=0,
                        tick_line=False,
                        axis_line=False,
                    ),
                    rx.recharts.y_axis(domain=[0, 100], unit="%", width=48, tick_line=False, axis_line=False),
                    _tooltip_grafico(),
                    rx.recharts.area(
                        data_key="percentual",
                        name="Disponibilidade (%)",
                        stroke="var(--accent-9)",
                        stroke_width=2.5,
                        fill="rgba(225, 29, 72, 0.12)",
                        type_="monotone",
                        connect_nulls=False,
                        dot=True,
                        active_dot=True,
                    ),
                    data=IndicadoresDiretoriaState.serie_horaria,
                    width="100%",
                    height=300,
                    margin={"top": 12, "right": 28, "bottom": 8, "left": 4},
                ),
                width="100%",
                min_width="0",
                overflow="hidden",
            ),
            width="100%",
            min_width="0",
            align="start",
            spacing="4",
        ),
        width="100%",
        min_width="0",
        padding="1.5rem",
        background=SUPERFICIE,
        border=f"1px solid {BORDA}",
        border_radius=RAIO_SUPERFICIE,
    )


def _faixa_risco(rotulo: str, limite: str, cor: str, quantidade) -> rx.Component:
    return rx.hstack(
        rx.box(width="0.25rem", align_self="stretch", border_radius="1rem", background=cor, flex_shrink="0"),
        rx.vstack(
            rx.text(rotulo, size="2", weight="bold", color=TEXTO),
            rx.text(limite, size="1", color=TEXTO_SECUNDARIO),
            align="start",
            spacing="0",
        ),
        rx.spacer(),
        rx.text(quantidade, size="5", weight="bold", color=TEXTO),
        align="center",
        spacing="3",
        width="100%",
        min_height="4.25rem",
        padding="0.75rem",
        border=f"1px solid {BORDA}",
        border_radius=RAIO_CONTROLE,
        background=SUPERFICIE,
    )


def _painel_operacao() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.text(IndicadoresDiretoriaState.operacao_periodo_texto, size="2", color=TEXTO_SECUNDARIO),
            align="start",
            spacing="1",
            width="100%",
        ),
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.text("VOLUME DE CHAMADOS", size="1", weight="bold", color=TEXTO_SECUNDARIO, letter_spacing="0.08em"),
                    rx.hstack(
                        rx.heading(IndicadoresDiretoriaState.volume_total, size="8", color=TEXTO),
                        rx.text("abertos no período", size="2", color=TEXTO_SECUNDARIO),
                        spacing="3",
                        align="baseline",
                        flex_wrap="wrap",
                    ),
                    rx.text("Distribuídos pelo status atual no painel abaixo.", size="2", color=TEXTO_SECUNDARIO),
                    align="start",
                    spacing="2",
                    width="100%",
                ),
                width="100%",
                height="100%",
                padding="1.5rem",
                border=f"1px solid {BORDA}",
                border_radius=RAIO_SUPERFICIE,
                background=SUPERFICIE,
                box_shadow=SOMBRA_BAIXA,
            ),
            rx.card(
                rx.vstack(
                    rx.text("CONFORMIDADE DE SLA", size="1", weight="bold", color=TEXTO_SECUNDARIO, letter_spacing="0.08em"),
                    rx.hstack(
                        rx.heading(IndicadoresDiretoriaState.conformidade_texto, size="8", color=TEXTO),
                        rx.text("no período", size="2", color=TEXTO_SECUNDARIO),
                        spacing="3",
                        align="baseline",
                        flex_wrap="wrap",
                    ),
                    rx.text(
                        IndicadoresDiretoriaState.conformidade_cumpriram.to_string() + " de " + IndicadoresDiretoriaState.conformidade_elegiveis.to_string() + " chamados elegíveis dentro do SLA",
                        size="2",
                        color=TEXTO,
                    ),
                    rx.cond(
                        IndicadoresDiretoriaState.conformidade_elegiveis > 0,
                        rx.box(
                            rx.box(width=IndicadoresDiretoriaState.conformidade_progresso, height="100%", background="var(--accent-9)", border_radius="1rem"),
                            width="100%",
                            height="0.5rem",
                            background=SUPERFICIE_SUAVE,
                            border_radius="1rem",
                            overflow="hidden",
                        ),
                        rx.text("Sem chamados elegíveis neste recorte.", size="2", color=TEXTO_SECUNDARIO),
                    ),
                    rx.text(
                        IndicadoresDiretoriaState.conformidade_cancelados.to_string() + " cancelados · " + IndicadoresDiretoriaState.conformidade_nao_calculaveis.to_string() + " não calculáveis",
                        size="1",
                        color=TEXTO_SECUNDARIO,
                    ),
                    align="start",
                    spacing="2",
                    width="100%",
                ),
                width="100%",
                height="100%",
                padding="1.5rem",
                border=f"1px solid {BORDA}",
                border_radius=RAIO_SUPERFICIE,
                background=SUPERFICIE,
                box_shadow=SOMBRA_BAIXA,
            ),
            columns={"initial": "1", "lg": "2"},
            spacing="4",
            width="100%",
            align="stretch",
        ),
        rx.grid(
            rx.card(
                rx.vstack(
                    rx.heading("Status dos chamados", size="5", color=TEXTO),
                    rx.text("Chamados abertos no período, agrupados pelo status atual.", size="2", color=TEXTO_SECUNDARIO),
                    rx.cond(
                        IndicadoresDiretoriaState.volume_total > 0,
                        rx.flex(
                            rx.box(
                                rx.recharts.pie_chart(
                                    rx.recharts.pie(
                                        rx.foreach(
                                            IndicadoresDiretoriaState.volume_status_grafico,
                                            lambda item: rx.recharts.cell(fill=item["fill"]),
                                        ),
                                        data=IndicadoresDiretoriaState.volume_status_grafico,
                                        data_key="quantidade",
                                        name_key="rotulo",
                                        inner_radius=68,
                                        outer_radius=104,
                                        padding_angle=2,
                                        stroke=SUPERFICIE,
                                        is_animation_active=False,
                                    ),
                                    width="100%",
                                    height=240,
                                ),
                                rx.center(
                                    rx.vstack(
                                        rx.text(IndicadoresDiretoriaState.volume_total, size="6", weight="bold", color=TEXTO),
                                        rx.text("chamados", size="1", color=TEXTO_SECUNDARIO),
                                        align="center",
                                        spacing="0",
                                    ),
                                    position="absolute",
                                    inset="0",
                                    pointer_events="none",
                                ),
                                position="relative",
                                width="15rem",
                                height="15rem",
                                flex_shrink="0",
                                overflow="hidden",
                            ),
                            rx.vstack(
                                rx.foreach(
                                    IndicadoresDiretoriaState.volume_status_grafico,
                                    lambda item: rx.hstack(
                                        rx.box(width="0.625rem", height="0.625rem", border_radius="50%", background=item["fill"], flex_shrink="0"),
                                        rx.text(item["rotulo"], size="2", color=TEXTO, min_width="0"),
                                        rx.spacer(),
                                        rx.text(item["quantidade"], size="2", weight="bold", color=TEXTO),
                                        align="center",
                                        spacing="2",
                                        width="100%",
                                    ),
                                ),
                                align="start",
                                spacing="2",
                                min_width="12rem",
                                flex="1",
                            ),
                            align="center",
                            justify="center",
                            gap="1rem",
                            flex_wrap="wrap",
                            width="100%",
                        ),
                        rx.center(rx.text("Nenhum chamado aberto neste recorte.", size="2", color=TEXTO_SECUNDARIO), min_height="15rem", width="100%"),
                    ),
                    align="start",
                    spacing="3",
                    width="100%",
                ),
                width="100%",
                height="100%",
                padding="1.5rem",
                border=f"1px solid {BORDA}",
                border_radius=RAIO_SUPERFICIE,
                background=SUPERFICIE,
                box_shadow=SOMBRA_BAIXA,
            ),
            rx.card(
                rx.vstack(
                    rx.heading("Termômetro de SLA", size="5", color=TEXTO),
                    rx.text("Risco atual · retrato em " + IndicadoresDiretoriaState.risco_instante_texto, size="2", color=TEXTO_SECUNDARIO),
                    rx.text("Considera todos os chamados ainda em contagem, inclusive os anteriores ao período.", size="2", color=TEXTO_SECUNDARIO),
                    rx.grid(
                        _faixa_risco("Normal", "< 70%", "#10B981", IndicadoresDiretoriaState.risco_faixas[0]["quantidade"]),
                        _faixa_risco("Risco", "70–90%", "#F59E0B", IndicadoresDiretoriaState.risco_faixas[1]["quantidade"]),
                        _faixa_risco("Crítico", "> 90–100%", "#F97316", IndicadoresDiretoriaState.risco_faixas[2]["quantidade"]),
                        _faixa_risco("Violado", "> 100%", "#E11D48", IndicadoresDiretoriaState.risco_faixas[3]["quantidade"]),
                        columns={"initial": "1", "sm": "2"},
                        spacing="2",
                        width="100%",
                    ),
                    rx.cond(
                        IndicadoresDiretoriaState.risco_sem_dados,
                        rx.text("Nenhum chamado em contagem neste recorte.", size="2", color=TEXTO_SECUNDARIO),
                        rx.fragment(),
                    ),
                    rx.text(
                        IndicadoresDiretoriaState.risco_nao_calculaveis.to_string() + " não calculáveis · " + IndicadoresDiretoriaState.risco_status_nao_canonicos.to_string() + " com status não canônico",
                        size="1",
                        color=TEXTO_SECUNDARIO,
                    ),
                    align="start",
                    spacing="3",
                    width="100%",
                ),
                width="100%",
                height="100%",
                padding="1.5rem",
                border=f"1px solid {BORDA}",
                border_radius=RAIO_SUPERFICIE,
                background=SUPERFICIE,
                box_shadow=SOMBRA_BAIXA,
            ),
            columns={"initial": "1", "lg": "2"},
            spacing="4",
            width="100%",
            align="stretch",
        ),
        align="start",
        spacing="4",
        width="100%",
    )


def _tabela_diaria() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading("Histórico por data", size="5", color=TEXTO),
                    rx.text("Médias em horas, da data mais recente à mais antiga.", size="2", color=TEXTO_SECUNDARIO),
                    align="start",
                    spacing="1",
                ),
                rx.spacer(),
                rx.badge(
                    IndicadoresDiretoriaState.serie_tabela.length().to_string() + " datas",
                    variant="soft",
                    color_scheme="gray",
                    size="2",
                ),
                align="start",
                width="100%",
            ),
            rx.cond(
                IndicadoresDiretoriaState.serie_tabela.length() > 0,
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("DATA", color=TEXTO_SECUNDARIO, font_size="0.6875rem", letter_spacing="0.06em", font_weight="700"),
                                rx.table.column_header_cell("MTTD · DETECÇÃO", color=TEXTO_SECUNDARIO, font_size="0.6875rem", letter_spacing="0.06em", font_weight="700"),
                                rx.table.column_header_cell("EVENTOS", color=TEXTO_SECUNDARIO, font_size="0.6875rem", letter_spacing="0.06em", font_weight="700"),
                                rx.table.column_header_cell("MTTR · RECUPERAÇÃO", color=TEXTO_SECUNDARIO, font_size="0.6875rem", letter_spacing="0.06em", font_weight="700"),
                                rx.table.column_header_cell("RETORNOS", color=TEXTO_SECUNDARIO, font_size="0.6875rem", letter_spacing="0.06em", font_weight="700"),
                            ),
                            background="#FAF9FC",
                        ),
                        rx.table.body(
                            rx.foreach(
                                IndicadoresDiretoriaState.serie_tabela,
                                lambda ponto: rx.table.row(
                                    rx.table.cell(rx.text(ponto["dia_texto"], weight="bold", color=TEXTO, white_space="nowrap")),
                                    rx.table.cell(
                                        rx.text(
                                            rx.cond(ponto["mttd_horas"] == None, "Sem média", ponto["mttd_horas_texto"]),
                                            weight="bold",
                                            color=rx.cond(ponto["mttd_horas"] == None, TEXTO_SECUNDARIO, AZUL_DETECCAO),
                                            white_space="nowrap",
                                        )
                                    ),
                                    rx.table.cell(
                                        rx.vstack(
                                            rx.text(ponto["mttd_eventos_texto"], size="2", color=TEXTO),
                                            rx.cond(
                                                ponto["mttd_inconsistentes"] > 0,
                                                rx.badge(ponto["mttd_inconsistencias_texto"], color_scheme="amber", variant="soft", size="1"),
                                                rx.fragment(),
                                            ),
                                            align="start",
                                            spacing="1",
                                        )
                                    ),
                                    rx.table.cell(
                                        rx.text(
                                            rx.cond(ponto["mttr_horas"] == None, "Sem média", ponto["mttr_horas_texto"]),
                                            weight="bold",
                                            color=rx.cond(ponto["mttr_horas"] == None, TEXTO_SECUNDARIO, ROSE_RECUPERACAO),
                                            white_space="nowrap",
                                        )
                                    ),
                                    rx.table.cell(
                                        rx.vstack(
                                            rx.text(ponto["mttr_recuperacoes_texto"], size="2", color=TEXTO),
                                            rx.cond(
                                                ponto["mttr_inconsistentes"] > 0,
                                                rx.badge(ponto["mttr_inconsistencias_texto"], color_scheme="amber", variant="soft", size="1"),
                                                rx.fragment(),
                                            ),
                                            align="start",
                                            spacing="1",
                                        )
                                    ),
                                    _hover={"background": "#FAF9FC"},
                                    border_bottom=f"1px solid {BORDA}",
                                    height="4.25rem",
                                ),
                            )
                        ),
                        width="100%",
                        min_width="42rem",
                    ),
                    width="100%",
                    overflow_x="auto",
                    border=f"1px solid {BORDA}",
                    border_radius=RAIO_CONTROLE,
                ),
                rx.center(
                    rx.text("Sem registros diários neste recorte.", size="2", color=TEXTO_SECUNDARIO),
                    min_height="8rem",
                    width="100%",
                    border=f"1px solid {BORDA}",
                    border_radius=RAIO_CONTROLE,
                ),
            ),
            width="100%",
            align="start",
            spacing="4",
        ),
        width="100%",
        padding="1.5rem",
        background=SUPERFICIE,
        border=f"1px solid {BORDA}",
        border_radius=RAIO_SUPERFICIE,
        box_shadow=SOMBRA_BAIXA,
    )


def indicadores_disponibilidade() -> rx.Component:
    conteudo = rx.vstack(
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Disponibilidade", value="disponibilidade", color_scheme="ruby"),
                rx.tabs.trigger("Chamados e SLA", value="operacao", color_scheme="ruby"),
                rx.tabs.trigger("Causas e recorrência", value="causas", color_scheme="ruby"),
                size="2",
                width="100%",
                border_bottom=f"1px solid {BORDA}",
            ),
            rx.tabs.content(
                rx.vstack(
                    _cabecalho("disponibilidade"),
                    _filtros("disponibilidade"),
                    rx.cond(
                        IndicadoresDiretoriaState.mensagem_erro_indicadores != "",
                        rx.callout(IndicadoresDiretoriaState.mensagem_erro_indicadores, icon="triangle_alert", color_scheme="red", width="100%"),
                        rx.fragment(),
                    ),
                    rx.cond(
                        IndicadoresDiretoriaState.carregando_indicadores,
                        rx.center(rx.spinner(size="3"), width="100%", padding="3rem"),
                        rx.fragment(),
                    ),
                    rx.cond(
                        IndicadoresDiretoriaState.tem_resultado,
                        rx.vstack(
                            rx.hstack(
                                rx.vstack(
                                    rx.heading("Resumo do período", size="5", color=TEXTO),
                                    rx.text(IndicadoresDiretoriaState.periodo_texto, size="2", color=TEXTO_SECUNDARIO),
                                    align="start",
                                    spacing="1",
                                ),
                                width="100%",
                            ),
                            rx.grid(
                                _cartao_indicador(
                                    "Disponibilidade da rede",
                                    IndicadoresDiretoriaState.disponibilidade_texto,
                                    "Quanto do tempo observado a rede permaneceu disponível.",
                                    IndicadoresDiretoriaState.disponibilidade_tempo,
                                    "#64748B",
                                    IndicadoresDiretoriaState.disponibilidade_detalhe,
                                ),
                                _cartao_indicador(
                                    "MTTD · Detecção",
                                    IndicadoresDiretoriaState.mttd_texto,
                                    "Tempo médio para detectar a indisponibilidade após a última telemetria.",
                                    IndicadoresDiretoriaState.mttd_detalhe,
                                    AZUL_DETECCAO,
                                ),
                                _cartao_indicador(
                                    "MTTR · Recuperação",
                                    IndicadoresDiretoriaState.mttr_texto,
                                    "Tempo médio que o Totem ficou indisponível antes de voltar Online.",
                                    IndicadoresDiretoriaState.mttr_detalhe,
                                    ROSE_RECUPERACAO,
                                ),
                                columns="3",
                                spacing="4",
                                width="100%",
                            ),
                            rx.text(
                                "MTTD mede a detecção; MTTR mede o retorno do Totem. O fechamento do chamado não altera o MTTR.",
                                size="2",
                                color=TEXTO_SECUNDARIO,
                            ),
                            rx.cond(
                                IndicadoresDiretoriaState.disponibilidade_aviso != "",
                                rx.callout(IndicadoresDiretoriaState.disponibilidade_aviso, icon="triangle_alert", color_scheme="amber", width="100%"),
                                rx.fragment(),
                            ),
                            rx.cond(IndicadoresDiretoriaState.serie_horaria.length() > 0, _grafico_horario(), _grafico()),
                            _tabela_diaria(),
                            spacing="4",
                            align="start",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    spacing="4",
                    align="start",
                    width="100%",
                ),
                value="disponibilidade",
                width="100%",
                padding_top="1rem",
            ),
            rx.tabs.content(
                rx.vstack(
                    _cabecalho("operacao"),
                    _filtros("operacao"),
                    rx.cond(
                        IndicadoresDiretoriaState.mensagem_erro_operacao != "",
                        rx.callout(IndicadoresDiretoriaState.mensagem_erro_operacao, icon="triangle_alert", color_scheme="red", width="100%"),
                        rx.fragment(),
                    ),
                    rx.cond(
                        IndicadoresDiretoriaState.carregando_indicadores,
                        rx.center(rx.spinner(size="3"), width="100%", padding="3rem"),
                        rx.fragment(),
                    ),
                    rx.cond(IndicadoresDiretoriaState.tem_operacao, _painel_operacao(), rx.fragment()),
                    spacing="4",
                    align="start",
                    width="100%",
                ),
                value="operacao",
                width="100%",
                padding_top="1rem",
            ),
            rx.tabs.content(
                rx.vstack(
                    _cabecalho("causas"),
                    _filtros("causas"),
                    rx.cond(
                        IndicadoresDiretoriaState.mensagem_erro_causas != "",
                        rx.callout(IndicadoresDiretoriaState.mensagem_erro_causas, icon="triangle_alert", color_scheme="red", width="100%"),
                        rx.fragment(),
                    ),
                    rx.cond(
                        IndicadoresDiretoriaState.carregando_indicadores,
                        rx.center(rx.spinner(size="3"), width="100%", padding="3rem"),
                        rx.fragment(),
                    ),
                    rx.cond(IndicadoresDiretoriaState.tem_causas, painel_causas(), rx.fragment()),
                    spacing="4", align="start", width="100%",
                ),
                value="causas", width="100%", padding_top="1rem",
            ),
            value=IndicadoresDiretoriaState.aba_ativa,
            on_change=IndicadoresDiretoriaState.selecionar_aba,
            width="100%",
        ),
        spacing="5",
        align="start",
        width="100%",
    )
    return rx.cond(
        AuthState.carregando,
        estado_carregamento(),
        rx.cond(
            AuthState.sessao_confirmada & AuthState.perfil_operacional & ~AuthState.deve_trocar_senha,
            casca_conteudo(conteudo),
            estado_carregamento(),
        ),
    )
