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
                        ChamadosTecnicoState.prioridades_tratativa(),
                        value=ChamadosTecnicoState.filtro_prioridade,
                        on_change=ChamadosTecnicoState.alterar_filtro_prioridade,
                        placeholder="Prioridade",
                    ),
                    rx.select(
                        ChamadosTecnicoState.responsaveis_filtro,
                        value=ChamadosTecnicoState.filtro_responsavel,
                        on_change=ChamadosTecnicoState.alterar_filtro_responsavel,
                        placeholder="Responsável",
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
                                _cabecalho_ordenavel("Número", "numero"),
                                _cabecalho_ordenavel("Título", "titulo"),
                                _cabecalho_ordenavel("Status", "status"),
                                _cabecalho_ordenavel("Prioridade", "prioridade"),
                                _cabecalho_ordenavel("Totem", "totem"),
                                _cabecalho_ordenavel("Categoria", "categoria"),
                                _cabecalho_ordenavel("Responsável", "responsavel"),
                                _cabecalho_ordenavel("Abertura", "criado_em"),
                                _cabecalho_ordenavel("Última atualização", "ultima_atualizacao_em"),
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
                                            href="/chamados/" + item["id"].to_string(),
                                        )
                                    ),
                                    rx.table.cell(item["titulo"]),
                                    rx.table.cell(rx.badge(item["status"])),
                                    rx.table.cell(item["prioridade"]),
                                    rx.table.cell(item["ativo_nome"]),
                                    rx.table.cell(item["categoria_nome"]),
                                    rx.table.cell(item["tecnico_nome"]),
                                    rx.table.cell(item["criado_em_texto"]),
                                    rx.table.cell(item["ultima_atualizacao_em_texto"]),
                                    rx.table.cell(
                                        rx.hstack(
                                            rx.link(
                                                "Ver detalhe",
                                                href="/chamados/" + item["id"].to_string(),
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


def _cabecalho_ordenavel(rotulo: str, coluna: str) -> rx.Component:
    return rx.table.column_header_cell(
        rx.button(
            rotulo,
            variant="ghost",
            on_click=ChamadosTecnicoState.ordenar_fila(coluna),
            disabled=ChamadosTecnicoState.carregando_fila,
        )
    )


def _detalhe_tecnico() -> rx.Component:
    return rx.vstack(
        cabecalho("Detalhe técnico", "Consulta global, responsável e histórico do chamado."),
        erro(ChamadosTecnicoState.mensagem_detalhe_tecnico),
        erro(ChamadosTecnicoState.mensagem_tratativa),
        rx.cond(
            ChamadosTecnicoState.mensagem_sucesso_tratativa != "",
            rx.callout(
                ChamadosTecnicoState.mensagem_sucesso_tratativa,
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
                        rx.text(
                            "Chamado #" + ChamadosTecnicoState.chamado["id"].to_string(),
                            weight="bold",
                        ),
                        rx.heading(ChamadosTecnicoState.chamado["titulo"], size="5"),
                        rx.cond(
                            ChamadosTecnicoState.edicao_funcional_bloqueada,
                            rx.callout(
                                "Chamado terminal: campos funcionais bloqueados.",
                                icon="lock",
                                color_scheme="gray",
                            ),
                            rx.fragment(),
                        ),
                        rx.grid(
                            rx.vstack(
                                rx.text("Status", size="2"),
                                rx.select(
                                    ChamadosTecnicoState.status_filtros(),
                                    value=ChamadosTecnicoState.status_pendente,
                                    on_change=ChamadosTecnicoState.alterar_status_pendente,
                                    disabled=ChamadosTecnicoState.edicao_funcional_bloqueada | ChamadosTecnicoState.salvando_tratativa,
                                    width="100%",
                                ),
                                align="start", width="100%",
                            ),
                            rx.vstack(
                                rx.text("Prioridade", size="2"),
                                rx.select(
                                    ChamadosTecnicoState.prioridades_tratativa(),
                                    value=ChamadosTecnicoState.prioridade_pendente,
                                    on_change=ChamadosTecnicoState.alterar_prioridade_pendente,
                                    disabled=ChamadosTecnicoState.edicao_funcional_bloqueada | ChamadosTecnicoState.salvando_tratativa,
                                    width="100%",
                                ),
                                align="start", width="100%",
                            ),
                            rx.vstack(
                                rx.text("Responsável", size="2"),
                                rx.select.root(
                                    rx.select.trigger(width="100%"),
                                    rx.select.content(
                                        rx.select.item("Não atribuído", value="0"),
                                        rx.foreach(
                                            ChamadosTecnicoState.tecnicos,
                                            lambda tecnico: rx.select.item(
                                                tecnico["nome"],
                                                value=tecnico["id"].to_string(),
                                            ),
                                        ),
                                    ),
                                    value=ChamadosTecnicoState.responsavel_pendente_id,
                                    on_change=ChamadosTecnicoState.alterar_responsavel_pendente,
                                    disabled=ChamadosTecnicoState.edicao_funcional_bloqueada | ChamadosTecnicoState.salvando_tratativa,
                                    width="100%",
                                ),
                                align="start", width="100%",
                            ),
                            rx.vstack(
                                rx.text("Categoria", size="2"),
                                rx.cond(
                                    ChamadosTecnicoState.categoria_confirmada_inativa,
                                    rx.text(
                                        "Categoria atual inativa: " + ChamadosTecnicoState.chamado["categoria_nome"],
                                        size="2",
                                        color="gray",
                                    ),
                                    rx.fragment(),
                                ),
                                rx.select.root(
                                    rx.select.trigger(width="100%"),
                                    rx.select.content(
                                        rx.cond(
                                            ChamadosTecnicoState.categoria_confirmada_inativa,
                                            rx.select.item(
                                                ChamadosTecnicoState.chamado["categoria_nome"],
                                                value=ChamadosTecnicoState.categoria_pendente_id,
                                                disabled=True,
                                            ),
                                            rx.fragment(),
                                        ),
                                        rx.foreach(
                                            ChamadosTecnicoState.categorias_tratativa,
                                            lambda categoria: rx.select.item(
                                                categoria["nome"],
                                                value=categoria["id"].to_string(),
                                            ),
                                        ),
                                    ),
                                    value=ChamadosTecnicoState.categoria_pendente_id,
                                    on_change=ChamadosTecnicoState.alterar_categoria_pendente,
                                    disabled=ChamadosTecnicoState.edicao_funcional_bloqueada | ChamadosTecnicoState.salvando_tratativa,
                                    width="100%",
                                ),
                                align="start", width="100%",
                            ),
                            rx.vstack(rx.text("Totem", size="2"), rx.text(ChamadosTecnicoState.chamado["ativo_nome"]), align="start", width="100%"),
                            rx.vstack(rx.text("Loja", size="2"), rx.text(ChamadosTecnicoState.chamado["loja_nome"]), align="start", width="100%"),
                            rx.vstack(rx.text("Solicitante", size="2"), rx.text(ChamadosTecnicoState.chamado["solicitante_nome"]), align="start", width="100%"),
                            rx.vstack(
                                rx.text("Origem: " + ChamadosTecnicoState.chamado["origem"], size="2"),
                                align="start",
                                width="100%",
                            ),
                            rx.vstack(rx.text("SLA aplicado", size="2"), rx.text(ChamadosTecnicoState.chamado["sla_horas_texto"]), align="start", width="100%"),
                            rx.vstack(rx.text("Atribuído em", size="2"), rx.text(ChamadosTecnicoState.chamado["atribuido_em_texto"]), align="start", width="100%"),
                            rx.vstack(rx.text("Aberto em", size="2"), rx.text(ChamadosTecnicoState.chamado["criado_em_texto"]), align="start", width="100%"),
                            rx.vstack(rx.text("Última atualização", size="2"), rx.text(ChamadosTecnicoState.chamado["ultima_atualizacao_em_texto"]), align="start", width="100%"),
                            rx.cond(
                                ChamadosTecnicoState.chamado["criador_sistema_nome"] != "",
                                rx.vstack(
                                    rx.text(
                                        "Criado por: "
                                        + ChamadosTecnicoState.chamado["criador_sistema_nome"],
                                        size="2",
                                    ),
                                    align="start",
                                    width="100%",
                                ),
                                rx.fragment(),
                            ),
                            columns=rx.breakpoints(initial="1", sm="2", lg="3"),
                            spacing="4",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Descrição", size="2"),
                            rx.text(
                                ChamadosTecnicoState.chamado["descricao"],
                                white_space="pre-wrap",
                            ),
                            align="start",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Comentário", size="2"),
                            rx.text_area(
                                value=ChamadosTecnicoState.comentario_status_pendente,
                                on_change=ChamadosTecnicoState.alterar_comentario_status_pendente,
                                placeholder="Registre uma atualização para o chamado",
                                disabled=ChamadosTecnicoState.salvando_tratativa,
                                width="100%",
                            ),
                            rx.text("Visibilidade", size="2"),
                            rx.cond(
                                ChamadosTecnicoState.status_pendente_exige_comentario_publico,
                                rx.badge("Público", color_scheme="blue"),
                                rx.select.root(
                                    rx.select.trigger(width="100%"),
                                    rx.select.content(
                                        rx.select.item("Público", value="publica"),
                                        rx.select.item("Interno", value="interna"),
                                    ),
                                    value=ChamadosTecnicoState.visibilidade_comentario_status_pendente,
                                    on_change=ChamadosTecnicoState.alterar_visibilidade_comentario_status_pendente,
                                    disabled=ChamadosTecnicoState.salvando_tratativa,
                                    width="100%",
                                ),
                            ),
                            align="start",
                            width="100%",
                        ),
                        rx.hstack(
                            rx.button(
                                "Descartar mudanças",
                                variant="outline",
                                on_click=ChamadosTecnicoState.descartar_mudancas_tratativa,
                                disabled=(ChamadosTecnicoState.ha_rascunho_pendente == False) | ChamadosTecnicoState.salvando_tratativa,
                            ),
                            rx.button(
                                rx.cond(ChamadosTecnicoState.salvando_tratativa, "Salvando...", "Salvar"),
                                on_click=ChamadosTecnicoState.salvar_tratativa,
                                disabled=(ChamadosTecnicoState.pode_salvar_tratativa == False) | ChamadosTecnicoState.salvando_tratativa,
                            ),
                            justify="end",
                            width="100%",
                            spacing="3",
                        ),
                        align="start",
                        spacing="4",
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
                                        item["comentario_conteudo"] != "",
                                        rx.vstack(
                                            rx.hstack(
                                                rx.text("Comentário", weight="medium"),
                                                rx.badge(item["comentario_visibilidade_texto"]),
                                                spacing="2",
                                            ),
                                            rx.text(item["comentario_conteudo"], white_space="pre-wrap"),
                                            align="start",
                                            spacing="1",
                                            width="100%",
                                        ),
                                        rx.fragment(),
                                    ),
                                    rx.cond(
                                        item["alteracoes_detalhadas"].length() > 0,
                                        rx.vstack(
                                            rx.text("Alterações realizadas", weight="medium"),
                                            rx.foreach(
                                                item["alteracoes_detalhadas"],
                                                lambda alteracao: rx.vstack(
                                                    rx.text(alteracao["campo"], weight="medium", size="2"),
                                                    rx.text(alteracao["anterior"] + " → " + alteracao["resultante"], size="2"),
                                                    align="start",
                                                    spacing="0",
                                                    width="100%",
                                                ),
                                            ),
                                            align="start",
                                            spacing="2",
                                            width="100%",
                                        ),
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
        rx.link("Voltar à fila", href="/chamados"),
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
            casca_conteudo(conteudo, "/inicio"),
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
