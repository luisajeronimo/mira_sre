"""Painéis de causas e recorrência: apresentação de agregados do backend."""

import reflex as rx

from app.components.visual import BORDA, RAIO_SUPERFICIE, SUPERFICIE, TEXTO, TEXTO_SECUNDARIO
from app.indicadores.state import IndicadoresDiretoriaState as Estado


def _painel(*filhos) -> rx.Component:
    return rx.box(
        rx.vstack(*filhos, align="start", spacing="4", width="100%"),
        padding="1.5rem", background=SUPERFICIE, border=f"1px solid {BORDA}",
        border_radius=RAIO_SUPERFICIE, width="100%", min_width="0",
    )


def _vazio(texto: str) -> rx.Component:
    return rx.center(rx.text(texto, size="2", color=TEXTO_SECUNDARIO), min_height="8rem", width="100%")


def _top_lojas() -> rx.Component:
    return _painel(
        rx.heading("Top 5 Lojas por incidentes", size="5", color=TEXTO),
        rx.cond(
            Estado.causas_top_lojas.length() > 0,
            rx.vstack(
                rx.foreach(Estado.causas_top_lojas, lambda loja, indice: rx.hstack(
                    rx.text((indice + 1).to_string(), size="2", color=TEXTO_SECUNDARIO, width="1.5rem"),
                    rx.text(loja["nome"], size="2", color=TEXTO, flex="1", overflow_wrap="anywhere"),
                    rx.text(loja["quantidade"].to_string(), weight="bold", color=TEXTO, font_variant_numeric="tabular-nums"),
                    align="center", role="listitem", width="100%", padding_y="0.75rem", border_bottom=f"1px solid {BORDA}",
                )), spacing="0", width="100%", role="list", aria_label="Ranking de Lojas por incidentes",
            ),
            _vazio("Nenhuma Loja com incidentes neste recorte."),
        ),
    )


def _tabela_recorrencia(linhas, unidade: str) -> rx.Component:
    return rx.cond(
        linhas.length() > 0,
        rx.box(
            rx.table.root(
                rx.table.header(rx.table.row(
                    rx.table.column_header_cell(unidade), rx.table.column_header_cell("Elegíveis"),
                    rx.table.column_header_cell("Recorrentes"), rx.table.column_header_cell("Taxa"),
                )),
                rx.table.body(rx.foreach(linhas, lambda linha: rx.table.row(
                    rx.table.row_header_cell(linha["nome"]),
                    rx.table.cell(linha["elegiveis"]), rx.table.cell(linha["recorrentes"]),
                    rx.table.cell(linha["percentual_texto"], white_space="nowrap"),
                ))), width="100%", size="2",
            ), overflow_x="auto", width="100%",
        ),
        _vazio("Nenhum incidente neste recorte."),
    )


def _recorrencia() -> rx.Component:
    return _painel(
        rx.heading("Recorrência em 30 dias", size="5", color=TEXTO),
        rx.hstack(
            rx.text(Estado.causas_recorrencia_texto, font_size="2.5rem", weight="bold", color=TEXTO, font_variant_numeric="tabular-nums"),
            rx.text(Estado.causas_recorrentes.to_string() + " recorrentes de " + Estado.causas_elegiveis.to_string() + " incidentes", size="2", color=TEXTO_SECUNDARIO),
            align="center", spacing="4", flex_wrap="wrap", width="100%",
        ),
        rx.tabs.root(
            rx.tabs.list(rx.tabs.trigger("Por Totem", value="totem"), rx.tabs.trigger("Por Loja", value="loja")),
            rx.tabs.content(_tabela_recorrencia(Estado.causas_por_totem, "Totem"), value="totem"),
            rx.tabs.content(_tabela_recorrencia(Estado.causas_por_loja, "Loja histórica"), value="loja"),
            default_value="totem", width="100%",
        ),
    )


