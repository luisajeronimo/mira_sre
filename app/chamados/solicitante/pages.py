"""Páginas de acompanhamento somente leitura do solicitante."""

import reflex as rx

from app.chamados.shared import cabecalho, erro
from app.chamados.solicitante.state import ChamadosSolicitanteState, acompanhamento_publicado
from app.components.layout import casca_conteudo, estado_carregamento, estado_revalidacao
from app.components.visual import badge_prioridade, badge_status, campo_info
from app.states.auth import AuthState


def _lista() -> rx.Component:
    return rx.vstack(
        cabecalho("Chamados solicitados", "Acompanhe os chamados em que você é o solicitante."),
        erro(ChamadosSolicitanteState.mensagem_lista),
        rx.cond(
            ChamadosSolicitanteState.carregando_lista,
            rx.spinner(size="3"),
            rx.cond(
                ChamadosSolicitanteState.chamados.length() == 0,
                rx.callout("Nenhum chamado solicitado.", icon="info"),
                rx.vstack(
                    rx.foreach(ChamadosSolicitanteState.chamados, lambda item: rx.link(
                        rx.card(
                            rx.vstack(
                                rx.hstack(
                                    rx.text("#" + item["id"].to_string() + " — " + item["titulo"], weight="bold"),
                                    badge_status(item["status"]),
                                    justify="between", width="100%",
                                ),
                                rx.text(item["ocorrencia"]),
                                rx.hstack(
                                    rx.text(item["ativo_nome"]),
                                    badge_prioridade(item["prioridade"]),
                                    rx.text("Atualizado em " + item["ultima_atualizacao_em_texto"], size="2"),
                                    spacing="3", wrap="wrap",
                                ),
                                align="start", spacing="2", width="100%",
                            ), width="100%",
                        ),
                        href="/chamados/solicitados/" + item["id"].to_string(),
                        width="100%",
                    )),
                    width="100%", spacing="3",
                ),
            ),
        ),
        width="100%", spacing="5", align="start",
    )


def _detalhe() -> rx.Component:
    return rx.vstack(
        cabecalho("Chamado solicitado", "Acompanhamento somente leitura."),
        erro(ChamadosSolicitanteState.mensagem_detalhe),
        rx.cond(
            ChamadosSolicitanteState.carregando_detalhe,
            rx.spinner(size="3"),
        ),
        rx.cond(
            ChamadosSolicitanteState.detalhe_carregado,
            rx.vstack(
                rx.card(
                    rx.vstack(
                        rx.heading(ChamadosSolicitanteState.chamado["titulo"], size="5"),
                        rx.grid(
                            campo_info("Número", ChamadosSolicitanteState.chamado["id"].to_string()),
                            campo_info("Status", badge_status(ChamadosSolicitanteState.chamado["status"])),
                            campo_info("Prioridade", badge_prioridade(ChamadosSolicitanteState.chamado["prioridade"])),
                            campo_info("Totem", ChamadosSolicitanteState.chamado["ativo_nome"]),
                            campo_info("Loja", ChamadosSolicitanteState.chamado["loja_nome"]),
                            campo_info("Categoria", ChamadosSolicitanteState.chamado["categoria_nome"]),
                            campo_info("Solicitante", ChamadosSolicitanteState.chamado["solicitante_nome"]),
                            campo_info("Responsável", ChamadosSolicitanteState.chamado["tecnico_nome"]),
                            campo_info("Origem", ChamadosSolicitanteState.chamado["origem"]),
                            campo_info("Aberto em", ChamadosSolicitanteState.chamado["criado_em_texto"]),
                            campo_info("Última atualização", ChamadosSolicitanteState.chamado["ultima_atualizacao_em_texto"]),
                            columns="3", spacing="3", width="100%",
                        ),
                        rx.text(ChamadosSolicitanteState.chamado["descricao"], white_space="pre-wrap"),
                        align="start", spacing="4", width="100%",
                    ), width="100%",
                ),
                rx.card(
                    rx.vstack(
                        rx.heading("Comentários públicos", size="4"),
                        erro(ChamadosSolicitanteState.mensagem_comentarios),
                        rx.cond(
                            ChamadosSolicitanteState.comentarios.length() == 0,
                            rx.text("Nenhum comentário público."),
                            rx.vstack(rx.foreach(ChamadosSolicitanteState.comentarios, lambda item: rx.card(
                                rx.text(item["conteudo"], white_space="pre-wrap"),
                                rx.text(item["autor_nome"] + " • " + item["criado_em_texto"], size="2"),
                                width="100%",
                            )), width="100%"),
                        ), align="start", width="100%",
                    ), width="100%",
                ),
                rx.card(
                    rx.vstack(
                        rx.heading("Histórico de status", size="4"),
                        erro(ChamadosSolicitanteState.mensagem_historico),
                        rx.cond(
                            ChamadosSolicitanteState.historico_status.length() == 0,
                            rx.text("Nenhuma transição registrada."),
                            rx.vstack(rx.foreach(ChamadosSolicitanteState.historico_status, lambda item: rx.card(
                                rx.text(item["status_anterior"] + " → " + item["status_resultante"], weight="medium"),
                                rx.text(item["criado_em_texto"] + " • " + item["autor_nome"] + " " + item["autor_perfil"], size="2"),
                                width="100%",
                            )), width="100%"),
                        ), align="start", width="100%",
                    ), width="100%",
                ),
                width="100%", spacing="4",
            ),
        ),
        rx.link("Voltar aos chamados solicitados", href="/chamados/solicitados"),
        width="100%", spacing="5", align="start",
    )


def _protegida(conteudo: rx.Component, evento) -> rx.Component:
    if not acompanhamento_publicado():
        return estado_revalidacao(evento)
    return rx.cond(
        AuthState.carregando,
        estado_carregamento(),
        rx.cond(
            AuthState.sessao_confirmada,
            casca_conteudo(conteudo),
            estado_revalidacao(evento),
        ),
    )


def chamados_solicitados() -> rx.Component:
    return _protegida(_lista(), ChamadosSolicitanteState.carregar_lista)


def detalhe_chamado_solicitado() -> rx.Component:
    return _protegida(_detalhe(), ChamadosSolicitanteState.carregar_detalhe)
