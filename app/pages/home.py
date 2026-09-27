"""Páginas iniciais neutras dos perfis oficiais."""

import reflex as rx

from app.components.layout import (
    casca_autenticada,
    estado_carregamento,
    estado_revalidacao,
)
from app.states.auth import AuthState


def index() -> rx.Component:
    return rx.cond(
        AuthState.carregando,
        estado_carregamento(),
        estado_revalidacao(AuthState.carregar_raiz),
    )


def _pagina_protegida(
    perfil: str,
    titulo: str,
    descricao: str,
    destino_inicio: str,
    evento_tentar_novamente,
) -> rx.Component:
    conteudo = rx.cond(
        AuthState.sessao_confirmada & (AuthState.role == perfil),
        casca_autenticada(titulo, descricao, destino_inicio),
        estado_revalidacao(evento_tentar_novamente),
    )
    return rx.cond(
        AuthState.carregando,
        estado_carregamento(),
        conteudo,
    )


def gerente() -> rx.Component:
    from app.pages.chamados import gerente_chamados

    return gerente_chamados()


def tecnico() -> rx.Component:
    return _pagina_protegida(
        "tecnico",
        "Início do Técnico",
        "Sua sessão está autenticada para o perfil Técnico.",
        "/tecnico",
        AuthState.carregar_tecnico,
    )


def diretoria() -> rx.Component:
    return _pagina_protegida(
        "diretoria",
        "Início da Diretoria",
        "Sua sessão está autenticada para o perfil Diretoria.",
        "/diretoria",
        AuthState.carregar_diretoria,
    )
