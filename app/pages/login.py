"""Tela pública de login."""

import reflex as rx

from app.states.auth import AuthState


def login() -> rx.Component:
    return rx.center(
        rx.card(
            rx.vstack(
                rx.vstack(
                    rx.heading("MIRA", size="8"),
                    rx.text(
                        "Service Desk e Observabilidade",
                        color="gray",
                        text_align="center",
                    ),
                    align="center",
                    spacing="2",
                ),
                rx.form(
                    rx.vstack(
                        rx.text("E-mail", as_="label", weight="medium"),
                        rx.input(
                            name="email",
                            type="email",
                            placeholder="nome@empresa.com",
                            auto_complete=True,
                            required=True,
                            width="100%",
                        ),
                        rx.text("Senha", as_="label", weight="medium"),
                        rx.input(
                            name="senha",
                            type="password",
                            placeholder="Digite sua senha",
                            auto_complete=True,
                            required=True,
                            width="100%",
                        ),
                        rx.cond(
                            AuthState.mensagem_erro != "",
                            rx.callout(
                                AuthState.mensagem_erro,
                                icon="triangle_alert",
                                color_scheme="red",
                                width="100%",
                            ),
                        ),
                        rx.button(
                            rx.cond(
                                AuthState.carregando,
                                rx.hstack(
                                    rx.spinner(size="2"),
                                    rx.text("Entrando..."),
                                    align="center",
                                ),
                                rx.text("Entrar"),
                            ),
                            type="submit",
                            disabled=AuthState.carregando,
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    on_submit=AuthState.login,
                    reset_on_submit=True,
                    width="100%",
                ),
                spacing="5",
                width="100%",
            ),
            max_width="26rem",
            width="100%",
        ),
        min_height="100vh",
        padding="2rem",
        background="var(--gray-2)",
    )
