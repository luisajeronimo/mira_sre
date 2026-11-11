"""Páginas da jornada de chamados do Gerente."""

import reflex as rx

from app.chamados.gerente.state import ChamadosGerenteState
from app.chamados.shared import botao_criar_chamado, cabecalho, cabecalho_lista_chamados, campo_sla_com_consumo, erro
from app.components.layout import casca_conteudo, estado_carregamento, estado_revalidacao
from app.components.visual import (
    BORDA,
    BORDA_ROSE_SUAVE,
    ESTILO_CAMPO_COMENTARIO,
    FOCO_VISIVEL,
    RAIO_CONTROLE,
    RAIO_SUPERFICIE,
    SOMBRA_BAIXA,
    SUPERFICIE,
    TEXTO,
    TEXTO_SECUNDARIO,
    acoes_filtro,
    badge_prioridade,
    badge_status,
    badge_visibilidade,
    cabecalho_detalhe_chamado,
    cabecalho_tabela_ordenavel,
    celula_tabela,
    campo_info,
    campo_rotulado,
    composicao_detalhe_chamado,
    dropdown_multisselecao,
    painel_filtros,
    periodo_rotulado,
    rotulo_campo,
)
from app.states.auth import AuthState


def _lista() -> rx.Component:
    return rx.vstack(
        cabecalho_lista_chamados(
            "Chamados",
            "Acompanhe os chamados da sua loja.",
            botao_criar_chamado(),
        ),
        painel_filtros(
                    campo_rotulado(
                        "Número do chamado",
                        rx.input(
                            value=ChamadosGerenteState.filtro_numero,
                            on_change=ChamadosGerenteState.alterar_filtro_numero,
                            type="number",
                            min="1",
                            placeholder="Número",
                            width="100%",
                        ),
                    ),
                    campo_rotulado(
                        "Status",
                        dropdown_multisselecao(
                            ChamadosGerenteState.status_filtros(),
                            ChamadosGerenteState.filtro_status,
                            ChamadosGerenteState.alterar_filtro_status,
                            "Status",
                            ChamadosGerenteState.carregando_chamados,
                        ),
                    ),
                    campo_rotulado(
                        "Totem",
                        dropdown_multisselecao(
                            ChamadosGerenteState.ativos,
                            ChamadosGerenteState.filtro_ativo,
                            ChamadosGerenteState.alterar_filtro_ativo,
                            "Totem",
                            ChamadosGerenteState.carregando_chamados,
                        ),
                    ),
                    periodo_rotulado(
                        "Abertura",
                        ChamadosGerenteState.filtro_data_inicio,
                        ChamadosGerenteState.filtro_data_fim,
                        ChamadosGerenteState.alterar_periodo_abertura,
                        ChamadosGerenteState.carregando_chamados,
                        coluna="span 6",
                        largura="12rem",
                        altura="3.75rem",
                    ),
                    periodo_rotulado(
                        "Atualização",
                        ChamadosGerenteState.filtro_ultima_atualizacao_inicio,
                        ChamadosGerenteState.filtro_ultima_atualizacao_fim,
                        ChamadosGerenteState.alterar_periodo_atualizacao,
                        ChamadosGerenteState.carregando_chamados,
                        coluna="span 6",
                        largura="12rem",
                        altura="3.75rem",
                    ),
                    acoes=acoes_filtro(
                        rx.button("Aplicar", on_click=ChamadosGerenteState.aplicar_filtros),
                        rx.button(
                            "Limpar filtros",
                            variant="outline",
                            on_click=ChamadosGerenteState.limpar_filtros_lista,
                        ),
                        mostrar_rotulo=False,
                    ),
                    aplicados=rx.cond(
                    ChamadosGerenteState.filtros_aplicados.length() > 0,
                    rx.hstack(
                        rx.text("Aplicados:", size="2", weight="medium"),
                        rx.foreach(
                            ChamadosGerenteState.filtros_aplicados,
                            lambda filtro: rx.badge(
                                rx.text(filtro, text_transform="uppercase"),
                                color_scheme="gray",
                            ),
                        ),
                        wrap="wrap",
                    ),
                ),
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
                rx.card(
                    rx.box(
                        rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                cabecalho_tabela_ordenavel("Número", "numero", ChamadosGerenteState.ordenar_por, ChamadosGerenteState.direcao, ChamadosGerenteState.alternar_ordenacao("numero"), ChamadosGerenteState.carregando_chamados, largura="10%"),
                                cabecalho_tabela_ordenavel("Chamado", "titulo", ChamadosGerenteState.ordenar_por, ChamadosGerenteState.direcao, ChamadosGerenteState.alternar_ordenacao("titulo"), ChamadosGerenteState.carregando_chamados, largura="30%"),
                                cabecalho_tabela_ordenavel("Status", "status", ChamadosGerenteState.ordenar_por, ChamadosGerenteState.direcao, ChamadosGerenteState.alternar_ordenacao("status"), ChamadosGerenteState.carregando_chamados, largura="10%"),
                                cabecalho_tabela_ordenavel("Prioridade", "prioridade", ChamadosGerenteState.ordenar_por, ChamadosGerenteState.direcao, ChamadosGerenteState.alternar_ordenacao("prioridade"), ChamadosGerenteState.carregando_chamados, largura="10%"),
                                cabecalho_tabela_ordenavel("Totem", "totem", ChamadosGerenteState.ordenar_por, ChamadosGerenteState.direcao, ChamadosGerenteState.alternar_ordenacao("totem"), ChamadosGerenteState.carregando_chamados, largura="10%"),
                                cabecalho_tabela_ordenavel("Categoria", "categoria", ChamadosGerenteState.ordenar_por, ChamadosGerenteState.direcao, ChamadosGerenteState.alternar_ordenacao("categoria"), ChamadosGerenteState.carregando_chamados, largura="10%"),
                                cabecalho_tabela_ordenavel("Data de abertura", "criado_em", ChamadosGerenteState.ordenar_por, ChamadosGerenteState.direcao, ChamadosGerenteState.alternar_ordenacao("criado_em"), ChamadosGerenteState.carregando_chamados, largura="10%"),
                                cabecalho_tabela_ordenavel(
                                    "Data da última atualização",
                                    "ultima_atualizacao_em",
                                    ChamadosGerenteState.ordenar_por,
                                    ChamadosGerenteState.direcao,
                                    ChamadosGerenteState.alternar_ordenacao("ultima_atualizacao_em"),
                                    ChamadosGerenteState.carregando_chamados,
                                    largura="10%",
                                ),
                            )
                        ),
                        rx.table.body(
                            rx.foreach(
                                ChamadosGerenteState.chamados,
                                lambda item: rx.table.row(
                                    celula_tabela(
                                        rx.link(
                                            "#" + item["id"].to_string(),
                                            href="/chamados/"
                                            + item["id"].to_string(),
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
                                    celula_tabela(
                                        rx.text(
                                            item["categoria_nome"],
                                            max_width="9rem",
                                            white_space="normal",
                                            overflow_wrap="anywhere",
                                        )
                                    ),
                                    celula_tabela(item["criado_em_texto"]),
                                    celula_tabela(
                                        item["ultima_atualizacao_em_texto"]
                                    ),
                                ),
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
        spacing="5",
        width="100%",
    )


def _rotulo_abertura(texto: str) -> rx.Component:
    return rx.hstack(
        rx.text(texto, size="2", weight="bold", color=TEXTO),
        rx.text("*", size="2", weight="bold", color="var(--accent-9)"),
        spacing="1",
        align="center",
    )


def _campo_abertura(rotulo: str, controle: rx.Component) -> rx.Component:
    return rx.vstack(
        _rotulo_abertura(rotulo),
        controle,
        spacing="2",
        align="start",
        width="100%",
    )


def _opcao_prioridade(prioridade: rx.Var | str, estado=ChamadosGerenteState) -> rx.Component:
    selecionada = estado.prioridade_formulario == prioridade
    return rx.button(
        rx.hstack(
            rx.box(
                width="0.75rem",
                height="0.75rem",
                border_radius="999px",
                background=rx.cond(selecionada, "var(--accent-9)", "#CBD5E1"),
                box_shadow=rx.cond(
                    selecionada,
                    "0 0 0 3px var(--accent-3)",
                    "none",
                ),
                flex_shrink="0",
            ),
            rx.text(prioridade, weight="bold", color=TEXTO),
            spacing="3",
            align="center",
            width="100%",
            min_width="0",
            overflow="hidden",
        ),
        on_click=estado.alterar_prioridade_formulario(prioridade),
        disabled=estado.enviando,
        aria_label="Prioridade " + prioridade,
        aria_pressed=selecionada,
        variant="ghost",
        height="3.75rem",
        width="100%",
        min_width="0",
        max_width="100%",
        padding="0.875rem 1rem",
        margin="0",
        overflow="hidden",
        box_sizing="border-box",
        background=rx.cond(selecionada, "var(--accent-2)", SUPERFICIE),
        border=rx.cond(
            selecionada,
            "2px solid var(--accent-9)",
            f"1px solid {BORDA}",
        ),
        border_radius=RAIO_CONTROLE,
        box_shadow="none",
        _hover={
            "background": "var(--accent-2)",
            "border_color": "var(--accent-8)",
        },
        _focus_visible=FOCO_VISIVEL,
    )


def formulario_abertura(estado=ChamadosGerenteState, escopo="os Totens da sua loja") -> rx.Component:
    estilo_controle = {
        "background": SUPERFICIE,
        "border": f"1px solid {BORDA}",
        "border_radius": RAIO_CONTROLE,
        "box_shadow": "none",
        "_focus_visible": FOCO_VISIVEL,
    }
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        width="0.625rem",
                        height="0.625rem",
                        border_radius="999px",
                        background="var(--accent-9)",
                    ),
                    rx.text(
                        "Módulo operacional • Service Desk",
                        size="1",
                        weight="bold",
                        color="var(--accent-11)",
                        text_transform="uppercase",
                        letter_spacing="0.05em",
                    ),
                    spacing="2",
                    align="center",
                ),
                rx.heading(
                    "Abrir novo chamado",
                    size="8",
                    color=TEXTO,
                    letter_spacing="-0.03em",
                ),
                rx.text(
                    "Registre uma solicitação para " + escopo + ".",
                    color=TEXTO_SECUNDARIO,
                    size="3",
                ),
                spacing="2",
                align="start",
                min_width="0",
            ),
            rx.button(
                rx.icon("arrow_left", size=17),
                "Voltar para lista",
                variant="outline",
                on_click=estado.voltar_para_lista,
                disabled=estado.enviando,
                flex_shrink="0",
                _focus_visible=FOCO_VISIVEL,
            ),
            justify="between",
            align="start",
            width="100%",
        ),
        erro(estado.mensagem_formulario),
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.hstack(
                        rx.center(
                            rx.text("1", weight="bold", color="var(--accent-11)"),
                            width="2rem",
                            height="2rem",
                            border_radius="0.5rem",
                            background="var(--accent-3)",
                        ),
                        rx.heading("Dados do chamado", size="5", color=TEXTO),
                        spacing="3",
                        align="center",
                    ),
                    rx.text(
                        "* Campos obrigatórios",
                        size="1",
                        weight="bold",
                        color=TEXTO_SECUNDARIO,
                    ),
                    justify="between",
                    align="center",
                    width="100%",
                ),
                _campo_abertura(
                    "Título do chamado",
                    rx.input(
                        value=estado.titulo_formulario,
                        on_change=estado.alterar_titulo_formulario,
                        placeholder="Resuma a solicitação",
                        width="100%",
                        min_height="3.25rem",
                        **estilo_controle,
                    ),
                ),
                rx.grid(
                    _campo_abertura(
                        "Totem afetado",
                        rx.select.root(
                            rx.select.trigger(
                                placeholder="Selecione o Totem",
                                width="100%",
                                min_height="3.25rem",
                                **estilo_controle,
                            ),
                            rx.select.content(
                                rx.foreach(
                                    estado.ativos_formulario,
                                    lambda ativo: rx.select.item(
                                        ativo["nome"],
                                        value=ativo["id"].to_string(),
                                    ),
                                ),
                            ),
                            value=estado.ativo_formulario,
                            on_change=estado.alterar_ativo_formulario,
                            width="100%",
                        ),
                    ),
                    _campo_abertura(
                        "Categoria",
                        rx.select.root(
                            rx.select.trigger(
                                placeholder="Selecione a categoria",
                                width="100%",
                                min_height="3.25rem",
                                **estilo_controle,
                            ),
                            rx.select.content(
                                rx.foreach(
                                    estado.categorias_formulario,
                                    lambda categoria: rx.select.item(
                                        categoria["nome"],
                                        value=categoria["id"].to_string(),
                                    ),
                                ),
                            ),
                            value=estado.categoria_formulario,
                            on_change=estado.alterar_categoria_formulario,
                            width="100%",
                        ),
                    ),
                    columns="2",
                    gap="1.25rem",
                    width="100%",
                ),
                _campo_abertura(
                    "Prioridade",
                    rx.grid(
                        rx.foreach(
                            estado.prioridades(),
                            lambda prioridade: _opcao_prioridade(prioridade, estado),
                        ),
                        columns="4",
                        gap="0.75rem",
                        width="100%",
                        min_width="0",
                        align="stretch",
                        style={
                            "gridTemplateColumns": "repeat(4, minmax(0, 1fr))"
                        },
                    ),
                ),
                _campo_abertura(
                    "Descrição detalhada",
                    rx.text_area(
                        value=estado.descricao_formulario,
                        on_change=estado.alterar_descricao_formulario,
                        placeholder="Descreva o problema, os sintomas e o contexto observado",
                        width="100%",
                        min_height="10rem",
                        resize="vertical",
                        padding="0.875rem 1rem",
                        **estilo_controle,
                    ),
                ),
                spacing="5",
                align="start",
                width="100%",
            ),
            width="100%",
            background=SUPERFICIE,
            border=f"1px solid {BORDA}",
            border_radius=RAIO_SUPERFICIE,
            box_shadow=SOMBRA_BAIXA,
            padding="2rem",
        ),
        rx.card(
            rx.hstack(
                rx.hstack(
                    rx.icon("lock", size=16, color="var(--accent-9)"),
                    rx.text("Abertura autenticada como", size="2", color=TEXTO_SECUNDARIO),
                    rx.text(AuthState.nome, size="2", weight="bold", color=TEXTO),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.button(
                        "Limpar",
                        variant="ghost",
                        on_click=estado.limpar_formulario,
                        disabled=estado.enviando,
                        _focus_visible=FOCO_VISIVEL,
                    ),
                    rx.button(
                        "Descartar",
                        variant="soft",
                        on_click=estado.descartar_formulario,
                        disabled=estado.enviando,
                        _focus_visible=FOCO_VISIVEL,
                    ),
                    rx.button(
                        rx.icon("send", size=17),
                        rx.cond(
                            estado.enviando,
                            "Enviando...",
                            "Confirmar e abrir chamado",
                        ),
                        on_click=estado.abrir_chamado,
                        disabled=estado.enviando,
                        color_scheme="ruby",
                        weight="bold",
                        _focus_visible=FOCO_VISIVEL,
                    ),
                    spacing="2",
                    align="center",
                ),
                justify="between",
                align="center",
                width="100%",
            ),
            width="100%",
            background=SUPERFICIE,
            border=f"1px solid {BORDA}",
            border_radius=RAIO_SUPERFICIE,
            box_shadow=SOMBRA_BAIXA,
            padding="1.25rem 1.5rem",
        ),
        spacing="5",
        align="start",
        max_width="72rem",
        margin="0 auto",
        width="100%",
    )


