"""Telas do fluxo inicial de chamados do Gerente."""

import reflex as rx

from app.components.layout import casca_conteudo, estado_carregamento, estado_revalidacao
from app.states.auth import AuthState
from app.states.chamados import ChamadosGerenteState, ChamadosTecnicoState


def _erro(mensagem: rx.Var) -> rx.Component:
    return rx.cond(mensagem != "", rx.callout(mensagem, icon="triangle_alert", color_scheme="red"))


def _cabecalho(titulo: str, descricao: str) -> rx.Component:
    return rx.vstack(rx.heading(titulo, size="7"), rx.text(descricao, color="gray"), align="start", spacing="1", width="100%")


def _lista() -> rx.Component:
    return rx.vstack(
        _cabecalho("Chamados", "Acompanhe os chamados da sua loja."),
        rx.hstack(rx.link(rx.button("Abrir chamado"), href="/gerente/chamados/novo"), align="center", width="100%"),
        _erro(ChamadosGerenteState.mensagem_chamados),
        rx.cond(
            ChamadosGerenteState.carregando_chamados,
            rx.center(rx.spinner(size="3"), width="100%", padding="4rem"),
            rx.cond(
                ChamadosGerenteState.chamados.length() == 0,
                rx.callout("Nenhum chamado encontrado.", icon="info"),
                rx.vstack(
                    rx.foreach(
                        ChamadosGerenteState.chamados,
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
                                rx.text(item["categoria_nome"], color="gray"),
                                rx.text(item["criado_em_texto"], size="2", color="gray"),
                                rx.link("Ver detalhe", href="/gerente/chamados/" + item["id"].to_string()),
                                align="start", width="100%",
                            ), width="100%",
                        ),
                    ), width="100%", spacing="3",
                ),
            ),
        ),
        spacing="5", width="100%",
    )


def _formulario() -> rx.Component:
    return rx.vstack(
        _cabecalho("Abrir chamado", "Registre uma solicitação para sua loja."),
        _erro(ChamadosGerenteState.mensagem_formulario),
        rx.cond(ChamadosGerenteState.mensagem_sucesso != "", rx.callout(ChamadosGerenteState.mensagem_sucesso, icon="check", color_scheme="green")),
        rx.form(
            rx.vstack(
                rx.select(ChamadosGerenteState.ativos, name="ativos_referencia_id", placeholder="Selecione o ativo", required=True, width="100%"),
                rx.select(ChamadosGerenteState.categorias, name="categorias_servico_id", placeholder="Selecione a categoria", required=True, width="100%"),
                rx.select(ChamadosGerenteState.prioridades(), name="prioridade", placeholder="Selecione a prioridade", required=True, width="100%"),
                rx.input(name="titulo", placeholder="Título", required=True, width="100%"),
                rx.text_area(name="descricao", placeholder="Descrição", required=True, width="100%"),
                rx.hstack(rx.link("Cancelar", href="/gerente"), rx.button(rx.cond(ChamadosGerenteState.enviando, "Enviando...", "Abrir chamado"), type="submit", disabled=ChamadosGerenteState.enviando), spacing="3"),
                spacing="3", width="100%",
            ), on_submit=ChamadosGerenteState.abrir_chamado, reset_on_submit=False, width="100%",
        ), spacing="5", width="100%",
    )


def _detalhe() -> rx.Component:
    return rx.vstack(
        _cabecalho("Detalhe do chamado", "Consulta somente leitura."),
        _erro(ChamadosGerenteState.mensagem_detalhe),
        rx.cond(ChamadosGerenteState.carregando_detalhe, rx.spinner(size="3"), rx.card(rx.vstack(
            rx.text(
                "Chamado #" + ChamadosGerenteState.chamado["id"].to_string(),
                weight="bold",
            ),
            rx.heading(ChamadosGerenteState.chamado["titulo"], size="5"),
            rx.text(ChamadosGerenteState.chamado["descricao"], white_space="pre-wrap"),
            rx.text("Status: " + ChamadosGerenteState.chamado["status"]),
            rx.text("Prioridade: " + ChamadosGerenteState.chamado["prioridade"]),
            rx.text("Origem: " + ChamadosGerenteState.chamado["origem"]),
            rx.text("SLA aplicado: " + ChamadosGerenteState.chamado["sla_horas_texto"]),
            rx.text(ChamadosGerenteState.chamado["criado_em_texto"], color="gray"), align="start", spacing="2"), width="100%")),
        rx.link("Voltar aos chamados", href="/gerente"), spacing="5", width="100%",
    )


