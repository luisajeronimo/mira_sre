"""Páginas da fila e detalhe de chamados do Técnico."""

import reflex as rx

from app.chamados.shared import cabecalho, erro
from app.chamados.tecnico.state import ChamadosTecnicoState
from app.components.layout import casca_conteudo, estado_carregamento, estado_revalidacao
from app.states.auth import AuthState


def _fila_tecnico() -> rx.Component:
    return rx.vstack(
        cabecalho("Fila técnica", "Consulte a fila global e a distribuição atual dos chamados."),
        rx.hstack(
            rx.button(
                "Todos",
                variant=rx.cond(ChamadosTecnicoState.visao == "todos", "solid", "outline"),
                on_click=ChamadosTecnicoState.selecionar_visao("todos"),
                disabled=ChamadosTecnicoState.carregando_fila,
            ),
            rx.button(
                "Não atribuídos",
                variant=rx.cond(ChamadosTecnicoState.visao == "nao_atribuidos", "solid", "outline"),
                on_click=ChamadosTecnicoState.selecionar_visao("nao_atribuidos"),
                disabled=ChamadosTecnicoState.carregando_fila,
            ),
            rx.cond(
                AuthState.role == "tecnico",
                rx.button(
                    "Atribuídos a mim",
                    variant=rx.cond(ChamadosTecnicoState.visao == "atribuidos_a_mim", "solid", "outline"),
                    on_click=ChamadosTecnicoState.selecionar_visao("atribuidos_a_mim"),
                    disabled=ChamadosTecnicoState.carregando_fila,
                ),
                rx.fragment(),
            ),
            rx.button(
                "Atribuídos a outros Técnicos",
                variant=rx.cond(ChamadosTecnicoState.visao == "atribuidos_a_outros", "solid", "outline"),
                on_click=ChamadosTecnicoState.selecionar_visao("atribuidos_a_outros"),
                disabled=ChamadosTecnicoState.carregando_fila,
            ),
            spacing="3",
            wrap="wrap",
        ),
        rx.hstack(
            rx.input(
                value=ChamadosTecnicoState.numero,
                placeholder="Número do chamado",
                on_change=ChamadosTecnicoState.atualizar_numero,
                aria_label="Pesquisar chamado por número",
                width="min(100%, 20rem)",
            ),
            rx.button(
                "Pesquisar",
                on_click=ChamadosTecnicoState.pesquisar_numero,
                disabled=ChamadosTecnicoState.carregando_fila,
            ),
            rx.cond(
                ChamadosTecnicoState.numero != "",
                rx.button(
                    "Limpar",
                    variant="outline",
                    on_click=ChamadosTecnicoState.limpar_pesquisa,
                    disabled=ChamadosTecnicoState.carregando_fila,
                ),
                rx.fragment(),
            ),
            spacing="3",
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
                ChamadosTecnicoState.chamados.length() == 0,
                rx.callout("Nenhum chamado encontrado.", icon="info"),
                rx.vstack(
                    rx.foreach(
                        ChamadosTecnicoState.chamados,
                        lambda item: rx.card(
                            rx.vstack(
                                rx.hstack(
                                    rx.vstack(
                                        rx.text("Chamado #" + item["id"].to_string(), weight="bold"),
                                        rx.heading(item["titulo"], size="4"),
                                        align="start",
                                        spacing="1",
                                    ),
                                    rx.badge(item["status"]),
                                    justify="between",
                                    width="100%",
                                ),
                                rx.text("Prioridade: " + item["prioridade"]),
                                rx.text("Categoria: " + item["categoria_nome"], color="gray"),
                                rx.text("Técnico: " + item["tecnico_nome"], color="gray"),
                                rx.hstack(
                                    rx.link("Ver detalhe", href="/tecnico/chamados/" + item["id"].to_string()),
                                    rx.cond(
                                        (AuthState.role == "tecnico") & item["pode_assumir"],
                                        rx.button(
                                            rx.cond(ChamadosTecnicoState.assumindo_id == item["id"], "Assumindo...", "Assumir"),
                                            on_click=ChamadosTecnicoState.assumir(item["id"]),
                                            disabled=ChamadosTecnicoState.assumindo_id != None,
                                        ),
                                        rx.fragment(),
                                    ),
                                    spacing="3",
                                ),
                                align="start",
                                width="100%",
                            ),
                            width="100%",
                        ),
                    ),
                    width="100%",
                    spacing="3",
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
            rx.card(
                rx.vstack(
                    rx.text("Chamado #" + ChamadosTecnicoState.chamado["id"].to_string(), weight="bold"),
                    rx.heading(ChamadosTecnicoState.chamado["titulo"], size="5"),
                    rx.text(ChamadosTecnicoState.chamado["descricao"], white_space="pre-wrap"),
                    rx.text("Status: " + ChamadosTecnicoState.chamado["status"]),
                    rx.text("Prioridade: " + ChamadosTecnicoState.chamado["prioridade"]),
                    rx.text("Origem: " + ChamadosTecnicoState.chamado["origem"]),
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
        ),
        rx.cond(
            (ChamadosTecnicoState.carregando_detalhe_tecnico == False)
            & (ChamadosTecnicoState.mensagem_detalhe_tecnico == "")
            & (ChamadosTecnicoState.chamado["id"] != None),
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
