"""Troca obrigatória da senha temporária no primeiro acesso."""

import reflex as rx

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
            rx.button(rx.cond(AuthState.carregando, "Salvando...", "Salvar nova senha"), type="submit", disabled=AuthState.carregando),
            width="100%", spacing="3",
        ), on_submit=AuthState.trocar_senha_primeiro_acesso, reset_on_submit=True, width="100%",
    )
    return rx.center(rx.card(rx.vstack(rx.heading("Defina uma nova senha", size="6"), rx.text("Para continuar, substitua sua senha temporária."), formulario, width="100%", spacing="4"), max_width="28rem", width="100%"), min_height="100vh", padding="2rem")
