"""State da jornada somente leitura do solicitante."""

from __future__ import annotations

import os
from typing import Any

import reflex as rx

from app.chamados.shared import (
    ChamadoView, ComentarioView, DetalheView, HistoricoStatusView,
    _detalhe_para_dict,
    _resumo_para_dict,
    comentario_publico_para_dict,
    historico_status_para_dict,
)
from app.services.service_desk import criar_cliente_service_desk
from app.services.xano import (
    XanoContratoInvalido, XanoIndisponivel, XanoNaoAutenticado,
    XanoNaoAutorizado, XanoNaoEncontrado,
)
from app.states.auth import (
    AuthState, MENSAGEM_EXPIRADA, MENSAGEM_INDISPONIVEL, MENSAGEM_NAO_AUTORIZADO,
)


def acompanhamento_publicado() -> bool:
    return os.getenv("MIRA_ACOMPANHAMENTO_SOLICITANTE_PUBLICADO", "false").lower() == "true"


class ChamadosSolicitanteState(AuthState):
    chamados: list[ChamadoView] = []
    chamado: DetalheView = {}
    comentarios: list[ComentarioView] = []
    historico_status: list[HistoricoStatusView] = []
    carregando_lista: bool = False
    carregando_detalhe: bool = False
    detalhe_carregado: bool = False
    mensagem_lista: str = ""
    mensagem_detalhe: str = ""
    mensagem_comentarios: str = ""
    mensagem_historico: str = ""

    def _limpar_sessao(self, mensagem: str = "") -> None:
        self.chamados = []
        self.chamado = {}
        self.comentarios = []
        self.historico_status = []
        self.detalhe_carregado = False
        self.carregando_lista = False
        self.carregando_detalhe = False
        super()._limpar_sessao(mensagem)

    def _contexto(self) -> tuple[int | None, int, str]:
        return self.usuario_id, self._versao_sessao, self._auth_token

    def _atual(self, contexto: tuple[int | None, int, str]) -> bool:
        return self.sessao_confirmada and self._contexto() == contexto

    def _erro(self, erro: Exception, campo: str) -> str | None:
        if isinstance(erro, XanoNaoAutenticado):
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            return "/login"
        if isinstance(erro, XanoNaoEncontrado):
            setattr(self, campo, "Chamado não encontrado.")
        elif isinstance(erro, XanoNaoAutorizado):
            setattr(self, campo, MENSAGEM_NAO_AUTORIZADO)
        elif isinstance(erro, (XanoContratoInvalido, XanoIndisponivel)):
            setattr(self, campo, MENSAGEM_INDISPONIVEL)
        else:
            setattr(self, campo, MENSAGEM_INDISPONIVEL)
        return None

    @rx.event
    async def carregar_lista(self):
        self.chamados = []
        self.mensagem_lista = ""
        if not acompanhamento_publicado():
            yield rx.redirect("/inicio")
            return
        self.carregando_lista = True
        yield
        destino = await self._revalidar()
        if destino is not None:
            self.carregando_lista = False
            yield rx.redirect(destino)
            return
        if not self.sessao_confirmada:
            self.carregando_lista = False
            return
        contexto = self._contexto()
        try:
            itens = await criar_cliente_service_desk().listar_chamados_solicitante(self._auth_token)
            if self._atual(contexto):
                self.chamados = [_resumo_para_dict(item) for item in itens]
        except Exception as erro:  # noqa: BLE001
            if self._atual(contexto):
                destino = self._erro(erro, "mensagem_lista")
                if destino is not None:
                    yield rx.redirect(destino)
        finally:
            self.carregando_lista = False

    @rx.event
    async def carregar_detalhe(self):
        self.chamado = {}
        self.comentarios = []
        self.historico_status = []
        self.detalhe_carregado = False
        self.mensagem_detalhe = ""
        self.mensagem_comentarios = ""
        self.mensagem_historico = ""
        if not acompanhamento_publicado():
            yield rx.redirect("/inicio")
            return
        self.carregando_detalhe = True
        yield
        destino = await self._revalidar()
        if destino is not None:
            self.carregando_detalhe = False
            yield rx.redirect(destino)
            return
        if not self.sessao_confirmada:
            self.carregando_detalhe = False
            return
        contexto = self._contexto()
        try:
            chamado_id = int(str(self.chamado_id))
            if chamado_id <= 0:
                raise ValueError
        except (AttributeError, TypeError, ValueError):
            self.mensagem_detalhe = "Chamado não encontrado."
            self.carregando_detalhe = False
            return
        try:
            cliente = criar_cliente_service_desk()
            detalhe = await cliente.obter_chamado_solicitante(self._auth_token, chamado_id)
            if not self._atual(contexto):
                self.carregando_detalhe = False
                return
            self.chamado = _detalhe_para_dict(detalhe)
            self.detalhe_carregado = True
        except Exception as erro:  # noqa: BLE001
            if self._atual(contexto):
                destino = self._erro(erro, "mensagem_detalhe")
                if destino is not None:
                    yield rx.redirect(destino)
            self.carregando_detalhe = False
            return
        try:
            comentarios = await cliente.listar_comentarios_publicos_solicitante(self._auth_token, chamado_id)
            if not self._atual(contexto):
                self.carregando_detalhe = False
                return
            self.comentarios = [comentario_publico_para_dict(item) for item in comentarios]
        except Exception as erro:  # noqa: BLE001
            if not self._atual(contexto):
                self.carregando_detalhe = False
                return
            destino = self._erro(erro, "mensagem_comentarios")
            if destino is not None:
                self.carregando_detalhe = False
                yield rx.redirect(destino)
                return
        try:
            historico = await cliente.listar_historico_status_solicitante(self._auth_token, chamado_id)
            if not self._atual(contexto):
                return
            self.historico_status = [historico_status_para_dict(item) for item in historico]
        except Exception as erro:  # noqa: BLE001
            if not self._atual(contexto):
                return
            destino = self._erro(erro, "mensagem_historico")
            if destino is not None:
                yield rx.redirect(destino)
                return
        finally:
            self.carregando_detalhe = False
