"""Tela pública de login."""

import reflex as rx

from app.components.visual import (
    BORDA,
    CANVAS,
    FOCO_VISIVEL,
    RAIO_CONTROLE,
    SUPERFICIE,
    TEXTO,
    TEXTO_SECUNDARIO,
)
from app.states.auth import AuthState


def _cartao_contexto(icone: str, titulo: str, descricao: str) -> rx.Component:
    """Resumo visual do produto sem métricas ou comportamento próprios."""
    return rx.card(
        rx.hstack(
            rx.center(
                rx.icon(icone, size=22, color="var(--accent-10)"),
                width="3rem",
                height="3rem",
                border_radius=RAIO_CONTROLE,
                background="#E7EEFF",
                flex_shrink="0",
            ),
            rx.vstack(
                rx.text(titulo, weight="bold", color=TEXTO),
                rx.text(descricao, size="2", color=TEXTO_SECUNDARIO),
                align="start",
                spacing="1",
                min_width="0",
            ),
            align="center",
            spacing="3",
            width="100%",
        ),
        width="100%",
        padding="1rem 1.125rem",
        background="rgba(255, 255, 255, 0.9)",
        border="1px solid rgba(255, 255, 255, 0.95)",
        border_radius="12px",
        box_shadow="none",
    )


def _painel_contexto() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.image(
                src="/mira-logo.svg",
                alt="Logotipo MIRA",
                width="1.75rem",
                height="1.75rem",
            ),
            rx.text("MIRA", weight="bold", size="2", color=TEXTO),
            rx.box(width="1px", height="1.5rem", background="var(--accent-6)"),
            rx.text(
                "SERVICE DESK & OBSERVABILIDADE",
                size="1",
                weight="bold",
                color="var(--accent-11)",
                letter_spacing="0.06em",
            ),
            align="center",
            spacing="3",
        ),
        rx.vstack(
            rx.heading(
                "Monitoramento Operacional",
                size="7",
                color=TEXTO,
                letter_spacing="-0.03em",
            ),
            rx.text(
                "Plataforma centralizada para acompanhar Totens, telemetria "
                "e chamados técnicos.",
                color="#536079",
                size="3",
                line_height="1.7",
                max_width="27rem",
            ),
            align="start",
            spacing="3",
            width="100%",
        ),
        rx.vstack(
            _cartao_contexto(
                "activity",
                "Observabilidade centralizada",
                "Acompanhe a operação dos Totens em uma experiência integrada.",
            ),
            _cartao_contexto(
                "headphones",
                "Service Desk conectado",
                "Registre e acompanhe chamados com clareza operacional.",
            ),
            spacing="3",
            width="100%",
        ),
        rx.card(
            rx.hstack(
                rx.icon("shield_check", size=22, color="var(--accent-10)"),
                rx.vstack(
                    rx.text(
                        "Operação conectada",
                        weight="bold",
                        color="var(--accent-11)",
                    ),
                    rx.text(
                        "Disponibilidade, telemetria e atendimento em um só lugar.",
                        size="2",
                        color="#536079",
                    ),
                    align="start",
                    spacing="1",
                ),
                align="start",
                spacing="3",
            ),
            width="100%",
            padding="1rem 1.125rem",
            background="rgba(255, 241, 242, 0.7)",
            border="1px solid rgba(251, 113, 133, 0.12)",
            border_radius="12px",
            box_shadow="none",
        ),
        align="start",
        justify="between",
        spacing="5",
        width="100%",
        height="100%",
        min_width="0",
        padding="2.75rem",
        background="linear-gradient(145deg, #FFF5F7 0%, #EDF2FF 52%, #E7EEFF 100%)",
    )


