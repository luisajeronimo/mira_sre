"""Ponto de entrada da aplicação Reflex do MIRA."""

import reflex as rx

from app.pages import (
    alias,
    detalhe_chamado_canonico,
    administracao,
    index,
    inicio,
    login,
    novo_chamado,
    chamados,
    primeiro_acesso,
)
from app.monitoramento.pages import monitoramento
from app.monitoramento.state import MonitoramentoState
from app.chamados.gerente import ChamadosGerenteState
from app.chamados.tecnico import ChamadosTecnicoState
from app.pages.administracao import AdministracaoState
from app.states.auth import AuthState


# `ruby` é o token Radix disponível mais próximo do rose definido no DESIGN.md.
app = rx.App(theme=rx.theme(appearance="light", accent_color="ruby"))

app.add_page(index, route="/", title="MIRA", on_load=AuthState.carregar_raiz)
app.add_page(
    login,
    route="/login",
    title="Entrar | MIRA",
    on_load=AuthState.carregar_login,
)
app.add_page(
    administracao,
    route="/administracao/usuarios",
    title="Administração | MIRA",
    on_load=AdministracaoState.carregar_administracao,
)
app.add_page(primeiro_acesso, route="/primeiro-acesso", title="Primeiro acesso | MIRA", on_load=AuthState.carregar_primeiro_acesso)
app.add_page(
    inicio,
    route="/inicio",
    title="Início | MIRA",
    on_load=AuthState.carregar_inicio,
)
app.add_page(
    chamados,
    route="/chamados",
    title="Chamados | MIRA",
    on_load=AuthState.redirecionar_chamados_para_inicio,
)
app.add_page(
    novo_chamado,
    route="/chamados/novo",
    title="Novo chamado | MIRA",
    on_load=ChamadosGerenteState.carregar_formulario,
)
app.add_page(
    detalhe_chamado_canonico,
    route="/chamados/[chamado_id]",
    title="Chamado | MIRA",
    on_load=AuthState.carregar_detalhe_chamado,
)
app.add_page(
    lambda: alias(ChamadosGerenteState.redirecionar_alias_lista),
    route="/gerente",
    title="Gerente | MIRA",
    on_load=ChamadosGerenteState.redirecionar_alias_lista,
)
app.add_page(
    lambda: alias(ChamadosGerenteState.redirecionar_alias_novo),
    route="/gerente/chamados/novo",
    title="Novo chamado | MIRA",
    on_load=ChamadosGerenteState.redirecionar_alias_novo,
)
app.add_page(
    lambda: alias(ChamadosGerenteState.redirecionar_alias_detalhe),
    route="/gerente/chamados/[chamado_id]",
    title="Chamado | MIRA",
    on_load=ChamadosGerenteState.redirecionar_alias_detalhe,
)
app.add_page(
    lambda: alias(ChamadosTecnicoState.redirecionar_alias_fila),
    route="/tecnico",
    title="Fila técnica | MIRA",
    on_load=ChamadosTecnicoState.redirecionar_alias_fila,
)
app.add_page(
    lambda: alias(ChamadosTecnicoState.redirecionar_alias_detalhe),
    route="/tecnico/chamados/[chamado_id]",
    title="Chamado técnico | MIRA",
    on_load=ChamadosTecnicoState.redirecionar_alias_detalhe,
)
app.add_page(
    lambda: alias(AuthState.redirecionar_alias_diretoria),
    route="/diretoria",
    title="Diretoria | MIRA",
    on_load=AuthState.redirecionar_alias_diretoria,
)
app.add_page(
    lambda: alias(AdministracaoState.redirecionar_alias_administracao),
    route="/administracao",
    title="Administração | MIRA",
    on_load=AdministracaoState.redirecionar_alias_administracao,
)

app.add_page(
    monitoramento,
    route="/monitoramento",
    title="Monitoramento | MIRA",
    on_load=MonitoramentoState.carregar,
)
