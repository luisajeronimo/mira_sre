"""Composições neutras das rotas canônicas por funcionalidade."""

import reflex as rx

from app.chamados.gerente import detalhe_chamado, gerente_chamados
from app.chamados.tecnico import detalhe_chamado_tecnico, tecnico_chamados
from app.components.layout import estado_carregamento, estado_revalidacao
from app.states.auth import AuthState


def _protegida(conteudo: rx.Component, evento) -> rx.Component:
    """Não escolhe uma jornada antes de a identidade estar confirmada."""
    return rx.cond(
        AuthState.carregando,
        estado_carregamento(),
        rx.cond(
            AuthState.sessao_confirmada,
            conteudo,
            estado_revalidacao(evento),
        ),
    )


def _jornada_lista() -> rx.Component:
    return rx.cond(
        AuthState.role == "gerente",
        gerente_chamados(),
        tecnico_chamados(),
    )


def inicio() -> rx.Component:
    return _protegida(_jornada_lista(), AuthState.carregar_inicio)


def chamados() -> rx.Component:
    """Rota legada que preserva links para a listagem canônica em `/inicio`."""
    return alias(AuthState.redirecionar_chamados_para_inicio)


def detalhe_chamado_canonico() -> rx.Component:
    return _protegida(
        rx.cond(
            AuthState.role == "gerente",
            detalhe_chamado(),
            detalhe_chamado_tecnico(),
        ),
        AuthState.carregar_detalhe_chamado,
    )


def alias(evento) -> rx.Component:
    """Placeholder protegido: aliases nunca renderizam a jornada anterior."""
    return rx.cond(
        AuthState.carregando,
        estado_carregamento(),
        estado_revalidacao(evento),
    )
