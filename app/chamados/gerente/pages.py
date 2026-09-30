"""Páginas da jornada de chamados do Gerente."""

import reflex as rx

from app.chamados.gerente.state import ChamadosGerenteState
from app.chamados.shared import cabecalho, erro
from app.components.layout import casca_conteudo, estado_carregamento, estado_revalidacao
from app.states.auth import AuthState


def _lista() -> rx.Component:
    return rx.vstack(
        cabecalho("Chamados", "Acompanhe os chamados da sua loja."),
        rx.hstack(
            rx.link(rx.button("Abrir chamado"), href="/gerente/chamados/novo"),
            align="center",
            width="100%",
        ),
        erro(ChamadosGerenteState.mensagem_chamados),
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
                                rx.link(
                                    "Ver detalhe",
                                    href="/gerente/chamados/" + item["id"].to_string(),
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


def _formulario() -> rx.Component:
    return rx.vstack(
        cabecalho("Abrir chamado", "Registre uma solicitação para sua loja."),
        erro(ChamadosGerenteState.mensagem_formulario),
        rx.cond(
            ChamadosGerenteState.mensagem_sucesso != "",
            rx.callout(
                ChamadosGerenteState.mensagem_sucesso,
                icon="check",
                color_scheme="green",
            ),
        ),
        rx.form(
            rx.vstack(
                rx.select(ChamadosGerenteState.ativos, name="ativos_referencia_id", placeholder="Selecione o ativo", required=True, width="100%"),
                rx.select(ChamadosGerenteState.categorias, name="categorias_servico_id", placeholder="Selecione a categoria", required=True, width="100%"),
                rx.select(ChamadosGerenteState.prioridades(), name="prioridade", placeholder="Selecione a prioridade", required=True, width="100%"),
                rx.input(name="titulo", placeholder="Título", required=True, width="100%"),
                rx.text_area(name="descricao", placeholder="Descrição", required=True, width="100%"),
                rx.hstack(
                    rx.link("Cancelar", href="/gerente"),
                    rx.button(
                        rx.cond(ChamadosGerenteState.enviando, "Enviando...", "Abrir chamado"),
                        type="submit",
                        disabled=ChamadosGerenteState.enviando,
                    ),
                    spacing="3",
                ),
                spacing="3",
                width="100%",
            ),
            on_submit=ChamadosGerenteState.abrir_chamado,
            reset_on_submit=False,
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
            rx.card(
                rx.vstack(
                    rx.text("Chamado #" + ChamadosGerenteState.chamado["id"].to_string(), weight="bold"),
                    rx.heading(ChamadosGerenteState.chamado["titulo"], size="5"),
                    rx.text(ChamadosGerenteState.chamado["descricao"], white_space="pre-wrap"),
                    rx.text("Status: " + ChamadosGerenteState.chamado["status"]),
                    rx.text("Prioridade: " + ChamadosGerenteState.chamado["prioridade"]),
                    rx.text("Origem: " + ChamadosGerenteState.chamado["origem"]),
                    rx.text("SLA aplicado: " + ChamadosGerenteState.chamado["sla_horas_texto"]),
                    rx.text(ChamadosGerenteState.chamado["criado_em_texto"], color="gray"),
                    align="start",
                    spacing="2",
                ),
                width="100%",
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
