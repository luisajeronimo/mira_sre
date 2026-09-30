"""Ponto de entrada da aplicação Reflex do MIRA."""

import reflex as rx

from app.pages import (
    detalhe_chamado,
    detalhe_chamado_tecnico,
    diretoria,
    gerente,
    index,
    login,
    novo_chamado,
    tecnico_chamados,
)
from app.chamados.gerente import ChamadosGerenteState
from app.chamados.tecnico import ChamadosTecnicoState
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
    on_load=ChamadosGerenteState.carregar_lista,
)
app.add_page(
    detalhe_chamado,
    route="/gerente/chamados/[chamado_id]",
    title="Chamado | MIRA",
    on_load=ChamadosGerenteState.carregar_detalhe,
)
app.add_page(
    novo_chamado,
    route="/gerente/chamados/novo",
    title="Novo chamado | MIRA",
    on_load=ChamadosGerenteState.carregar_formulario,
)
app.add_page(
    tecnico_chamados,
    route="/tecnico",
    title="Fila técnica | MIRA",
    on_load=ChamadosTecnicoState.carregar_fila,
)
app.add_page(
    detalhe_chamado_tecnico,
    route="/tecnico/chamados/[chamado_id]",
    title="Chamado técnico | MIRA",
    on_load=ChamadosTecnicoState.carregar_detalhe_tecnico,
)
app.add_page(
    diretoria,
    route="/diretoria",
    title="Diretoria | MIRA",
    on_load=AuthState.carregar_diretoria,
)