def _pareto() -> rx.Component:
    return _painel(
        rx.heading("Causas por Categoria · Pareto", size="5", color=TEXTO),
        rx.cond(
            Estado.causas_elegiveis > 0,
            rx.text(
                Estado.causas_categorias_80.to_string() + " Categorias concentram 80% ou mais dos incidentes.",
                size="2", color=TEXTO_SECUNDARIO,
            ),
            rx.fragment(),
        ),
        rx.cond(
            Estado.causas_pareto.length() > 0,
            rx.vstack(
                rx.box(
                    rx.recharts.composed_chart(
                        rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                        rx.recharts.x_axis(data_key="nome", hide=True),
                        rx.recharts.y_axis(y_axis_id="volume", allow_decimals=False, width=42),
                        rx.recharts.y_axis(y_axis_id="percentual", orientation="right", domain=[0, 100], unit="%", width=52),
                        rx.recharts.graphing_tooltip(),
                        rx.recharts.legend(),
                        rx.recharts.bar(data_key="quantidade", name="Incidentes", y_axis_id="volume", fill="var(--accent-9)", max_bar_size=64, is_animation_active=False),
                        rx.recharts.line(data_key="acumulado_percentual", name="Acumulado (%)", y_axis_id="percentual", stroke="#2563EB", stroke_width=2, dot=True, is_animation_active=False),
                        rx.recharts.reference_line(y=80, y_axis_id="percentual", stroke=TEXTO_SECUNDARIO, stroke_dasharray="4 4"),
                        data=Estado.causas_pareto, width="100%", height=260,
                        margin={"top": 12, "right": 8, "bottom": 8, "left": 0},
                    ), width="100%", min_width="0", role="img", aria_label="Pareto: volume por Categoria e percentual acumulado. Valores na tabela abaixo.",
                ),
                rx.box(
                    rx.table.root(
                        rx.table.header(rx.table.row(
                            rx.table.column_header_cell("Categoria"), rx.table.column_header_cell("Incidentes"),
                            rx.table.column_header_cell("Participação"), rx.table.column_header_cell("Acumulado"),
                            rx.table.column_header_cell("Grupo de 80%"),
                        )),
                        rx.table.body(rx.foreach(Estado.causas_pareto, lambda causa: rx.table.row(
                            rx.table.row_header_cell(causa["nome"]), rx.table.cell(causa["quantidade"]),
                            rx.table.cell(causa["percentual_texto"]), rx.table.cell(causa["acumulado_texto"]),
                            rx.table.cell(rx.cond(causa["destaque_80"], rx.badge("Incluída", color_scheme="ruby", variant="soft"), rx.text("—"))),
                        ))), width="100%", size="2",
                    ), width="100%", overflow_x="auto",
                ), spacing="4", width="100%", align="start",
            ),
            _vazio("Nenhum incidente neste recorte."),
        ),
    )


def painel_causas() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.text(Estado.causas_periodo_texto, size="2", color=TEXTO),
            rx.text(Estado.causas_recorte_texto, size="2", color=TEXTO_SECUNDARIO),
            rx.text(Estado.causas_elegiveis.to_string() + " incidentes analisados", size="2", color=TEXTO_SECUNDARIO),
            align="start", spacing="1", width="100%",
        ),
        rx.cond(
            Estado.causas_sem_loja > 0,
            rx.callout(Estado.causas_sem_loja.to_string() + " incidentes sem Loja histórica ficam fora das análises por Loja.", icon="info", color_scheme="amber", width="100%"),
            rx.fragment(),
        ),
        rx.grid(_top_lojas(), _recorrencia(), columns={"initial": "1", "lg": "2"}, spacing="4", width="100%", align="start"),
        _pareto(),
        rx.el.details(
            rx.el.summary(
                "Como os indicadores são calculados",
                cursor="pointer", color=TEXTO_SECUNDARIO, font_size="0.875rem",
                _focus_visible={"outline": "2px solid var(--accent-9)", "outline_offset": "4px"},
            ),
            rx.vstack(
                rx.text("Somente Incidentes não cancelados, com Categoria e Totem válidos. A Categoria associada e o status atuais são usados, inclusive quando a Categoria está inativa. A Loja é a comprovada na abertura.", size="2", color=TEXTO_SECUNDARIO),
                rx.text("Um incidente é recorrente quando o mesmo Totem já teve outro da mesma Categoria nos 30 dias anteriores. O limite de 30 dias é incluído; chamados no mesmo instante não são predecessores entre si. O predecessor pode estar antes do período ou na Loja anterior do mesmo Totem.", size="2", color=TEXTO_SECUNDARIO),
                rx.text("O Pareto destaca as Categorias até alcançar pelo menos 80% dos incidentes. Empates de volume usam o menor ID.", size="2", color=TEXTO_SECUNDARIO),
                rx.text(Estado.causas_exclusoes_texto, size="2", color=TEXTO_SECUNDARIO),
                align="start", spacing="2", padding_top="0.75rem",
            ),
            max_width="75ch", width="100%",
        ),
        align="start", spacing="5", width="100%",
    )