def _detalhe() -> rx.Component:
    return rx.vstack(
        cabecalho("Detalhe do chamado", "Acompanhe o chamado e suas atualizações."),
        erro(ChamadosGerenteState.mensagem_detalhe),
        rx.cond(
            ChamadosGerenteState.carregando_detalhe,
            rx.spinner(size="3"),
            rx.cond(
                ChamadosGerenteState.detalhe_carregado,
                composicao_detalhe_chamado(
                    rx.vstack(
                        cabecalho_detalhe_chamado(
                            ChamadosGerenteState.chamado["id"].to_string(),
                            ChamadosGerenteState.chamado["titulo"],
                            ChamadosGerenteState.abrir_drawer_totem,
                        ),
                        rx.heading("Dados do chamado", size="3"),
                        rx.grid(
                            campo_info("Status", badge_status(ChamadosGerenteState.chamado["status"])),
                            campo_info("Prioridade", badge_prioridade(ChamadosGerenteState.chamado["prioridade"])),
                            campo_info(
                                "Origem",
                                rx.text(
                                    ChamadosGerenteState.chamado["origem"],
                                    text_transform="uppercase",
                                ),
                            ),
                            campo_info(
                                "Totem",
                                ChamadosGerenteState.chamado["ativo_nome"],
                            ),
                            campo_info("Loja", ChamadosGerenteState.chamado["loja_nome"]),
                            campo_info("Categoria", ChamadosGerenteState.chamado["categoria_nome"]),
                            campo_info("Solicitante", ChamadosGerenteState.chamado["solicitante_nome"]),
                            campo_info("Responsável", ChamadosGerenteState.chamado["tecnico_nome"]),
                            campo_sla_com_consumo(
                                ChamadosGerenteState.chamado["sla_horas_texto"],
                                ChamadosGerenteState.consumo_sla,
                                ChamadosGerenteState.carregando_sla,
                                ChamadosGerenteState.mensagem_sla,
                            ),
                            campo_info("Aberto em", ChamadosGerenteState.chamado["criado_em_texto"]),
                            campo_info("Última atualização", ChamadosGerenteState.chamado["ultima_atualizacao_em_texto"]),
                            rx.cond(
                                ChamadosGerenteState.chamado["criador_sistema_nome"] != "",
                                campo_info("Criado por", ChamadosGerenteState.chamado["criador_sistema_nome"]),
                                rx.fragment(),
                            ),
                            columns="3",
                            spacing="3",
                            width="100%",
                        ),
                        align="start",
                        spacing="4",
                        width="100%",
                    ),
                    ChamadosGerenteState.chamado["descricao"],
                ),
                rx.fragment(),
            ),
        ),
        rx.drawer.root(
            rx.drawer.portal(
                rx.drawer.overlay(),
                rx.drawer.content(
                    rx.vstack(
                        rx.flex(
                            rx.drawer.title("Detalhe do Totem"),
                            rx.drawer.close(
                                rx.icon_button(
                                    rx.icon("x"),
                                    variant="ghost",
                                    aria_label="Fechar detalhe do Totem",
                                )
                            ),
                            justify="between",
                            align="center",
                            width="100%",
                        ),
                        rx.cond(
                            ChamadosGerenteState.chamado["resumo_totem"] != None,
                            rx.vstack(
                                rx.text("Totem: " + ChamadosGerenteState.chamado["resumo_totem"]["nome_ativo"]),
                                rx.text("Loja: " + ChamadosGerenteState.chamado["resumo_totem"]["loja"]["nome"]),
                                campo_info(
                                    "Estado",
                                    badge_status(ChamadosGerenteState.chamado["resumo_totem"]["status_atual"]),
                                ),
                                rx.cond(
                                    ChamadosGerenteState.chamado["resumo_totem"]["ultima_telemetria"] != None,
                                    rx.vstack(
                                        rx.text("Última telemetria", weight="medium"),
                                        rx.text("Recebida em: " + ChamadosGerenteState.chamado["resumo_totem"]["ultima_telemetria"]["evento_timestamp_texto"]),
                                        rx.text("CPU: " + ChamadosGerenteState.chamado["resumo_totem"]["ultima_telemetria"]["uso_cpu"].to_string() + "%"),
                                        rx.text("Memória: " + ChamadosGerenteState.chamado["resumo_totem"]["ultima_telemetria"]["uso_memoria"].to_string() + "%"),
                                        rx.text("Temperatura: " + ChamadosGerenteState.chamado["resumo_totem"]["ultima_telemetria"]["temperatura"].to_string() + "°C"),
                                        campo_info(
                                            "Rede",
                                            badge_status(ChamadosGerenteState.chamado["resumo_totem"]["ultima_telemetria"]["status_rede"]),
                                        ),
                                        align="start",
                                    ),
                                    rx.callout("Nenhuma telemetria registrada.", icon="info"),
                                ),
                                align="start",
                                width="100%",
                            ),
                        ),
                        align="start",
                        spacing="4",
                        width="100%",
                    ),
                    background="var(--color-panel)",
                    box_shadow="-8px 0 24px rgba(0, 0, 0, 0.12)",
                    height="100vh",
                    margin_left="auto",
                    overflow_y="auto",
                    padding="24px",
                    width="min(28rem, 100vw)",
                ),
            ),
            direction="right",
            on_open_change=ChamadosGerenteState.definir_drawer_totem_aberto,
            open=ChamadosGerenteState.drawer_totem_aberto,
        ),
        rx.cond(
            ChamadosGerenteState.detalhe_carregado & (ChamadosGerenteState.chamado["status"] == "Resolvido"),
            rx.card(
                rx.vstack(
                    rx.heading("Rejeitar solução", size="4"),
                    rx.text("Explique por que a solução não resolveu o problema."),
                    erro(ChamadosGerenteState.mensagem_rejeicao),
                    rx.text_area(
                        value=ChamadosGerenteState.justificativa_rejeicao,
                        on_change=ChamadosGerenteState.alterar_justificativa_rejeicao,
                        disabled=ChamadosGerenteState.enviando_rejeicao,
                        aria_label="Justificativa da rejeição",
                        width="100%",
                    ),
                    rx.button(
                        rx.cond(ChamadosGerenteState.enviando_rejeicao, "Enviando...", "Rejeitar solução"),
                        on_click=ChamadosGerenteState.rejeitar_solucao,
                        disabled=ChamadosGerenteState.enviando_rejeicao,
                    ),
                    align="start", spacing="3", width="100%",
                ),
                width="100%",
            ),
        ),
        rx.cond(
            ChamadosGerenteState.mensagem_sucesso_rejeicao != "",
            rx.callout(ChamadosGerenteState.mensagem_sucesso_rejeicao, icon="check", color_scheme="green"),
        ),
        rx.cond(
            ChamadosGerenteState.detalhe_carregado,
            rx.card(
                rx.vstack(
                    rx.heading("Histórico de status", size="4"),
                    erro(ChamadosGerenteState.mensagem_historico),
                    rx.cond(
                        ChamadosGerenteState.carregando_historico,
                        rx.spinner(size="2"),
                        rx.cond(
                            ChamadosGerenteState.historico_status.length() == 0,
                            rx.text("Nenhuma transição registrada."),
                            rx.vstack(
                                rx.foreach(ChamadosGerenteState.historico_status, lambda item: rx.card(
                                    rx.text(item["status_anterior"] + " → " + item["status_resultante"], weight="medium"),
                                    rx.text(item["criado_em_texto"] + " • " + item["autor_nome"] + " " + item["autor_perfil"], size="2"),
                                    width="100%",
                                )), width="100%",
                            ),
                        ),
                    ),
                    align="start", width="100%",
                ), width="100%",
            ),
        ),
        rx.cond(
            ChamadosGerenteState.detalhe_carregado,
            rx.vstack(
                rx.heading("Comentários", size="5"),
                erro(ChamadosGerenteState.mensagem_comentarios),
                rx.cond(
                    ChamadosGerenteState.mensagem_sucesso != "",
                    rx.callout(ChamadosGerenteState.mensagem_sucesso, icon="check", color_scheme="green"),
                ),
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
                                    rx.hstack(
                                        rx.vstack(
                                            rx.text(comentario["autor_nome"], weight="medium"),
                                            rx.text(comentario["conteudo"], white_space="pre-wrap"),
                                            align="start",
                                            spacing="1",
                                            flex_grow="1",
                                            min_width="0",
                                        ),
                                        rx.vstack(
                                            rx.text(comentario["criado_em_texto"], size="1", color=TEXTO_SECUNDARIO),
                                            badge_visibilidade("Público"),
                                            align="end",
                                            spacing="2",
                                            min_width="8rem",
                                        ),
                                        justify="between",
                                        align="start",
                                        spacing="4",
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
                            width="100%",
                            spacing="2",
                        ),
                    ),
                ),
                rx.vstack(
                        rx.text_area(
                            value=ChamadosGerenteState.rascunho_comentario,
                            on_change=ChamadosGerenteState.alterar_rascunho_comentario,
                            placeholder="Adicionar comentário público",
                            width="100%",
                            **ESTILO_CAMPO_COMENTARIO,
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
                width="100%",
                spacing="3",
            ),
        ),
        rx.link("Voltar aos chamados", href="/inicio"),
        spacing="5",
        width="100%",
    )


def _protegida(conteudo: rx.Component, evento) -> rx.Component:
    return rx.cond(
        AuthState.carregando,
        estado_carregamento(),
        rx.cond(
            AuthState.sessao_confirmada & (AuthState.role == "gerente"),
            casca_conteudo(conteudo, "/inicio", evento_sair=ChamadosGerenteState.sair_gerente),
            estado_revalidacao(evento),
        ),
    )


def gerente_chamados() -> rx.Component:
    return _protegida(_lista(), ChamadosGerenteState.carregar_lista)


def novo_chamado() -> rx.Component:
    return _protegida(formulario_abertura(), ChamadosGerenteState.carregar_formulario)


def detalhe_chamado() -> rx.Component:
    return _protegida(_detalhe(), ChamadosGerenteState.carregar_detalhe)
