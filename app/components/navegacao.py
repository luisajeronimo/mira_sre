"""Configuração central da navegação autenticada do MIRA."""

from __future__ import annotations

from dataclasses import dataclass
import os


PERFIS_OFICIAIS = frozenset(
    {"gerente", "tecnico", "diretoria", "administrador"}
)


@dataclass(frozen=True)
class ItemNavegacao:
    """Destino autenticado e perfis que podem descobri-lo na interface."""

    rotulo: str
    rota: str
    icone: str
    perfis: frozenset[str]
    rotas_ativas: frozenset[str]


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
    ItemNavegacao(
        "Monitoramento",
        "/monitoramento",
        "monitor",
        frozenset({"tecnico", "diretoria", "administrador"}),
        frozenset({"/monitoramento"}),
    ),
    ItemNavegacao(
        "Chamados solicitados",
        "/chamados/solicitados",
        "clipboard-list",
        PERFIS_OFICIAIS,
        frozenset({"/chamados/solicitados", "/chamados/solicitados/[chamado_id]"}),
    ),
    ItemNavegacao(
        "Administração",
        "/administracao/gestao",
        "settings",
        frozenset({"administrador"}),
        frozenset({"/administracao/gestao"}),
    ),
)


def itens_visiveis(role: str) -> tuple[ItemNavegacao, ...]:
    """Retorna os destinos aprovados somente para um perfil oficial."""
    if role not in PERFIS_OFICIAIS:
        return ()
    return tuple(
        item for item in ITENS_NAVEGACAO
        if role in item.perfis
        and (item.rota != "/chamados/solicitados" or os.getenv("MIRA_ACOMPANHAMENTO_SOLICITANTE_PUBLICADO", "false").lower() == "true")
    )


def item_esta_ativo(item: ItemNavegacao, rota_atual: str) -> bool:
    """Determina o item ativo por padrões canônicos de rota do Reflex."""
    return rota_atual in item.rotas_ativas
