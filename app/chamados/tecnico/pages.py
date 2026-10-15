"""Páginas da fila e detalhe de chamados do Técnico."""

import reflex as rx

from app.chamados.shared import cabecalho, erro
from app.chamados.tecnico.state import ChamadosTecnicoState
from app.components.layout import casca_conteudo, estado_carregamento, estado_revalidacao
from app.states.auth import AuthState


def _fila_tecnico() -> rx.Component:
    return rx.vstack(
        cabecalho("Fila técnica", "Consulte a fila global e a distribuição atual dos chamados."),
        rx.cond(
            AuthState.role == "tecnico",
            rx.hstack(
                rx.button(
                    "Todos",
                    variant=rx.cond(
                        ChamadosTecnicoState.escopo_rapido == "todos",
                        "solid",
                        "outline",
                    ),
                    on_click=ChamadosTecnicoState.selecionar_escopo_rapido("todos"),
                    disabled=ChamadosTecnicoState.carregando_fila,
                ),
                rx.button(
                    "Atribuídos a mim",
                    variant=rx.cond(
                        ChamadosTecnicoState.escopo_rapido == "atribuidos_a_mim",
                        "solid",
                        "outline",
                    ),
                    on_click=ChamadosTecnicoState.selecionar_escopo_rapido("atribuidos_a_mim"),
                    disabled=ChamadosTecnicoState.carregando_fila,
                ),
            ),
        ),
        rx.card(
            rx.vstack(
                rx.text("Filtros", weight="bold"),
                rx.hstack(
                    rx.input(
                        value=ChamadosTecnicoState.filtro_numero,
                        placeholder="Número do chamado",
                        on_change=ChamadosTecnicoState.alterar_filtro_numero,
                        type="number",
                        min="1",
                        aria_label="Pesquisar chamado por número",
                    ),
                    rx.select(
                        ChamadosTecnicoState.status_filtros(),
                        value=ChamadosTecnicoState.filtro_status,
                        on_change=ChamadosTecnicoState.alterar_filtro_status,
                        placeholder="Status",
                    ),
                    rx.select(
                        ChamadosTecnicoState.ativos,
                        value=ChamadosTecnicoState.filtro_ativo,
                        on_change=ChamadosTecnicoState.alterar_filtro_ativo,
                        placeholder="Totem",
                    ),
                    rx.input(
                        value=ChamadosTecnicoState.filtro_data_inicio,
                        on_change=ChamadosTecnicoState.alterar_filtro_data_inicio,
                        type="date",
                        aria_label="Abertura a partir de",
                    ),
                    rx.input(
                        value=ChamadosTecnicoState.filtro_data_fim,
                        on_change=ChamadosTecnicoState.alterar_filtro_data_fim,
                        type="date",
                        aria_label="Abertura até",
                    ),
                    rx.button(
                        "Aplicar",
                        on_click=ChamadosTecnicoState.aplicar_filtros,
                        disabled=ChamadosTecnicoState.carregando_fila,
                    ),
                    rx.button(
                        "Limpar filtros",
                        variant="outline",
                        on_click=ChamadosTecnicoState.limpar_filtros,
                        disabled=ChamadosTecnicoState.carregando_fila,
                    ),
                    wrap="wrap",
                    width="100%",
                ),
                rx.cond(
                    ChamadosTecnicoState.filtros_aplicados.length() > 0,
                    rx.hstack(
                        rx.text("Aplicados:", size="2", weight="medium"),
                        rx.foreach(
                            ChamadosTecnicoState.filtros_aplicados,
                            lambda filtro: rx.badge(filtro, color_scheme="gray"),
                        ),
                        wrap="wrap",
                    ),
                ),
                align="start",
                spacing="3",
                width="100%",
            ),
            width="100%",
        ),
        erro(ChamadosTecnicoState.mensagem_fila),
        erro(ChamadosTecnicoState.mensagem_assuncao),
        rx.cond(
            ChamadosTecnicoState.mensagem_sucesso_responsavel != "",
            rx.callout(
                ChamadosTecnicoState.mensagem_sucesso_responsavel,
                icon="check",
                color_scheme="green",
            ),
        ),
        rx.cond(
            ChamadosTecnicoState.carregando_fila,
            rx.center(rx.spinner(size="3"), width="100%", padding="4rem"),
            rx.cond(
                ChamadosTecnicoState.mensagem_fila != "",
                rx.fragment(),
                rx.cond(
                    ChamadosTecnicoState.chamados.length() == 0,
                    rx.callout("Nenhum chamado encontrado.", icon="info"),
                    rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("Número"),
                                rx.table.column_header_cell("Título"),
                                rx.table.column_header_cell("Status"),
                                rx.table.column_header_cell("Prioridade"),
                                rx.table.column_header_cell("Totem"),
                                rx.table.column_header_cell("Categoria"),
                                rx.table.column_header_cell("Responsável"),
                                rx.table.column_header_cell("Atribuído em"),
                                rx.table.column_header_cell("Ações"),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                ChamadosTecnicoState.chamados,
                                lambda item: rx.table.row(
                                    rx.table.cell(
                                        rx.link(
                                            "#" + item["id"].to_string(),
                                            href="/tecnico/chamados/" + item["id"].to_string(),
                                        )
                                    ),
                                    rx.table.cell(item["titulo"]),
                                    rx.table.cell(rx.badge(item["status"])),
                                    rx.table.cell(item["prioridade"]),
                                    rx.table.cell(item["ativo_nome"]),
                                    rx.table.cell(item["categoria_nome"]),
                                    rx.table.cell(item["tecnico_nome"]),
                                    rx.table.cell(item["atribuido_em_texto"]),
                                    rx.table.cell(
                                        rx.hstack(
                                            rx.link(
                                                "Ver detalhe",
                                                href="/tecnico/chamados/" + item["id"].to_string(),
                                            ),
                                            rx.cond(
                                                (AuthState.role == "tecnico") & item["pode_assumir"],
                                                rx.button(
                                                    rx.cond(
                                                        ChamadosTecnicoState.assumindo_id == item["id"],
                                                        "Assumindo...",
                                                        "Assumir",
                                                    ),
                                                    on_click=ChamadosTecnicoState.assumir(item["id"]),
                                                    disabled=ChamadosTecnicoState.assumindo_id != None,
                                                ),
                                                rx.fragment(),
                                            ),
                                            spacing="3",
                                        )
                                    ),
                                ),
                            )
                        ),
                        width="100%",
                    ),
                        overflow_x="auto",
                        width="100%",
                    ),
                ),
            ),
        ),
        spacing="5",
        width="100%",
    )


