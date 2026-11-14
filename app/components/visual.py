"""Tokens e composições visuais compartilhados da interface desktop do MIRA."""

from __future__ import annotations

import reflex as rx
from reflex.components.component import NoSSRComponent

FONTE_INTERFACE = '"Plus Jakarta Sans", "Segoe UI", sans-serif'
FONTE_TECNICA = '"JetBrains Mono", "SFMono-Regular", Consolas, monospace'

CANVAS = "#F7F8FC"
SUPERFICIE = "#FFFFFF"
SUPERFICIE_SUAVE = "#F3F4F9"
TEXTO = "#172033"
TEXTO_SECUNDARIO = "#626C7D"
BORDA = "#E6E8F0"
BORDA_ROSE_SUAVE = "var(--accent-5)"
SOMBRA_BAIXA = "0 2px 8px rgba(23, 32, 51, 0.025)"
RAIO_CONTROLE = "10px"
RAIO_SUPERFICIE = "14px"

FOCO_VISIVEL = {
    "outline": "3px solid var(--accent-9)",
    "outline_offset": "2px",
}

ESTILO_CAMPO_COMENTARIO = {
    "background": SUPERFICIE,
    "border": f"1px solid {BORDA_ROSE_SUAVE}",
    "border_radius": RAIO_CONTROLE,
    "padding": "0.75rem",
    "box_shadow": "none",
    "_focus_visible": FOCO_VISIVEL,
}

_ARQUIVO_SELETOR_PERIODO = rx.asset("date_range_picker.jsx", shared=True)


class SeletorPeriodoCalendario(NoSSRComponent):
    """Wrapper client-side do calendário de intervalo, sem contrato remoto."""

    library = _ARQUIVO_SELETOR_PERIODO.importable_path
    tag = "SeletorPeriodoCalendario"
    lib_dependencies = ["react-day-picker@9.14.0"]

    inicio: rx.Var[str]
    fim: rx.Var[str]
    rotulo: rx.Var[str]
    disabled: rx.Var[bool]
    on_change: rx.EventHandler[lambda inicio, fim: [inicio, fim]]


seletor_periodo_calendario = SeletorPeriodoCalendario.create


def dropdown_multisselecao(opcoes, selecionados, ao_alternar, rotulo: str, disabled=False) -> rx.Component:
    """Seleção controlada; marcar opções não confirma os filtros da página."""
    return rx.popover.root(
        rx.popover.trigger(
            rx.button(
                rx.cond(selecionados.length() == 0, rotulo, selecionados.length().to_string() + " selecionado(s)"),
                rx.icon("chevron-down", size=16),
                variant="outline",
                color_scheme="gray",
                disabled=disabled,
                width="100%",
                justify="between",
                min_height="2.5rem",
                padding_x="0.75rem",
                aria_label=rotulo,
                _focus_visible=FOCO_VISIVEL,
            )
        ),
        rx.popover.content(
            rx.vstack(
                rx.foreach(
                    opcoes,
                    lambda opcao: rx.checkbox(
                        opcao,
                        checked=selecionados.contains(opcao),
                        on_change=lambda _: ao_alternar(opcao),
                        disabled=disabled,
                        _focus_visible=FOCO_VISIVEL,
                    ),
                ),
                align="start",
                spacing="2",
            ),
            max_height="20rem",
            overflow_y="auto",
            padding="1rem",
            border_radius=RAIO_SUPERFICIE,
        ),
    )


def rotulo_campo(texto: str) -> rx.Component:
    """Rótulo compacto e persistente para filtros e informações."""
    return rx.text(
        texto,
        size="1",
        weight="bold",
        color=TEXTO_SECUNDARIO,
        letter_spacing="0.035em",
        text_transform="uppercase",
    )


def campo_rotulado(
    rotulo: str,
    controle: rx.Component,
    *,
    largura: str = "11rem",
    coluna: str = "span 3",
) -> rx.Component:
    return rx.vstack(
        rotulo_campo(rotulo),
        controle,
        spacing="2",
        align="start",
        min_width=f"min({largura}, 100%)",
        min_height="4rem",
        width="100%",
        grid_column=coluna,
    )


