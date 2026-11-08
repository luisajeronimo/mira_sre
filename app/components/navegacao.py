"""Configuração central da navegação autenticada do MIRA."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


PERFIS_OFICIAIS = frozenset(
    {"gerente", "tecnico", "diretoria", "administrador"}
)

VARIAVEL_ACOMPANHAMENTO_SOLICITANTE = "MIRA_ACOMPANHAMENTO_SOLICITANTE_PUBLICADO"


def acompanhamento_solicitante_publicado() -> bool:
    """Liberação (K-B, task 5.8) do acompanhamento do solicitante e do histórico.

    Ligar somente depois que os contratos `solicitante/**` e `historico-status`
    estiverem publicados e validados no Xano; desligado por padrão.
    """
    return os.getenv(VARIAVEL_ACOMPANHAMENTO_SOLICITANTE, "").strip().lower() == "true"


@dataclass(frozen=True)
class ItemNavegacao:
    """Destino autenticado e perfis que podem descobri-lo na interface."""

    rotulo: str
    rota: str
    icone: str
    perfis: frozenset[str]
    rotas_ativas: frozenset[str]
    requer_acompanhamento_publicado: bool = False


ITENS_NAVEGACAO = (
    ItemNavegacao(
        "Início",
        "/inicio",
        "house",
        PERFIS_OFICIAIS,
        frozenset({
            "/inicio",
            "/chamados",
            "/chamados/novo",
            "/chamados/[chamado_id]",
        }),
    ),
    # A visibilidade do item não é autorização: o Xano decide pelo vínculo.
    ItemNavegacao(
        "Chamados solicitados",
        "/chamados/solicitados",
        "inbox",
        PERFIS_OFICIAIS,
        frozenset({"/chamados/solicitados", "/chamados/solicitados/[chamado_id]"}),
        requer_acompanhamento_publicado=True,
    ),
    ItemNavegacao(
        "Monitoramento",
        "/monitoramento",
        "monitor",
        frozenset({"tecnico", "diretoria", "administrador"}),
        frozenset({"/monitoramento"}),
    ),
    ItemNavegacao(
        "Administração",
        "/administracao/gestao",
        "settings",
        frozenset({"administrador"}),
        frozenset({"/administracao/gestao"}),
    ),
)


def item_liberado(item: ItemNavegacao) -> bool:
    """Destino cujo backend ainda não foi publicado não aparece na navegação."""
    return not item.requer_acompanhamento_publicado or acompanhamento_solicitante_publicado()


def itens_visiveis(role: str) -> tuple[ItemNavegacao, ...]:
    """Retorna os destinos aprovados e liberados somente para um perfil oficial."""
    if role not in PERFIS_OFICIAIS:
        return ()
    return tuple(
        item for item in ITENS_NAVEGACAO if role in item.perfis and item_liberado(item)
    )


def item_esta_ativo(item: ItemNavegacao, rota_atual: str) -> bool:
    """Determina o item ativo por padrões canônicos de rota do Reflex."""
    return rota_atual in item.rotas_ativas
