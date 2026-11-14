"""Componentes da casca autenticada e estados neutros do MIRA."""

from __future__ import annotations

import reflex as rx

from app.components.breadcrumbs import breadcrumbs_pagina
from app.components.navegacao import ITENS_NAVEGACAO, ItemNavegacao
from app.components.visual import (
    BORDA,
    CANVAS,
    FOCO_VISIVEL,
    RAIO_CONTROLE,
    RAIO_SUPERFICIE,
    SOMBRA_BAIXA,
    SUPERFICIE,
    SUPERFICIE_SUAVE,
    TEXTO,
    TEXTO_SECUNDARIO,
)
from app.states.auth import AuthState


def estado_carregamento() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.spinner(size="3"),
            rx.text("Validando sessão...", color="gray"),
            align="center",
            spacing="3",
        ),
        min_height="100vh",
        width="100%",
    )


def estado_revalidacao(evento_tentar_novamente) -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading("Não foi possível validar a sessão", size="5"),
                rx.text(AuthState.mensagem_erro, color="gray"),
                rx.button(
                    "Tentar novamente",
                    on_click=evento_tentar_novamente,
                ),
                align="center",
                spacing="4",
            ),
            max_width="28rem",
            width="100%",
        ),
        min_height="100vh",
        padding="2rem",
    )


def _perfil_tem_acesso(item: ItemNavegacao):
    expressoes = [AuthState.role == perfil for perfil in item.perfis]
    permitido = expressoes[0]
    for expressao in expressoes[1:]:
        permitido = permitido | expressao
    return permitido


def _item_ativo(item: ItemNavegacao):
    rota_atual = AuthState.router.page.path
    expressoes = [rota_atual == rota for rota in item.rotas_ativas]
    ativo = expressoes[0]
    for expressao in expressoes[1:]:
        ativo = ativo | expressao
    return ativo


def _link_navegacao(item: ItemNavegacao) -> rx.Component:
    ativo = _item_ativo(item)
    return rx.cond(
        _perfil_tem_acesso(item),
        rx.link(
            rx.hstack(
                rx.icon(item.icone, size=18),
                rx.text(item.rotulo, weight=rx.cond(ativo, "bold", "medium")),
                spacing="3",
                width="100%",
                align="center",
            ),
            href=item.rota,
            aria_current=rx.cond(ativo, "page", "false"),
            width="100%",
            padding="0.75rem 0.875rem",
            border_radius=RAIO_CONTROLE,
            background=rx.cond(ativo, "var(--accent-3)", "transparent"),
            color=rx.cond(ativo, "var(--accent-11)", TEXTO),
            text_decoration="none",
            border_left=rx.cond(ativo, "1px solid var(--accent-9)", "1px solid transparent"),
            _hover={"background": rx.cond(ativo, "var(--accent-4)", SUPERFICIE_SUAVE)},
            _focus_visible=FOCO_VISIVEL,
            class_name="mira-nav-link",
        ),
        rx.fragment(),
    )


def _marca() -> rx.Component:
    return rx.hstack(
        rx.image(
            src="/mira-logo.svg",
            alt="Logotipo MIRA",
            width="2.5rem",
            height="2.5rem",
        ),
        rx.vstack(
            rx.text("MIRA", weight="bold", size="4", color=TEXTO),
            rx.text("Service Desk e Observabilidade", size="1", color=TEXTO_SECUNDARIO, line_height="1.5"),
            align="start",
            spacing="0",
        ),
        align="center",
        spacing="3",
    )


def _itens_navegacao() -> rx.Component:
    return rx.vstack(
        *[_link_navegacao(item) for item in ITENS_NAVEGACAO],
        width="100%",
        spacing="1",
        align="start",
    )


def _sidebar_desktop() -> rx.Component:
    return rx.vstack(
        _marca(),
        _itens_navegacao(),
        rx.spacer(),
        width="15.5rem",
        flex_shrink="0",
        height="100vh",
        min_height="100vh",
        padding="1.75rem 1rem",
        border_right=f"1px solid {BORDA}",
        background=SUPERFICIE,
        align="start",
        spacing="7",
        position="sticky",
        top="0",
        class_name="mira-sidebar",
    )


def _topbar_desktop(evento_sair=AuthState.logout) -> rx.Component:
    return rx.hstack(
        rx.spacer(),
        rx.hstack(
            rx.avatar(fallback=AuthState.nome[:1].upper(), aria_label=AuthState.nome, size="2", variant="soft"),
            rx.vstack(
                rx.text(AuthState.nome, size="2", weight="medium", color=TEXTO),
                rx.text(
                    AuthState.role,
                    size="1",
                    weight="bold",
                    color=TEXTO_SECUNDARIO,
                    text_transform="uppercase",
                    letter_spacing="0.05em",
                ),
                spacing="0",
                align="start",
            ),
            rx.divider(orientation="vertical", height="1.75rem"),
            rx.button(
                "Sair",
                on_click=evento_sair,
                color_scheme="ruby",
                variant="soft",
                size="2",
            ),
            spacing="3",
            align="center",
        ),
        width="100%",
        padding="0.875rem 2rem",
        border_bottom=f"1px solid {BORDA}",
        background=SUPERFICIE,
        min_height="4.25rem",
        class_name="mira-topbar",
    )


def casca_autenticada(
    titulo: str,
    descricao: str,
    destino_inicio: str,
) -> rx.Component:
    del destino_inicio
    return casca_conteudo(
        rx.card(
            rx.vstack(
                rx.heading(titulo, size="7"),
                rx.text(descricao, color="gray", text_align="center"),
                align="center",
                spacing="4",
            ),
            max_width="38rem",
            width="100%",
        )
    )


def casca_conteudo(
    conteudo: rx.Component, destino_inicio: str | None = None, evento_sair=None
) -> rx.Component:
    """Apresenta conteúdo somente dentro da navegação autenticada."""
    del destino_inicio
    return rx.hstack(
        _sidebar_desktop(),
        rx.vstack(
            _topbar_desktop(evento_sair or AuthState.logout),
            rx.box(
                rx.box(
                    breadcrumbs_pagina(),
                    conteudo,
                    display="flex",
                    flex_direction="column",
                    gap="1.25rem",
                    width="100%",
                    max_width="104rem",
                    margin="0 auto",
                    min_width="0",
                ),
                width="100%",
                padding="2rem 2rem 3rem",
                background=CANVAS,
                min_width="0",
                class_name="mira-workspace",
            ),
            width="100%",
            min_width="0",
            min_height="100vh",
            spacing="0",
            align="start",
        ),
        width="100%",
        min_height="100vh",
        spacing="0",
        align="start",
        class_name="mira-shell",
    )