def _campo_login(
    rotulo: str,
    nome: str,
    tipo: str,
    placeholder: str,
    icone: str,
) -> rx.Component:
    return rx.vstack(
        rx.el.label(rotulo, html_for="login-" + nome, color=TEXTO),
        rx.input(
            rx.input.slot(rx.icon(icone, size=18, color="#60708E")),
            name=nome,
            id="login-" + nome,
            type=tipo,
            placeholder=placeholder,
            auto_complete=True,
            required=True,
            size="3",
            width="100%",
            min_height="3.5rem",
            background=SUPERFICIE,
            border=f"1px solid {BORDA}",
            border_radius=RAIO_CONTROLE,
            box_shadow="none",
            _focus_visible=FOCO_VISIVEL,
        ),
        align="start",
        spacing="2",
        width="100%",
    )


def _formulario_login() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.image(
                src="/mira-logo.svg",
                alt="Logotipo oficial do MIRA",
                width="7rem",
                height="7rem",
            ),
            rx.text(
                "Entre com suas credenciais.",
                color=TEXTO_SECUNDARIO,
                text_align="center",
                line_height="1.6",
            ),
            align="center",
            spacing="3",
            width="100%",
        ),
        rx.form(
            rx.vstack(
                _campo_login(
                    "E-mail institucional",
                    "email",
                    "email",
                    "nome@empresa.com",
                    "mail",
                ),
                _campo_login(
                    "Senha de acesso",
                    "senha",
                    "password",
                    "Digite sua senha",
                    "lock",
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
                            justify="center",
                        ),
                        rx.hstack(
                            rx.text("Entrar", weight="bold"),
                            rx.icon("arrow_right", size=18),
                            align="center",
                            justify="center",
                        ),
                    ),
                    type="submit",
                    disabled=AuthState.carregando,
                    color_scheme="ruby",
                    width="100%",
                    min_height="3.5rem",
                    weight="bold",
                    border_radius=RAIO_CONTROLE,
                    box_shadow="0 3px 8px rgba(190, 18, 60, 0.12)",
                    _focus_visible=FOCO_VISIVEL,
                ),
                spacing="4",
                width="100%",
            ),
            on_submit=AuthState.login,
            reset_on_submit=True,
            width="100%",
        ),
        spacing="6",
        align="center",
        width="100%",
        max_width="34rem",
    )


def _painel_login() -> rx.Component:
    return rx.vstack(
        rx.center(
            _formulario_login(),
            width="100%",
            flex="1",
            padding="3rem 4rem 2.5rem",
        ),
        rx.hstack(
            rx.hstack(
                rx.icon("lock", size=17, color="var(--accent-10)"),
                rx.text("Ambiente de acesso protegido", size="2", color="#536079"),
                align="center",
                spacing="2",
            ),
            rx.text(
                "MIRA • Service Desk e Observabilidade",
                size="1",
                weight="bold",
                color=TEXTO_SECUNDARIO,
            ),
            justify="between",
            align="center",
            width="100%",
            padding="1.25rem 2rem",
            background="#F6F7FB",
        ),
        spacing="0",
        align="center",
        width="100%",
        height="100%",
        min_width="0",
        background=SUPERFICIE,
    )


def login() -> rx.Component:
    return rx.center(
        rx.grid(
            _painel_contexto(),
            _painel_login(),
            columns="2",
            width="100%",
            max_width="72rem",
            min_height="43rem",
            background=SUPERFICIE,
            border=f"1px solid {BORDA}",
            border_radius="16px",
            box_shadow="0 16px 48px rgba(35, 25, 45, 0.07)",
            overflow="hidden",
            style={
                "gridTemplateColumns": "minmax(0, 5fr) minmax(0, 7fr)",
            },
        ),
        min_height="100vh",
        width="100%",
        padding="2rem",
        background=(
            "radial-gradient(circle at 88% 8%, rgba(251, 113, 133, 0.13), "
            "transparent 28%), "
            "radial-gradient(circle at 8% 92%, rgba(96, 165, 250, 0.11), "
            f"transparent 30%), {CANVAS}"
        ),
    )