def periodo_rotulado(
    rotulo: str,
    inicio: rx.Var[str],
    fim: rx.Var[str],
    on_change,
    disabled: rx.Var[bool],
    *,
    coluna: str = "span 4",
    largura: str = "18rem",
    altura: str = "4.5rem",
) -> rx.Component:
    return rx.vstack(
        rotulo_campo(rotulo),
        seletor_periodo_calendario(
            inicio=inicio,
            fim=fim,
            rotulo=rotulo,
            on_change=on_change,
            disabled=disabled,
        ),
        spacing="2",
        min_width=f"min({largura}, 100%)",
        min_height=altura,
        width="100%",
        grid_column=coluna,
    )


def acoes_filtro(
    aplicar: rx.Component,
    limpar: rx.Component,
    *,
    mostrar_rotulo: bool = True,
) -> rx.Component:
    """Agrupa as ações existentes sem alterar seus eventos ou disponibilidade."""
    conteudo = [
        rx.hstack(
            aplicar,
            limpar,
            spacing="2",
            align="center",
            width="100%",
        )
    ]
    if mostrar_rotulo:
        conteudo.insert(0, rotulo_campo("Ações"))

    return rx.vstack(
        *conteudo,
        spacing="1",
        align="end",
        flex_shrink="0",
    )


