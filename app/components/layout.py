"""Componentes da casca autenticada e estados neutros do MIRA."""

from __future__ import annotations

import reflex as rx

from app.components.navegacao import ITENS_NAVEGACAO, ItemNavegacao
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
                rx.text(item.rotulo, weight="medium"),
                spacing="3",
                width="100%",
                align="center",
            ),
            href=item.rota,
            aria_current=rx.cond(ativo, "page", "false"),
            width="100%",
            padding="0.7rem 0.8rem",
            border_radius="8px",
            background=rx.cond(ativo, "var(--accent-3)", "transparent"),
            color=rx.cond(ativo, "var(--accent-11)", "var(--gray-12)"),
            text_decoration="none",
            border_left=rx.cond(ativo, "3px solid var(--accent-9)", "3px solid transparent"),
            _hover={"background": "var(--gray-3)"},
            _focus_visible={
                "outline": "3px solid var(--accent-9)",
                "outline_offset": "2px",
            },
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
            rx.text("MIRA", weight="bold", size="4"),
            rx.text("Service Desk e Observabilidade", size="1", color="gray"),
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


def _identidade() -> rx.Component:
    return rx.vstack(
        rx.text(AuthState.nome, weight="bold", size="2"),
        rx.text(AuthState.email, size="1", color="gray", max_width="13rem"),
        rx.badge(AuthState.role, variant="soft"),
        align="start",
        spacing="1",
        width="100%",
    )


def _sidebar_desktop() -> rx.Component:
    return rx.vstack(
        _marca(),
        _itens_navegacao(),
        rx.spacer(),
        _identidade(),
        rx.button(
            "Sair",
            on_click=AuthState.logout,
            variant="outline",
            width="100%",
        ),
        width="17rem",
        min_height="100vh",
        padding="1.25rem",
        border_right="1px solid var(--gray-5)",
        background="var(--color-panel)",
        align="start",
        spacing="5",
        position="sticky",
        top="0",
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
    conteudo: rx.Component, destino_inicio: str | None = None
) -> rx.Component:
    """Apresenta conteúdo somente dentro da navegação autenticada."""
    del destino_inicio
    return rx.hstack(
        _sidebar_desktop(),
        rx.vstack(
            rx.box(
                conteudo,
                width="100%",
                padding="2rem",
            ),
            width="100%",
            min_height="100vh",
            spacing="0",
            align="start",
        ),
        width="100%",
        min_height="100vh",
        spacing="0",
        align="start",
    )
