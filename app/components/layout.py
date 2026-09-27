"""Componentes da casca autenticada do MIRA."""

import reflex as rx

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


def casca_autenticada(
    titulo: str,
    descricao: str,
    destino_inicio: str,
) -> rx.Component:
    return casca_conteudo(
        rx.card(
            rx.vstack(
                rx.heading(titulo, size="7"),
                rx.text(descricao, color="gray", text_align="center"),
                rx.text(
                    "A navegação funcional será adicionada em changes futuras.",
                    size="2",
                    color="gray",
                ),
                align="center",
                spacing="4",
            ),
            max_width="38rem",
            width="100%",
        ),
        destino_inicio,
    )


def casca_conteudo(conteudo: rx.Component, destino_inicio: str) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.heading("MIRA", size="6"),
                rx.text("Service Desk e Observabilidade", color="gray"),
                align="start",
                spacing="1",
            ),
            rx.spacer(),
            rx.link("Início", href=destino_inicio),
            rx.vstack(
                rx.text(AuthState.nome, weight="bold"),
                rx.text(AuthState.email, size="2", color="gray"),
                rx.badge(AuthState.role, variant="soft"),
                align="end",
                spacing="1",
            ),
            rx.button("Sair", variant="outline", on_click=AuthState.logout),
            width="100%",
            align="center",
            padding="1.25rem 2rem",
            border_bottom="1px solid var(--gray-5)",
        ),
        rx.center(
            conteudo,
            flex="1",
            width="100%",
            padding="2rem",
        ),
        min_height="100vh",
        width="100%",
        spacing="0",
    )
