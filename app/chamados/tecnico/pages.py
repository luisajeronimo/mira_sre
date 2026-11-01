"""Páginas da fila e detalhe de chamados do Técnico."""

import reflex as rx

from app.chamados.shared import cabecalho, erro
from app.chamados.tecnico.state import ChamadosTecnicoState
from app.components.layout import casca_conteudo, estado_carregamento, estado_revalidacao
from app.components.visual import (
    BORDA,
    BORDA_ROSE_SUAVE,
    ESTILO_CAMPO_COMENTARIO,
    RAIO_CONTROLE,
    RAIO_SUPERFICIE,
    SOMBRA_BAIXA,
    SUPERFICIE,
    TEXTO,
    TEXTO_SECUNDARIO,
    acoes_filtro,
    badge_status,
    badge_visibilidade,
    cabecalho_detalhe_chamado,
    cabecalho_tabela_ordenavel,
    celula_tabela,
    campo_info,
    campo_rotulado,
    composicao_detalhe_chamado,
    painel_filtros,
    periodo_rotulado,
    rotulo_campo,
)
from app.states.auth import AuthState


def _fila_tecnico() -> rx.Component:
    return rx.vstack(
        cabecalho("Fila técnica", "Consulte a fila global e a distribuição atual dos chamados."),
        rx.cond(
            AuthState.role == "tecnico",
            rx.box(
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
                    spacing="2",
                ),
                background=SUPERFICIE,
                border=f"1px solid {BORDA}",
                border_radius=RAIO_SUPERFICIE,
                padding="0.5rem",
                box_shadow=SOMBRA_BAIXA,
                width="fit-content",
            ),
        ),
        painel_filtros(
                    campo_rotulado(
                        "Número do chamado",
                        rx.input(
                            value=ChamadosTecnicoState.filtro_numero,
                            placeholder="Número do chamado",
                            on_change=ChamadosTecnicoState.alterar_filtro_numero,
                            type="number",
                            min="1",
                            aria_label="Pesquisar chamado por número",
                            width="100%",
                        ),
                    ),
                    campo_rotulado(
                        "Status",
                        rx.select(
                            ChamadosTecnicoState.status_filtros(),
                            value=ChamadosTecnicoState.filtro_status,
                            on_change=ChamadosTecnicoState.alterar_filtro_status,
                            placeholder="Status",
                            width="100%",
                            text_transform="uppercase",
                        ),
                    ),
                    campo_rotulado(
                        "Prioridade",
                        rx.select(
                            ChamadosTecnicoState.prioridades_tratativa(),
                            value=ChamadosTecnicoState.filtro_prioridade,
                            on_change=ChamadosTecnicoState.alterar_filtro_prioridade,
                            placeholder="Prioridade",
                            width="100%",
                        ),
                    ),
                    campo_rotulado(
                        "Responsável",
                        rx.select(
                            ChamadosTecnicoState.responsaveis_filtro,
                            value=ChamadosTecnicoState.filtro_responsavel,
                            on_change=ChamadosTecnicoState.alterar_filtro_responsavel,
                            placeholder="Responsável",
                            width="100%",
                        ),
                    ),
                    campo_rotulado(
                        "Totem",
                        rx.select(
                            ChamadosTecnicoState.ativos,
                            value=ChamadosTecnicoState.filtro_ativo,
                            on_change=ChamadosTecnicoState.alterar_filtro_ativo,
                            placeholder="Totem",
                            width="100%",
                        ),
                    ),
                    campo_rotulado(
                        "Loja",
                        rx.select(
                            ChamadosTecnicoState.lojas,
                            value=ChamadosTecnicoState.filtro_loja,
                            on_change=ChamadosTecnicoState.alterar_filtro_loja,
                            placeholder="Loja",
                            width="100%",
                        ),
                    ),
                    periodo_rotulado(
                        "Abertura",
                        ChamadosTecnicoState.filtro_data_inicio,
                        ChamadosTecnicoState.filtro_data_fim,
                        ChamadosTecnicoState.alterar_periodo_abertura,
                        ChamadosTecnicoState.carregando_fila,
                        coluna="span 3",
                        largura="12rem",
                        altura="3.75rem",
                    ),
                    periodo_rotulado(
                        "Atualização",
                        ChamadosTecnicoState.filtro_ultima_atualizacao_inicio,
                        ChamadosTecnicoState.filtro_ultima_atualizacao_fim,
                        ChamadosTecnicoState.alterar_periodo_atualizacao,
                        ChamadosTecnicoState.carregando_fila,
                        coluna="span 3",
                        largura="12rem",
                        altura="3.75rem",
                    ),
                    acoes=acoes_filtro(
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
                        mostrar_rotulo=False,
                    ),
                    aplicados=rx.cond(
                    ChamadosTecnicoState.filtros_aplicados.length() > 0,
                    rx.hstack(
                        rx.text("Aplicados:", size="2", weight="medium"),
                        rx.foreach(
                            ChamadosTecnicoState.filtros_aplicados,
                            lambda filtro: rx.badge(
                                rx.text(filtro, text_transform="uppercase"),
                                color_scheme="gray",
                            ),
                        ),
                        wrap="wrap",
                    ),
                ),
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
                    rx.card(
                        rx.box(
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        cabecalho_tabela_ordenavel("Número", "numero", ChamadosTecnicoState.ordenar_por, ChamadosTecnicoState.direcao_ordenacao, ChamadosTecnicoState.ordenar_fila("numero"), ChamadosTecnicoState.carregando_fila, largura="7.7%"),
                                        cabecalho_tabela_ordenavel("Título", "titulo", ChamadosTecnicoState.ordenar_por, ChamadosTecnicoState.direcao_ordenacao, ChamadosTecnicoState.ordenar_fila("titulo"), ChamadosTecnicoState.carregando_fila, largura="23%"),
                                        cabecalho_tabela_ordenavel("Status", "status", ChamadosTecnicoState.ordenar_por, ChamadosTecnicoState.direcao_ordenacao, ChamadosTecnicoState.ordenar_fila("status"), ChamadosTecnicoState.carregando_fila, largura="7.7%"),
                                        cabecalho_tabela_ordenavel("Prioridade", "prioridade", ChamadosTecnicoState.ordenar_por, ChamadosTecnicoState.direcao_ordenacao, ChamadosTecnicoState.ordenar_fila("prioridade"), ChamadosTecnicoState.carregando_fila, largura="7.7%"),
                                        cabecalho_tabela_ordenavel("Totem", "totem", ChamadosTecnicoState.ordenar_por, ChamadosTecnicoState.direcao_ordenacao, ChamadosTecnicoState.ordenar_fila("totem"), ChamadosTecnicoState.carregando_fila, largura="7.7%"),
                                        cabecalho_tabela_ordenavel("Loja", "loja", ChamadosTecnicoState.ordenar_por, ChamadosTecnicoState.direcao_ordenacao, ChamadosTecnicoState.ordenar_fila("loja"), ChamadosTecnicoState.carregando_fila, largura="7.7%"),
                                        cabecalho_tabela_ordenavel("Categoria", "categoria", ChamadosTecnicoState.ordenar_por, ChamadosTecnicoState.direcao_ordenacao, ChamadosTecnicoState.ordenar_fila("categoria"), ChamadosTecnicoState.carregando_fila, largura="7.7%"),
                                        cabecalho_tabela_ordenavel("Aberto por", "aberto_por", ChamadosTecnicoState.ordenar_por, ChamadosTecnicoState.direcao_ordenacao, ChamadosTecnicoState.ordenar_fila("aberto_por"), ChamadosTecnicoState.carregando_fila, largura="7.7%"),
                                        cabecalho_tabela_ordenavel("Responsável", "responsavel", ChamadosTecnicoState.ordenar_por, ChamadosTecnicoState.direcao_ordenacao, ChamadosTecnicoState.ordenar_fila("responsavel"), ChamadosTecnicoState.carregando_fila, largura="7.7%"),
                                        cabecalho_tabela_ordenavel("Abertura", "criado_em", ChamadosTecnicoState.ordenar_por, ChamadosTecnicoState.direcao_ordenacao, ChamadosTecnicoState.ordenar_fila("criado_em"), ChamadosTecnicoState.carregando_fila, largura="7.7%"),
                                        cabecalho_tabela_ordenavel("Última atualização", "ultima_atualizacao_em", ChamadosTecnicoState.ordenar_por, ChamadosTecnicoState.direcao_ordenacao, ChamadosTecnicoState.ordenar_fila("ultima_atualizacao_em"), ChamadosTecnicoState.carregando_fila, largura="7.7%"),
                                    )
                                ),
                                rx.table.body(
                                    rx.foreach(
                                        ChamadosTecnicoState.chamados,
                                        lambda item: rx.table.row(
                                            celula_tabela(
                                                rx.link(
                                                    "#" + item["id"].to_string(),
                                                    href="/chamados/" + item["id"].to_string(),
                                                )
                                            ),
                                            celula_tabela(
                                                rx.vstack(
                                                    rx.text(item["titulo"], weight="medium"),
                                                    rx.text(
                                                        item["ocorrencia"],
                                                        size="2",
                                                        color="gray",
                                                    ),
                                                    align="start",
                                                    spacing="1",
                                                ),
                                                alinhamento="left",
                                            ),
                                            celula_tabela(badge_status(item["status"])),
                                            celula_tabela(item["prioridade"]),
                                            celula_tabela(item["ativo_nome"]),
                                            celula_tabela(item["loja_nome"]),
                                            celula_tabela(
                                                rx.text(
                                                    item["categoria_nome"],
                                                    max_width="9rem",
                                                    white_space="normal",
                                                    overflow_wrap="anywhere",
                                                )
                                            ),
                                            celula_tabela(item["aberto_por"]),
                                            celula_tabela(item["tecnico_nome"]),
                                            celula_tabela(item["criado_em_texto"]),
                                            celula_tabela(item["ultima_atualizacao_em_texto"]),
                                        )
                                    )
                                ),
                                width="100%",
                                style={"tableLayout": "fixed"},
                                min_width="0",
                                max_width="100%",
                                overflow_x="hidden",
                            ),
                            width="100%",
                        ),
                        width="100%",
                        padding="0",
                        background=SUPERFICIE,
                        border=f"1px solid {BORDA}",
                        border_radius=RAIO_SUPERFICIE,
                        box_shadow=SOMBRA_BAIXA,
                        overflow="hidden",
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
                composicao_detalhe_chamado(
                    rx.vstack(
                        cabecalho_detalhe_chamado(
                            ChamadosTecnicoState.chamado["id"].to_string(),
                            ChamadosTecnicoState.chamado["titulo"],
                            ChamadosTecnicoState.abrir_monitoramento_totem,
                        ),
                        rx.cond(
                            ChamadosTecnicoState.edicao_funcional_bloqueada,
                            rx.callout(
                                "Chamado terminal: campos funcionais bloqueados.",
                                icon="lock",
                                color_scheme="gray",
                            ),
                            rx.fragment(),
                        ),
                        rx.heading("Dados do chamado", size="3"),
                        rx.grid(
                            rx.vstack(
                                rotulo_campo("Status"),
                                rx.select(
                                    ChamadosTecnicoState.status_filtros(),
                                    value=ChamadosTecnicoState.status_pendente,
                                    on_change=ChamadosTecnicoState.alterar_status_pendente,
                                    disabled=ChamadosTecnicoState.edicao_funcional_bloqueada | ChamadosTecnicoState.salvando_tratativa,
                                    width="100%",
                                    text_transform="uppercase",
                                ),
                                align="start", width="100%",
                            ),
                            rx.vstack(
                                rotulo_campo("Prioridade"),
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
                                rotulo_campo("Responsável"),
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
                                rotulo_campo("Categoria"),
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
                            campo_info("Totem", ChamadosTecnicoState.chamado["ativo_nome"]),
                            campo_info("Loja", ChamadosTecnicoState.chamado["loja_nome"]),
                            campo_info("Solicitante", ChamadosTecnicoState.chamado["solicitante_nome"]),
                            campo_info(
                                "Origem",
                                rx.text(
                                    ChamadosTecnicoState.chamado["origem"],
                                    text_transform="uppercase",
                                ),
                            ),
                            campo_info("SLA aplicado", ChamadosTecnicoState.chamado["sla_horas_texto"]),
                            campo_info("Atribuído em", ChamadosTecnicoState.chamado["atribuido_em_texto"]),
                            campo_info("Aberto em", ChamadosTecnicoState.chamado["criado_em_texto"]),
                            campo_info("Última atualização", ChamadosTecnicoState.chamado["ultima_atualizacao_em_texto"]),
                            rx.cond(
                                ChamadosTecnicoState.chamado["criador_sistema_nome"] != "",
                                campo_info("Criado por", ChamadosTecnicoState.chamado["criador_sistema_nome"]),
                                rx.fragment(),
                            ),
                            columns="3",
                            spacing="4",
                            width="100%",
                        ),
                        align="start",
                        spacing="4",
                        width="100%",
                    ),
                    ChamadosTecnicoState.chamado["descricao"],
                    rx.vstack(
                        rx.vstack(
                            rotulo_campo("Comentário"),
                            rx.text_area(
                                value=ChamadosTecnicoState.comentario_status_pendente,
                                on_change=ChamadosTecnicoState.alterar_comentario_status_pendente,
                                placeholder="Registre uma atualização para o chamado",
                                disabled=ChamadosTecnicoState.salvando_tratativa,
                                width="100%",
                                **ESTILO_CAMPO_COMENTARIO,
                            ),
                            rotulo_campo("Visibilidade"),
                            rx.cond(
                                ChamadosTecnicoState.status_pendente_exige_comentario_publico,
                                badge_visibilidade("Público"),
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
                                        rx.vstack(
                                            rx.heading(item["titulo"], size="3"),
                                            rx.text("Por: " + item["autor_nome"], size="2", color=TEXTO_SECUNDARIO),
                                            align="start",
                                            spacing="1",
                                        ),
                                        rx.vstack(
                                            rx.text(item["criado_em_texto"], size="1", color=TEXTO_SECUNDARIO),
                                            badge_visibilidade(item["visibilidade_texto"]),
                                            align="end",
                                            spacing="2",
                                        ),
                                        justify="between",
                                        align="start",
                                        width="100%",
                                    ),
                                    rx.cond(
                                        item["conteudo"] != "",
                                        rx.text(item["conteudo"], white_space="pre-wrap"),
                                        rx.fragment(),
                                    ),
                                    rx.cond(
                                        item["comentario_conteudo"] != "",
                                        rx.vstack(
                                            rx.hstack(
                                                rx.text("Comentário", weight="bold"),
                                                badge_visibilidade(item["comentario_visibilidade_texto"]),
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
                                            rx.text("Alterações realizadas", weight="bold"),
                                            rx.grid(
                                                rx.foreach(
                                                item["alteracoes_detalhadas"],
                                                lambda alteracao: rx.vstack(
                                                    rx.text(alteracao["campo"], weight="bold", size="2"),
                                                    rx.text(alteracao["anterior"] + " → " + alteracao["resultante"], size="2"),
                                                    align="start",
                                                    spacing="0",
                                                    border=f"1px solid {BORDA_ROSE_SUAVE}",
                                                    border_radius=RAIO_CONTROLE,
                                                    padding="0.625rem",
                                                    width="100%",
                                                ),
                                            ),
                                                columns="2",
                                                gap="0.75rem",
                                                width="100%",
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
                                padding="1rem",
                                border=f"1px solid {BORDA_ROSE_SUAVE}",
                                border_radius=RAIO_SUPERFICIE,
                                box_shadow="none",
                                background=SUPERFICIE,
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
        rx.link("Voltar à fila", href="/inicio"),
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
