"""Trilhas de navegação para os destinos existentes do MIRA."""

import reflex as rx

from app.components.visual import TEXTO, TEXTO_SECUNDARIO
from app.states.auth import AuthState


def breadcrumbs(*itens: tuple[str, str | None]) -> rx.Component:
    """Renderiza ancestrais navegáveis e identifica a página atual."""
    segmentos = []
    for indice, (rotulo, destino) in enumerate(itens):
        atual = indice == len(itens) - 1
        segmentos.append(
            rx.el.li(
                *([rx.icon("chevron-right", size=14, aria_hidden=True)] if indice else []),
                rx.text(rotulo, as_="span", aria_current="page", color=TEXTO, weight="medium")
                if atual else rx.link(rotulo, href=destino, color=TEXTO_SECUNDARIO),
                display="flex", align_items="center", gap="0.5rem", min_width="0",
            )
        )
    return rx.el.nav(
        rx.el.ol(
            *segmentos,
            display="flex", flex_wrap="wrap", align_items="center", gap="0.5rem",
            list_style_type="none", margin="0", padding="0",
        ),
        aria_label="Caminho de navegação",
        class_name="mira-breadcrumbs", font_size="0.8125rem", line_height="1.5",
        color=TEXTO_SECUNDARIO,
    )


def breadcrumbs_pagina() -> rx.Component:
    """Usa as rotas canônicas; aliases mantêm o mesmo contexto até redirecionar."""
    destinos = {
        "/monitoramento": "Monitoramento",
        "/indicadores/disponibilidade": "Indicadores",
        "/administracao/gestao": "Administração",
        "/administracao": "Administração",
        "/administracao/usuarios": "Administração",
        "/chamados/novo": "Novo chamado",
        "/gerente/chamados/novo": "Novo chamado",
        "/chamados/[chamado_id]": "Detalhe do chamado",
        "/gerente/chamados/[chamado_id]": "Detalhe do chamado",
        "/tecnico/chamados/[chamado_id]": "Detalhe do chamado",
    }
    return rx.match(
        AuthState.router.page.path,
        *[(rota, breadcrumbs(("Início", "/inicio"), (rotulo, None)))
          for rota, rotulo in destinos.items()],
        breadcrumbs(("Início", None)),
    )
