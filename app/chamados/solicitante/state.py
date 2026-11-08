"""State do acompanhamento somente leitura dos chamados solicitados."""

from __future__ import annotations

import reflex as rx

from app.chamados.shared import (
    ChamadoView,
    ComentarioView,
    DetalheSolicitanteView,
    TransicaoStatusView,
    _resumo_para_dict,
    comentario_publico_para_dict,
    detalhe_solicitante_para_dict,
    transicao_status_para_dict,
)
from app.components.navegacao import acompanhamento_solicitante_publicado
from app.services.service_desk import criar_cliente_service_desk
from app.services.xano import (
    XanoNaoAutenticado,
    XanoNaoAutorizado,
    XanoNaoEncontrado,
)
from app.states.auth import (
    MENSAGEM_EXPIRADA,
    MENSAGEM_INDISPONIVEL,
    MENSAGEM_NAO_AUTORIZADO,
    AuthState,
)


MENSAGEM_NAO_ENCONTRADO = "Chamado não encontrado."
DESTINO_SEM_LIBERACAO = "/inicio"


class ChamadosSolicitanteState(AuthState):
    """Consulta os contratos do solicitante; o vínculo é decidido pelo Xano.

    Não há evento de escrita: comentário, rejeição, aceitação, Save e
    atribuição não existem nesta jornada.
    """

    chamados: list[ChamadoView] = []
    chamado: DetalheSolicitanteView = {}
    comentarios: list[ComentarioView] = []
    historico: list[TransicaoStatusView] = []

    carregando_chamados: bool = False
    carregando_detalhe: bool = False
    carregando_comentarios: bool = False
    carregando_historico: bool = False
    lista_carregada: bool = False
    detalhe_carregado: bool = False

    mensagem_chamados: str = ""
    mensagem_detalhe: str = ""
    mensagem_comentarios: str = ""
    mensagem_historico: str = ""

    def _registrar_erro(self, erro: Exception, destino: str) -> str | None:
        """Converte o erro em mensagem sanitizada; 401 encerra a sessão local."""
        if isinstance(erro, XanoNaoAutenticado):
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            return "/login"
        if isinstance(erro, XanoNaoEncontrado):
            # O Xano responde 404 tanto para chamado inexistente quanto para
            # chamado de outra pessoa; a interface mantém a mesma mensagem.
            setattr(self, destino, MENSAGEM_NAO_ENCONTRADO)
            return None
        if isinstance(erro, XanoNaoAutorizado):
            setattr(self, destino, MENSAGEM_NAO_AUTORIZADO)
            return None
        setattr(self, destino, MENSAGEM_INDISPONIVEL)
        return None

    def _chamado_id_da_rota(self) -> int | None:
        try:
            chamado_id = int(str(self.chamado_id))
        except (AttributeError, TypeError, ValueError):
            return None
        return chamado_id if chamado_id > 0 else None

    @rx.event
    async def carregar_lista(self):
        if not acompanhamento_solicitante_publicado():
            # Contratos ainda não publicados: nenhuma consulta ao backend.
            yield rx.redirect(DESTINO_SEM_LIBERACAO)
            return
        if self.carregando_chamados:
            return
        self.carregando_chamados = True
        self.lista_carregada = False
        self.chamados = []
        self.mensagem_chamados = ""
        yield
        destino = await self._revalidar()
        if destino is not None:
            self.carregando_chamados = False
            yield rx.redirect(destino)
            return
        if not self.sessao_confirmada:
            self.carregando_chamados = False
            return
        try:
            itens = await criar_cliente_service_desk().listar_chamados_solicitante(
                self._auth_token
            )
            # A ordem do backend é preservada; não há filtro nem ordenação local.
            self.chamados = [_resumo_para_dict(item) for item in itens]
            self.lista_carregada = True
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro(erro, "mensagem_chamados")
            if destino is not None:
                self.carregando_chamados = False
                yield rx.redirect(destino)
                return
        self.carregando_chamados = False

    @rx.event
    async def carregar_detalhe(self):
        if not acompanhamento_solicitante_publicado():
            yield rx.redirect(DESTINO_SEM_LIBERACAO)
            return
        if self.carregando_detalhe:
            return
        self.carregando_detalhe = True
        self.detalhe_carregado = False
        self.chamado = {}
        self.comentarios = []
        self.historico = []
        self.mensagem_detalhe = ""
        self.mensagem_comentarios = ""
        self.mensagem_historico = ""
        yield
        destino = await self._revalidar()
        if destino is not None:
            self.carregando_detalhe = False
            yield rx.redirect(destino)
            return
        if not self.sessao_confirmada:
            self.carregando_detalhe = False
            return
        chamado_id = self._chamado_id_da_rota()
        if chamado_id is None:
            self.mensagem_detalhe = MENSAGEM_NAO_ENCONTRADO
            self.carregando_detalhe = False
            return

        cliente = criar_cliente_service_desk()
        try:
            detalhe = await cliente.obter_chamado_solicitante(self._auth_token, chamado_id)
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro(erro, "mensagem_detalhe")
            self.carregando_detalhe = False
            if destino is not None:
                yield rx.redirect(destino)
            return
        self.chamado = detalhe_solicitante_para_dict(detalhe)
        self.detalhe_carregado = True
        self.carregando_detalhe = False
        self.carregando_comentarios = True
        self.carregando_historico = True
        yield

        # Comentários e histórico falham de forma isolada: o detalhe permanece.
        try:
            comentarios = await cliente.listar_comentarios_publicos_solicitante(
                self._auth_token,
                chamado_id,
            )
            self.comentarios = [comentario_publico_para_dict(item) for item in comentarios]
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro(erro, "mensagem_comentarios")
            if destino is not None:
                self.carregando_comentarios = False
                self.carregando_historico = False
                yield rx.redirect(destino)
                return
        finally:
            self.carregando_comentarios = False

        try:
            historico = await cliente.listar_historico_status_solicitante(
                self._auth_token,
                chamado_id,
            )
            self.historico = [transicao_status_para_dict(item) for item in historico]
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro(erro, "mensagem_historico")
            if destino is not None:
                self.carregando_historico = False
                yield rx.redirect(destino)
                return
        finally:
            self.carregando_historico = False
