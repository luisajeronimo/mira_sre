"""Configuração central da navegação autenticada do MIRA."""

from __future__ import annotations

from dataclasses import dataclass


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
        "Administração de usuários",
        "/administracao/usuarios",
        "settings",
        frozenset({"administrador"}),
        frozenset({"/administracao/usuarios"}),
    ),
)


def itens_visiveis(role: str) -> tuple[ItemNavegacao, ...]:
    """Retorna os destinos aprovados somente para um perfil oficial."""
    if role not in PERFIS_OFICIAIS:
        return ()
    return tuple(item for item in ITENS_NAVEGACAO if role in item.perfis)


def item_esta_ativo(item: ItemNavegacao, rota_atual: str) -> bool:
    """Determina o item ativo por padrões canônicos de rota do Reflex."""
    return rota_atual in item.rotas_ativas
