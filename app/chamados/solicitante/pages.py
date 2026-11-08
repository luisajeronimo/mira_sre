"""Páginas somente leitura dos chamados em que o usuário é solicitante."""

import reflex as rx

from app.chamados.shared import cabecalho, erro, secao_historico_status
from app.chamados.solicitante.state import ChamadosSolicitanteState
from app.components.layout import casca_conteudo, estado_carregamento, estado_revalidacao
from app.components.visual import (
    BORDA,
    BORDA_ROSE_SUAVE,
    RAIO_SUPERFICIE,
    SOMBRA_BAIXA,
    SUPERFICIE,
    TEXTO,
    TEXTO_SECUNDARIO,
    badge_prioridade,
    badge_status,
    badge_visibilidade,
    cabecalho_tabela_texto,
    campo_info,
    celula_tabela,
    composicao_detalhe_chamado,
)
from app.states.auth import AuthState


ROTA_LISTA = "/chamados/solicitados"


def _lista() -> rx.Component:
    return rx.vstack(
        cabecalho(
            "Chamados solicitados",
            "Acompanhe, somente para consulta, os chamados em que você é o solicitante.",
        ),
        erro(ChamadosSolicitanteState.mensagem_chamados),
        rx.cond(
            ChamadosSolicitanteState.carregando_chamados,
            rx.center(rx.spinner(size="3"), width="100%", padding="4rem"),
            rx.cond(
                ChamadosSolicitanteState.lista_carregada,
                rx.cond(
                    ChamadosSolicitanteState.chamados.length() == 0,
                    rx.callout("Você não possui chamados solicitados.", icon="info"),
                    rx.card(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    cabecalho_tabela_texto("Número", largura="10%"),
                                    cabecalho_tabela_texto("Chamado", largura="30%"),
                                    cabecalho_tabela_texto("Status", largura="12%"),
                                    cabecalho_tabela_texto("Prioridade", largura="10%"),
                                    cabecalho_tabela_texto("Totem", largura="10%"),
                                    cabecalho_tabela_texto("Categoria", largura="10%"),
                                    cabecalho_tabela_texto("Data de abertura", largura="9%"),
                                    cabecalho_tabela_texto("Data da última atualização", largura="9%"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    ChamadosSolicitanteState.chamados,
                                    lambda item: rx.table.row(
                                        celula_tabela(
                                            rx.link(
                                                "#" + item["id"].to_string(),
                                                href=ROTA_LISTA + "/" + item["id"].to_string(),
                                            )
                                        ),
                                        celula_tabela(
                                            rx.vstack(
                                                rx.text(item["titulo"], weight="medium"),
                                                rx.text(item["ocorrencia"], size="2", color="gray"),
                                                align="start",
                                                spacing="1",
                                            ),
                                            alinhamento="left",
                                        ),
                                        celula_tabela(badge_status(item["status"])),
                                        celula_tabela(item["prioridade"]),
                                        celula_tabela(item["ativo_nome"]),
                                        celula_tabela(item["categoria_nome"]),
                                        celula_tabela(item["criado_em_texto"]),
                                        celula_tabela(item["ultima_atualizacao_em_texto"]),
                                    ),
                                )
                            ),
                            width="100%",
                            style={"tableLayout": "fixed"},
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
                rx.fragment(),
            ),
        ),
        spacing="5",
        width="100%",
    )


def _comentarios() -> rx.Component:
    """Comentários públicos retornados pelo contrato; sem campo de envio."""
    return rx.vstack(
        rx.heading("Comentários", size="5"),
        erro(ChamadosSolicitanteState.mensagem_comentarios),
        rx.cond(
            ChamadosSolicitanteState.carregando_comentarios,
            rx.spinner(size="2"),
            rx.cond(
                ChamadosSolicitanteState.mensagem_comentarios != "",
                rx.fragment(),
                rx.cond(
                    ChamadosSolicitanteState.comentarios.length() == 0,
                    rx.text("Nenhum comentário público.", color="gray"),
                    rx.vstack(
                        rx.foreach(
                            ChamadosSolicitanteState.comentarios,
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
        ),
        width="100%",
        spacing="3",
    )


def _dados_chamado() -> rx.Component:
    chamado = ChamadosSolicitanteState.chamado
    return rx.vstack(
        rx.heading(
            "Chamado #" + chamado["id"].to_string() + " - " + chamado["titulo"],
            size="5",
            weight="bold",
            color=TEXTO,
        ),
        rx.heading("Dados do chamado", size="3"),
        rx.grid(
            campo_info("Status", badge_status(chamado["status"])),
            campo_info("Prioridade", badge_prioridade(chamado["prioridade"])),
            campo_info("Origem", rx.text(chamado["origem"], text_transform="uppercase")),
            campo_info("Totem", chamado["ativo_nome"]),
            campo_info("Loja", chamado["loja_nome"]),
            campo_info("Categoria", chamado["categoria_nome"]),
            campo_info("Solicitante", chamado["solicitante_nome"]),
            campo_info("Responsável", chamado["tecnico_nome"]),
            campo_info("SLA aplicado", chamado["sla_horas_texto"]),
            campo_info("Aberto em", chamado["criado_em_texto"]),
            campo_info("Última atualização", chamado["ultima_atualizacao_em_texto"]),
            rx.cond(
                chamado["criador_sistema_nome"] != "",
                campo_info("Criado por", chamado["criador_sistema_nome"]),
                rx.fragment(),
            ),
            columns="3",
            spacing="3",
            width="100%",
        ),
        align="start",
        spacing="4",
        width="100%",
    )


def _detalhe() -> rx.Component:
    return rx.vstack(
        cabecalho("Detalhe do chamado solicitado", "Consulta somente leitura."),
        erro(ChamadosSolicitanteState.mensagem_detalhe),
        rx.cond(
            ChamadosSolicitanteState.carregando_detalhe,
            rx.spinner(size="3"),
            rx.cond(
                ChamadosSolicitanteState.detalhe_carregado,
                composicao_detalhe_chamado(
                    _dados_chamado(),
                    ChamadosSolicitanteState.chamado["descricao"],
                    _comentarios(),
                    secao_historico_status(
                        ChamadosSolicitanteState.historico,
                        ChamadosSolicitanteState.carregando_historico,
                        ChamadosSolicitanteState.mensagem_historico,
                    ),
                ),
                rx.fragment(),
            ),
        ),
        rx.link("Voltar aos chamados solicitados", href=ROTA_LISTA),
        spacing="5",
        width="100%",
    )


def _protegida(conteudo: rx.Component, evento) -> rx.Component:
    """Qualquer perfil oficial confirmado; o vínculo é autorizado pelo Xano."""
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