def painel_filtros(
    *campos: rx.Component,
    acoes: rx.Component,
    aplicados: rx.Component,
) -> rx.Component:
    """Superfície e grade únicas para filtros já existentes nas filas."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("sliders-horizontal", size=16, color=TEXTO_SECUNDARIO),
                    rx.text("Filtros", weight="bold", color=TEXTO),
                    align="center",
                    spacing="2",
                ),
                rx.spacer(),
                acoes,
                align="center",
                width="100%",
            ),
            rx.grid(
                *campos,
                columns="repeat(12, minmax(0, 1fr))",
                column_gap="1rem",
                row_gap="0.75rem",
                align_items="start",
                width="100%",
            ),
            aplicados,
            align="start",
            spacing="4",
            width="100%",
        ),
        width="100%",
        background=SUPERFICIE,
        border=f"1px solid {BORDA}",
        border_radius=RAIO_SUPERFICIE,
        box_shadow=SOMBRA_BAIXA,
        padding="1.5rem",
        class_name="mira-filters",
    )


def cabecalho_tabela_ordenavel(
    rotulo: str,
    coluna: str,
    ordenar_por: rx.Var,
    direcao: rx.Var,
    on_click,
    disabled: rx.Var,
    *,
    largura: str = "auto",
) -> rx.Component:
    """Cabeçalho rose acessível que preserva o controle de ordenação recebido."""
    return rx.table.column_header_cell(
        rx.button(
            rx.hstack(
                rx.text(rotulo, weight="bold", line_height="1.4"),
                rx.cond(
                    ordenar_por == coluna,
                    rx.cond(
                        direcao == "ASC",
                        rx.icon("arrow_up", size=17, color="white"),
                        rx.icon("arrow_down", size=17, color="white"),
                    ),
                ),
                spacing="1",
                align="center",
                justify="center",
                width="100%",
            ),
            variant="ghost",
            on_click=on_click,
            disabled=disabled,
            aria_label="Ordenar por " + rotulo,
            color="white",
            border_radius="0",
            border="0",
            box_shadow="none",
            height="100%",
            min_height="3rem",
            padding="0.75rem 0.25rem",
            margin="0",
            box_sizing="border-box",
            transform="none",
            width="100%",
            _hover={
                "background": "var(--accent-10)",
                "border": "0",
                "box_shadow": "none",
                "transform": "none",
            },
            transition="background-color 150ms ease",
            _focus_visible=FOCO_VISIVEL,
        ),
        background="var(--accent-9)",
        color="white",
        text_align="center",
        vertical_align="middle",
        height="100%",
        padding="0",
        width=largura,
    )


def cabecalho_tabela_texto(rotulo: str, *, largura: str = "auto") -> rx.Component:
    return rx.table.column_header_cell(
        rx.text(rotulo, weight="bold"),
        background="var(--accent-9)",
        color="white",
        text_align="center",
        vertical_align="middle",
        padding="0.75rem",
        width=largura,
    )


def celula_tabela(conteudo, *, alinhamento: str = "center") -> rx.Component:
    """Mantém o ritmo visual das células, preservando o conteúdo recebido."""
    return rx.table.cell(
        conteudo,
        text_align=alinhamento,
        vertical_align="middle",
        padding_x="0.375rem",
        padding_y="0.875rem",
        overflow_wrap="break-word",
        line_height="1.5",
    )


def campo_info(rotulo: str, valor: rx.Component | str) -> rx.Component:
    return rx.vstack(
        rotulo_campo(rotulo),
        rx.box(valor, color=TEXTO, width="100%"),
        spacing="2",
        align="start",
        padding_y="0.25rem",
        width="100%",
    )


def painel_detalhe(conteudo: rx.Component) -> rx.Component:
    """Superfície única para os dados funcionais do chamado."""
    return rx.card(
        conteudo,
        width="100%",
        background=SUPERFICIE,
        border=f"1px solid {BORDA}",
        border_radius=RAIO_SUPERFICIE,
        box_shadow=SOMBRA_BAIXA,
        padding="1.5rem",
    )


def cabecalho_detalhe_chamado(
    identificador: rx.Var | str,
    titulo: rx.Var | str,
    on_click,
) -> rx.Component:
    """Faixa compartilhada do detalhe, preservando a ação própria de cada perfil."""
    return rx.hstack(
        rx.heading(
            "Chamado #" + identificador + " - " + titulo,
            size="5",
            weight="bold",
            color=TEXTO,
            flex_grow="1",
            min_width="0",
        ),
        rx.button(
            rx.text("Detalhe do Totem", weight="bold"),
            size="3",
            color_scheme="ruby",
            on_click=on_click,
            flex_shrink="0",
        ),
        justify="between",
        align="center",
        flex_wrap="wrap",
        gap="1rem",
        width="100%",
    )


def composicao_detalhe_chamado(
    dados: rx.Component,
    descricao: rx.Var | str,
    *secoes_externas: rx.Component,
) -> rx.Component:
    """Mantém descrição e tratativa como seções irmãs do painel de dados."""
    return rx.vstack(
        painel_detalhe(dados),
        bloco_descricao(descricao),
        *secoes_externas,
        align="start",
        spacing="4",
        width="100%",
    )


def bloco_descricao(valor: rx.Var | str) -> rx.Component:
    """Agrupa a descrição em área própria sem competir com os dados em grade."""
    return rx.vstack(
        rotulo_campo("Descrição"),
        rx.text(valor, white_space="pre-wrap", color=TEXTO, line_height="1.75", max_width="75ch"),
        align="start",
        spacing="2",
        background=SUPERFICIE,
        border=f"1px solid {BORDA}",
        border_radius=RAIO_CONTROLE,
        padding="1rem",
        width="100%",
    )


def badge_status(valor: rx.Var | str) -> rx.Component:
    esquema = rx.match(
        valor,
        ("online", "green"),
        ("offline", "red"),
        ("Resolvido", "green"),
        ("Encerrado", "green"),
        ("Cancelado", "red"),
        ("Em Atendimento", "blue"),
        ("Novo", "ruby"),
        "gray",
    )
    return rx.badge(
        rx.text(valor, text_transform="uppercase", size="1", weight="bold"),
        color_scheme=esquema,
        variant="soft",
        radius="full",
        padding="0.1875rem 0.5625rem",
    )


def badge_prioridade(valor: rx.Var | str) -> rx.Component:
    """Distingue visualmente a prioridade já retornada, sem normalizá-la."""
    esquema = rx.match(
        valor,
        ("Crítica", "red"),
        ("Alta", "ruby"),
        ("Média", "violet"),
        ("Baixa", "gray"),
        "gray",
    )
    return rx.badge(
        rx.text(valor, size="1", weight="bold"),
        color_scheme=esquema,
        variant="soft",
        radius="full",
        padding="0.1875rem 0.5625rem",
    )


def badge_visibilidade(valor: rx.Var | str) -> rx.Component:
    return rx.badge(
        rx.text(valor, text_transform="uppercase", size="1", weight="bold"),
        color_scheme=rx.match(valor, ("Interno", "amber"), ("Público", "blue"), "gray"),
        variant="soft",
        radius="full",
    )
