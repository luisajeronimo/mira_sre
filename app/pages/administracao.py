"""Troca obrigatória da senha temporária no primeiro acesso."""

import reflex as rx

from app.components.breadcrumbs import breadcrumbs
from app.components.visual import BORDA, CANVAS, RAIO_SUPERFICIE, SUPERFICIE, TEXTO, TEXTO_SECUNDARIO
from app.states.auth import AuthState


def _campo_rotulado(rotulo: str, identificador: str, controle: rx.Component) -> rx.Component:
    return rx.vstack(
        rx.el.label(rotulo, html_for=identificador), controle,
        spacing="2", align="start", width="100%",
    )


def primeiro_acesso() -> rx.Component:
    formulario = rx.form(
        rx.vstack(
            _campo_rotulado("Nova senha", "nova-senha", rx.input(id="nova-senha", name="nova_senha", type="password", placeholder="Nova senha", min_length=8, required=True, width="100%")),
            _campo_rotulado("Confirme a nova senha", "confirmacao-nova-senha", rx.input(id="confirmacao-nova-senha", name="confirmacao", type="password", placeholder="Confirme a nova senha", min_length=8, required=True, width="100%")),
            rx.cond(AuthState.mensagem_erro != "", rx.callout(AuthState.mensagem_erro, color_scheme="red", width="100%")),
            rx.button(rx.cond(AuthState.carregando, "Salvando...", "Salvar nova senha"), type="submit", disabled=AuthState.carregando, width="100%"),
            width="100%", spacing="4",
        ), on_submit=AuthState.trocar_senha_primeiro_acesso, reset_on_submit=True, width="100%",
    )
    return rx.center(
        rx.card(
            rx.vstack(
                breadcrumbs(("Acesso", "/login"), ("Primeiro acesso", None)),
                rx.image(src="/mira-logo.svg", alt="Logotipo MIRA", width="3rem", height="3rem"),
                rx.vstack(
                    rx.heading("Defina uma nova senha", size="6", color=TEXTO),
                    rx.text("Para continuar, substitua sua senha temporária.", color=TEXTO_SECUNDARIO, line_height="1.7"),
                    align="start", spacing="2", width="100%",
                ),
                formulario,
                align="start", width="100%", spacing="5",
            ),
            max_width="30rem", width="100%", padding="2rem",
            background=SUPERFICIE, border=f"1px solid {BORDA}", border_radius=RAIO_SUPERFICIE,
        ),
        min_height="100vh", padding="2rem", background=CANVAS,
    )
