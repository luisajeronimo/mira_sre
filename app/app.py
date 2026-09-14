"""Ponto de entrada da aplicação Reflex do MIRA."""

import reflex as rx

from app.pages import diretoria, gerente, index, login, tecnico
from app.states.auth import AuthState


app = rx.App(theme=rx.theme(appearance="light", accent_color="blue"))

app.add_page(index, route="/", title="MIRA", on_load=AuthState.carregar_raiz)
app.add_page(
    login,
    route="/login",
    title="Entrar | MIRA",
    on_load=AuthState.carregar_login,
)
app.add_page(
    gerente,
    route="/gerente",
    title="Gerente | MIRA",
    on_load=AuthState.carregar_gerente,
)
app.add_page(
    tecnico,
    route="/tecnico",
    title="Técnico | MIRA",
    on_load=AuthState.carregar_tecnico,
)
app.add_page(
    diretoria,
    route="/diretoria",
    title="Diretoria | MIRA",
    on_load=AuthState.carregar_diretoria,
)
