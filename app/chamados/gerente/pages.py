"""Páginas da jornada de chamados do Gerente."""

import reflex as rx

from app.chamados.gerente.state import ChamadosGerenteState
from app.chamados.shared import cabecalho, erro
from app.components.layout import casca_conteudo, estado_carregamento, estado_revalidacao
from app.states.auth import AuthState


def _cabecalho_ordenavel(texto: str, coluna: str) -> rx.Component:
    return rx.table.column_header_cell(
        rx.button(
            rx.hstack(
                rx.text(texto),
                rx.cond(
                    ChamadosGerenteState.ordenar_por == coluna,
                    rx.text(ChamadosGerenteState.direcao),
                    rx.text("Ordenar"),
                ),
                spacing="1",
                align="center",
            ),
            on_click=ChamadosGerenteState.alternar_ordenacao(coluna),
            variant="ghost",
            aria_label="Ordenar por " + texto,
        )
    )


def _lista() -> rx.Component:
    return rx.vstack(
        cabecalho("Chamados", "Acompanhe os chamados da sua loja."),
        rx.hstack(
            rx.link(
                rx.button("Criar chamado", color_scheme="pink"),
                href="/gerente/chamados/novo",
            ),
            justify="end",
            width="100%",
        ),
        rx.card(
            rx.vstack(
                rx.text("Filtros", weight="bold"),
                rx.hstack(
                    rx.input(
                        value=ChamadosGerenteState.filtro_numero,
                        on_change=ChamadosGerenteState.alterar_filtro_numero,
                        type="number",
                        min="1",
                        placeholder="Número",
                    ),
                    rx.select(
                        ChamadosGerenteState.status_filtros(),
                        value=ChamadosGerenteState.filtro_status,
                        on_change=ChamadosGerenteState.alterar_filtro_status,
                        placeholder="Status",
                    ),
                    rx.select(
                        ChamadosGerenteState.ativos,
                        value=ChamadosGerenteState.filtro_ativo,
                        on_change=ChamadosGerenteState.alterar_filtro_ativo,
                        placeholder="Totem",
                    ),
                    rx.input(
                        value=ChamadosGerenteState.filtro_data_inicio,
                        on_change=ChamadosGerenteState.alterar_filtro_data_inicio,
                        type="date",
                        aria_label="Abertura a partir de",
                    ),
                    rx.input(
                        value=ChamadosGerenteState.filtro_data_fim,
                        on_change=ChamadosGerenteState.alterar_filtro_data_fim,
                        type="date",
                        aria_label="Abertura até",
                    ),
                    rx.button("Aplicar", on_click=ChamadosGerenteState.aplicar_filtros),
                    rx.button(
                        "Limpar filtros",
                        variant="outline",
                        on_click=ChamadosGerenteState.limpar_filtros_lista,
                    ),
                    wrap="wrap",
                    width="100%",
                ),
                rx.cond(
                    ChamadosGerenteState.filtros_aplicados.length() > 0,
                    rx.hstack(
                        rx.text("Aplicados:", size="2", weight="medium"),
                        rx.foreach(
                            ChamadosGerenteState.filtros_aplicados,
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
        rx.text(
            ChamadosGerenteState.total_chamados.to_string()
            + " chamados • "
            + ChamadosGerenteState.chamados.length().to_string()
            + " exibidos",
            color="gray",
            size="2",
        ),
        erro(ChamadosGerenteState.mensagem_chamados),
        rx.cond(
            ChamadosGerenteState.carregando_chamados,
            rx.center(rx.spinner(size="3"), width="100%", padding="4rem"),
            rx.cond(
                ChamadosGerenteState.chamados.length() == 0,
                rx.callout("Nenhum chamado encontrado.", icon="info"),
                rx.box(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                _cabecalho_ordenavel("Número", "numero"),
                                _cabecalho_ordenavel("Título + ocorrência", "titulo"),
                                _cabecalho_ordenavel("Status", "status"),
                                _cabecalho_ordenavel("Prioridade", "prioridade"),
                                _cabecalho_ordenavel("Totem", "totem"),
                                _cabecalho_ordenavel("Categoria", "categoria"),
                                _cabecalho_ordenavel("Data de abertura", "criado_em"),
                                _cabecalho_ordenavel(
                                    "Data da última atualização",
                                    "ultima_atualizacao_em",
                                ),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                ChamadosGerenteState.chamados,
                                lambda item: rx.table.row(
                                    rx.table.cell(
                                        rx.link(
                                            "#" + item["id"].to_string(),
                                            href="/gerente/chamados/"
                                            + item["id"].to_string(),
                                        )
                                    ),
                                    rx.table.cell(
                                        rx.vstack(
                                            rx.text(item["titulo"], weight="medium"),
                                            rx.text(
                                                item["ocorrencia"],
                                                size="2",
                                                color="gray",
                                            ),
                                            align="start",
                                            spacing="1",
                                        )
                                    ),
                                    rx.table.cell(rx.badge(item["status"])),
                                    rx.table.cell(item["prioridade"]),
                                    rx.table.cell(item["ativo_nome"]),
                                    rx.table.cell(item["categoria_nome"]),
                                    rx.table.cell(item["criado_em_texto"]),
                                    rx.table.cell(
                                        item["ultima_atualizacao_em_texto"]
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
        spacing="5",
        width="100%",
    )


def _formulario() -> rx.Component:
    return rx.vstack(
        cabecalho("Criar chamado", "Registre uma solicitação para sua loja."),
        erro(ChamadosGerenteState.mensagem_formulario),
        rx.vstack(
            rx.select.root(
                rx.select.trigger(placeholder="Selecione o Totem", width="100%"),
                rx.select.content(
                    rx.foreach(
                        ChamadosGerenteState.ativos_formulario,
                        lambda ativo: rx.select.item(
                            ativo["nome"],
                            value=ativo["id"].to_string(),
                        ),
                    ),
                ),
                value=ChamadosGerenteState.ativo_formulario,
                on_change=ChamadosGerenteState.alterar_ativo_formulario,
                width="100%",
            ),
            rx.select.root(
                rx.select.trigger(placeholder="Selecione a categoria", width="100%"),
                rx.select.content(
                    rx.foreach(
                        ChamadosGerenteState.categorias_formulario,
                        lambda categoria: rx.select.item(
                            categoria["nome"],
                            value=categoria["id"].to_string(),
                        ),
                    ),
                ),
                value=ChamadosGerenteState.categoria_formulario,
                on_change=ChamadosGerenteState.alterar_categoria_formulario,
                width="100%",
            ),
            rx.select(
                ChamadosGerenteState.prioridades(),
                value=ChamadosGerenteState.prioridade_formulario,
                on_change=ChamadosGerenteState.alterar_prioridade_formulario,
                placeholder="Selecione a prioridade",
                width="100%",
            ),
            rx.input(
                value=ChamadosGerenteState.titulo_formulario,
                on_change=ChamadosGerenteState.alterar_titulo_formulario,
                placeholder="Título",
                width="100%",
            ),
            rx.text_area(
                value=ChamadosGerenteState.descricao_formulario,
                on_change=ChamadosGerenteState.alterar_descricao_formulario,
                placeholder="Descrição detalhada",
                width="100%",
            ),
            rx.hstack(
                rx.button(
                    rx.cond(ChamadosGerenteState.enviando, "Enviando...", "Salvar"),
                    on_click=ChamadosGerenteState.abrir_chamado,
                    disabled=ChamadosGerenteState.enviando,
                    color_scheme="pink",
                ),
                rx.button(
                    "Limpar",
                    variant="outline",
                    on_click=ChamadosGerenteState.limpar_formulario,
                    disabled=ChamadosGerenteState.enviando,
                ),
                rx.button(
                    "Descartar",
                    variant="outline",
                    on_click=ChamadosGerenteState.descartar_formulario,
                    disabled=ChamadosGerenteState.enviando,
                ),
                rx.button(
                    "Voltar para lista de chamados",
                    variant="ghost",
                    on_click=ChamadosGerenteState.voltar_para_lista,
                    disabled=ChamadosGerenteState.enviando,
                ),
                wrap="wrap",
                spacing="3",
            ),
            spacing="3",
            width="100%",
        ),
        spacing="5",
        width="100%",
    )


def _detalhe() -> rx.Component:
    return rx.vstack(
        cabecalho("Detalhe do chamado", "Consulta somente leitura."),
        erro(ChamadosGerenteState.mensagem_detalhe),
        rx.cond(
            ChamadosGerenteState.carregando_detalhe,
            rx.spinner(size="3"),
            rx.cond(
                ChamadosGerenteState.detalhe_carregado,
                rx.card(
                    rx.vstack(
                        rx.text("Chamado #" + ChamadosGerenteState.chamado["id"].to_string(), weight="bold"),
                        rx.heading(ChamadosGerenteState.chamado["titulo"], size="5"),
                        rx.text(ChamadosGerenteState.chamado["descricao"], white_space="pre-wrap"),
                        rx.text("Status: " + ChamadosGerenteState.chamado["status"]),
                        rx.text("Prioridade: " + ChamadosGerenteState.chamado["prioridade"]),
                        rx.text("Origem: " + ChamadosGerenteState.chamado["origem"]),
                        rx.text("Totem: " + ChamadosGerenteState.chamado["ativo_nome"]),
                        rx.text("Categoria: " + ChamadosGerenteState.chamado["categoria_nome"]),
                        rx.text("Solicitante: " + ChamadosGerenteState.chamado["solicitante_nome"]),
                        rx.text("Técnico: " + ChamadosGerenteState.chamado["tecnico_nome"]),
                        rx.cond(
                            ChamadosGerenteState.chamado["criador_sistema_nome"] != "",
                            rx.text(
                                "Criado por: "
                                + ChamadosGerenteState.chamado["criador_sistema_nome"]
                            ),
                        ),
                        rx.text("SLA aplicado: " + ChamadosGerenteState.chamado["sla_horas_texto"]),
                        rx.text("Aberto em: " + ChamadosGerenteState.chamado["criado_em_texto"], color="gray"),
                        rx.text(
                            "Última atualização: "
                            + ChamadosGerenteState.chamado["ultima_atualizacao_em_texto"],
                            color="gray",
                        ),
                        align="start",
                        spacing="2",
                    ),
                    width="100%",
                ),
                rx.fragment(),
            ),
        ),
        rx.cond(
            ChamadosGerenteState.detalhe_carregado,
            rx.vstack(
                rx.heading("Comentários", size="5"),
                erro(ChamadosGerenteState.mensagem_comentarios),
                rx.cond(
                    ChamadosGerenteState.carregando_comentarios,
                    rx.spinner(size="2"),
                    rx.cond(
                        ChamadosGerenteState.comentarios.length() == 0,
                        rx.text("Nenhum comentário público.", color="gray"),
                        rx.vstack(
                            rx.foreach(
                                ChamadosGerenteState.comentarios,
                                lambda comentario: rx.card(
                                    rx.vstack(
                                        rx.text(comentario["conteudo"], white_space="pre-wrap"),
                                        rx.text(
                                            comentario["autor_nome"]
                                            + " • "
                                            + comentario["criado_em_texto"],
                                            size="2",
                                            color="gray",
                                        ),
                                        align="start",
                                        spacing="1",
                                    ),
                                    width="100%",
                                ),
                            ),
                            width="100%",
                            spacing="2",
                        ),
                    ),
                ),
                rx.cond(
                    (ChamadosGerenteState.chamado["status"] != "Encerrado")
                    & (ChamadosGerenteState.chamado["status"] != "Cancelado"),
                    rx.vstack(
                        rx.text_area(
                            value=ChamadosGerenteState.rascunho_comentario,
                            on_change=ChamadosGerenteState.alterar_rascunho_comentario,
                            placeholder="Adicionar comentário público",
                            width="100%",
                        ),
                        rx.hstack(
                            rx.button(
                                rx.cond(
                                    ChamadosGerenteState.enviando_comentario,
                                    "Enviando...",
                                    "Postar comentário",
                                ),
                                on_click=ChamadosGerenteState.publicar_comentario,
                                disabled=ChamadosGerenteState.enviando_comentario,
                            ),
                            rx.button(
                                "Descartar rascunho",
                                variant="outline",
                                on_click=ChamadosGerenteState.descartar_rascunho_comentario,
                                disabled=ChamadosGerenteState.enviando_comentario,
                            ),
                            spacing="3",
                        ),
                        width="100%",
                        spacing="3",
                    ),
                ),
                width="100%",
                spacing="3",
            ),
        ),
        rx.link("Voltar aos chamados", href="/gerente"),
        spacing="5",
        width="100%",
    )


def _protegida(conteudo: rx.Component, evento) -> rx.Component:
    return rx.cond(
        AuthState.carregando,
        estado_carregamento(),
        rx.cond(
            AuthState.sessao_confirmada & (AuthState.role == "gerente"),
            casca_conteudo(conteudo, "/gerente"),
            estado_revalidacao(evento),
        ),
    )


def gerente_chamados() -> rx.Component:
    return _protegida(_lista(), ChamadosGerenteState.carregar_lista)


def novo_chamado() -> rx.Component:
    return _protegida(_formulario(), ChamadosGerenteState.carregar_formulario)


def detalhe_chamado() -> rx.Component:
    return _protegida(_detalhe(), ChamadosGerenteState.carregar_detalhe)