def _detalhe_tecnico() -> rx.Component:
    return rx.vstack(
        cabecalho("Detalhe técnico", "Consulta global, responsável e histórico do chamado."),
        erro(ChamadosTecnicoState.mensagem_detalhe_tecnico),
        erro(ChamadosTecnicoState.mensagem_assuncao),
        erro(ChamadosTecnicoState.mensagem_responsavel),
        rx.cond(
            ChamadosTecnicoState.mensagem_sucesso_responsavel != "",
            rx.callout(
                ChamadosTecnicoState.mensagem_sucesso_responsavel,
                icon="check",
                color_scheme="green",
            ),
        ),
        rx.cond(
            ChamadosTecnicoState.carregando_detalhe_tecnico,
            rx.spinner(size="3"),
            rx.cond(
                ChamadosTecnicoState.detalhe_tecnico_carregado,
                rx.card(
                rx.vstack(
                    rx.text("Chamado #" + ChamadosTecnicoState.chamado["id"].to_string(), weight="bold"),
                    rx.heading(ChamadosTecnicoState.chamado["titulo"], size="5"),
                    rx.text(ChamadosTecnicoState.chamado["descricao"], white_space="pre-wrap"),
                    rx.text("Status: " + ChamadosTecnicoState.chamado["status"]),
                    rx.text("Prioridade: " + ChamadosTecnicoState.chamado["prioridade"]),
                    rx.text("Origem: " + ChamadosTecnicoState.chamado["origem"]),
                    rx.text("Loja: " + ChamadosTecnicoState.chamado["loja_nome"]),
                    rx.text("Totem: " + ChamadosTecnicoState.chamado["ativo_nome"]),
                    rx.text("Categoria: " + ChamadosTecnicoState.chamado["categoria_nome"]),
                    rx.text("Solicitante: " + ChamadosTecnicoState.chamado["solicitante_nome"]),
                    rx.cond(
                        ChamadosTecnicoState.chamado["criador_sistema_nome"] != "",
                        rx.text(
                            "Criado por: "
                            + ChamadosTecnicoState.chamado["criador_sistema_nome"]
                        ),
                    ),
                    rx.text("SLA aplicado: " + ChamadosTecnicoState.chamado["sla_horas_texto"]),
                    rx.text("Técnico: " + ChamadosTecnicoState.chamado["tecnico_nome"]),
                    rx.text("Atribuído em: " + ChamadosTecnicoState.chamado["atribuido_em_texto"]),
                    rx.text("Aberto em: " + ChamadosTecnicoState.chamado["criado_em_texto"], color="gray"),
                    rx.text(
                        "Última atualização: "
                        + ChamadosTecnicoState.chamado["ultima_atualizacao_em_texto"],
                        color="gray",
                    ),
                    rx.cond(
                        (AuthState.role == "tecnico")
                        & ChamadosTecnicoState.chamado["pode_assumir"],
                        rx.button(
                            rx.cond(ChamadosTecnicoState.assumindo_id != None, "Assumindo...", "Assumir"),
                            on_click=ChamadosTecnicoState.assumir(ChamadosTecnicoState.chamado["id"]),
                            disabled=ChamadosTecnicoState.assumindo_id != None,
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        (
                            (AuthState.role == "tecnico")
                            | (AuthState.role == "diretoria")
                            | (AuthState.role == "administrador")
                        )
                        & ChamadosTecnicoState.chamado["pode_atribuir"],
                        rx.vstack(
                            rx.text("Atribuir ou reatribuir responsável", weight="bold"),
                            rx.select.root(
                                rx.select.trigger(
                                    placeholder="Selecione um Técnico",
                                    width="100%",
                                ),
                                rx.select.content(
                                    rx.foreach(
                                        ChamadosTecnicoState.tecnicos,
                                        lambda tecnico: rx.select.item(
                                            tecnico["nome"],
                                            value=tecnico["id"].to_string(),
                                        ),
                                    ),
                                ),
                                value=ChamadosTecnicoState.tecnico_alvo_id,
                                on_change=ChamadosTecnicoState.selecionar_tecnico_alvo,
                                width="100%",
                            ),
                            rx.button(
                                rx.cond(
                                    ChamadosTecnicoState.chamado["tecnico_nome"] == "Não atribuído",
                                    "Atribuir Técnico",
                                    "Reatribuir Técnico",
                                ),
                                on_click=ChamadosTecnicoState.atribuir_responsavel,
                                disabled=(
                                    (ChamadosTecnicoState.tecnico_alvo_id == "")
                                    | (ChamadosTecnicoState.alterando_responsavel_id != None)
                                    | (ChamadosTecnicoState.assumindo_id != None)
                                ),
                            ),
                            align="start",
                            spacing="2",
                            width="100%",
                        ),
                        rx.fragment(),
                    ),
                    rx.cond(
                        ChamadosTecnicoState.chamado["pode_liberar"],
                        rx.button(
                            rx.cond(
                                ChamadosTecnicoState.alterando_responsavel_id
                                == ChamadosTecnicoState.chamado["id"],
                                "Liberando...",
                                "Liberar responsável",
                            ),
                            on_click=ChamadosTecnicoState.liberar_responsavel,
                            disabled=(
                                (ChamadosTecnicoState.alterando_responsavel_id != None)
                                | (ChamadosTecnicoState.assumindo_id != None)
                            ),
                            variant="outline",
                        ),
                        rx.fragment(),
                    ),
                    align="start",
                    spacing="2",
                    width="100%",
                ),
                width="100%",
            ),
                rx.fragment(),
            ),
        ),
        rx.cond(
            (ChamadosTecnicoState.carregando_detalhe_tecnico == False)
            & (ChamadosTecnicoState.mensagem_detalhe_tecnico == "")
            & ChamadosTecnicoState.detalhe_tecnico_carregado,
            rx.vstack(
                rx.heading("Linha do tempo", size="4"),
                rx.cond(
                    ChamadosTecnicoState.timeline.length() == 0,
                    rx.callout(
                        "Nenhum comentário ou evento registrado.",
                        icon="info",
                    ),
                    rx.vstack(
                        rx.foreach(
                            ChamadosTecnicoState.timeline,
                            lambda item: rx.card(
                                rx.vstack(
                                    rx.hstack(
                                        rx.heading(item["titulo"], size="3"),
                                        rx.badge(item["visibilidade_texto"]),
                                        rx.text(item["criado_em_texto"], color="gray"),
                                        justify="between",
                                        width="100%",
                                    ),
                                    rx.text("Por: " + item["autor_nome"], color="gray"),
                                    rx.cond(
                                        item["conteudo"] != "",
                                        rx.text(item["conteudo"], white_space="pre-wrap"),
                                        rx.fragment(),
                                    ),
                                    rx.cond(
                                        item["tecnico_anterior_nome"] != "",
                                        rx.text("De: " + item["tecnico_anterior_nome"]),
                                        rx.fragment(),
                                    ),
                                    rx.cond(
                                        item["tecnico_novo_nome"] != "",
                                        rx.text("Para: " + item["tecnico_novo_nome"]),
                                        rx.fragment(),
                                    ),
                                    align="start",
                                    spacing="2",
                                    width="100%",
                                ),
                                width="100%",
                            ),
                        ),
                        spacing="3",
                        width="100%",
                    ),
                ),
                spacing="5",
                width="100%",
            ),
            rx.fragment(),
        ),
        rx.link("Voltar à fila", href="/tecnico"),
        spacing="5",
        width="100%",
    )


def _protegida_fila_global(conteudo: rx.Component, evento) -> rx.Component:
    return rx.cond(
        AuthState.carregando,
        estado_carregamento(),
        rx.cond(
            AuthState.sessao_confirmada
            & (
                (AuthState.role == "tecnico")
                | (AuthState.role == "diretoria")
                | (AuthState.role == "administrador")
            ),
            casca_conteudo(conteudo, "/tecnico"),
            estado_revalidacao(evento),
        ),
    )


def tecnico_chamados() -> rx.Component:
    return _protegida_fila_global(_fila_tecnico(), ChamadosTecnicoState.carregar_fila)


def detalhe_chamado_tecnico() -> rx.Component:
    return _protegida_fila_global(
        _detalhe_tecnico(),
        ChamadosTecnicoState.carregar_detalhe_tecnico,
    )