def _protegida(conteudo: rx.Component, evento) -> rx.Component:
    return rx.cond(AuthState.carregando, estado_carregamento(), rx.cond(AuthState.sessao_confirmada & (AuthState.role == "gerente"), casca_conteudo(conteudo, "/gerente"), estado_revalidacao(evento)))


def gerente_chamados() -> rx.Component:
    return _protegida(_lista(), ChamadosGerenteState.carregar_lista)


def novo_chamado() -> rx.Component:
    return _protegida(_formulario(), ChamadosGerenteState.carregar_formulario)


def detalhe_chamado() -> rx.Component:
    return _protegida(_detalhe(), ChamadosGerenteState.carregar_detalhe)


def _fila_tecnico() -> rx.Component:
    return rx.vstack(
        _cabecalho("Fila técnica", "Consulte chamados elegíveis para assumir."),
        rx.hstack(
            rx.button(
                "Não atribuídos",
                variant=rx.cond(
                    ChamadosTecnicoState.visao == "nao_atribuidos",
                    "solid",
                    "outline",
                ),
                on_click=ChamadosTecnicoState.selecionar_visao("nao_atribuidos"),
            ),
            rx.button(
                "Atribuídos a mim",
                variant=rx.cond(
                    ChamadosTecnicoState.visao == "atribuidos_a_mim",
                    "solid",
                    "outline",
                ),
                on_click=ChamadosTecnicoState.selecionar_visao("atribuidos_a_mim"),
            ),
            spacing="3",
        ),
        _erro(ChamadosTecnicoState.mensagem_fila),
        _erro(ChamadosTecnicoState.mensagem_assuncao),
        rx.cond(
            ChamadosTecnicoState.carregando_fila,
            rx.center(rx.spinner(size="3"), width="100%", padding="4rem"),
            rx.cond(
                ChamadosTecnicoState.chamados.length() == 0,
                rx.callout("Nenhum chamado elegível encontrado.", icon="info"),
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
                                        item["pode_assumir"],
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
        _cabecalho("Detalhe técnico", "Consulta somente leitura, com autoatribuição aprovada."),
        _erro(ChamadosTecnicoState.mensagem_detalhe_tecnico),
        _erro(ChamadosTecnicoState.mensagem_assuncao),
        rx.cond(
            ChamadosTecnicoState.carregando_detalhe_tecnico,
            rx.spinner(size="3"),
            rx.card(
                rx.vstack(
                    rx.text(
                        "Chamado #" + ChamadosTecnicoState.chamado["id"].to_string(),
                        weight="bold",
                    ),
                    rx.heading(ChamadosTecnicoState.chamado["titulo"], size="5"),
                    rx.text(
                        ChamadosTecnicoState.chamado["descricao"],
                        white_space="pre-wrap",
                    ),
                    rx.text("Status: " + ChamadosTecnicoState.chamado["status"]),
                    rx.text("Prioridade: " + ChamadosTecnicoState.chamado["prioridade"]),
                    rx.text("Origem: " + ChamadosTecnicoState.chamado["origem"]),
                    rx.text("SLA aplicado: " + ChamadosTecnicoState.chamado["sla_horas_texto"]),
                    rx.text("Técnico: " + ChamadosTecnicoState.chamado["tecnico_nome"]),
                    rx.text("Atribuído em: " + ChamadosTecnicoState.chamado["atribuido_em_texto"]),
                    rx.cond(
                        ChamadosTecnicoState.chamado["pode_assumir"],
                        rx.button(
                            rx.cond(
                                ChamadosTecnicoState.assumindo_id != None,
                                "Assumindo...",
                                "Assumir",
                            ),
                            on_click=ChamadosTecnicoState.assumir(ChamadosTecnicoState.chamado["id"]),
                            disabled=ChamadosTecnicoState.assumindo_id != None,
                        ),
                        rx.fragment(),
                    ),
                    align="start",
                    spacing="2",
                ),
                width="100%",
            ),
        ),
        rx.link("Voltar à fila", href="/tecnico"),
        spacing="5",
        width="100%",
    )


def _protegida_tecnico(conteudo: rx.Component, evento) -> rx.Component:
    return rx.cond(
        AuthState.carregando,
        estado_carregamento(),
        rx.cond(
            AuthState.sessao_confirmada & (AuthState.role == "tecnico"),
            casca_conteudo(conteudo, "/tecnico"),
            estado_revalidacao(evento),
        ),
    )


def tecnico_chamados() -> rx.Component:
    return _protegida_tecnico(_fila_tecnico(), ChamadosTecnicoState.carregar_fila)


def detalhe_chamado_tecnico() -> rx.Component:
    return _protegida_tecnico(
        _detalhe_tecnico(),
        ChamadosTecnicoState.carregar_detalhe_tecnico,
    )
