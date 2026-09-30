"""State da fila técnica e da assunção de chamados."""

from __future__ import annotations

import reflex as rx

from app.chamados.shared import DetalheView, TecnicoView, _detalhe_para_dict, _tecnico_para_dict
from app.services.service_desk import criar_cliente_service_desk
from app.services.xano import (
    XanoConflito,
    XanoContratoInvalido,
    XanoEntradaInvalida,
    XanoIndisponivel,
    XanoNaoAutenticado,
    XanoNaoAutorizado,
    XanoNaoEncontrado,
)
from app.states.auth import (
    MENSAGEM_EXPIRADA,
    MENSAGEM_IDENTIDADE_INVALIDA,
    MENSAGEM_INDISPONIVEL,
    MENSAGEM_NAO_AUTORIZADO,
    AuthState,
)


class ChamadosTecnicoState(AuthState):
    """Mantém a fila técnica e a assunção sem ampliar a tratativa."""

    visao: str = "nao_atribuidos"
    chamados: list[TecnicoView] = []
    chamado: DetalheView = {}
    carregando_fila: bool = False
    carregando_detalhe_tecnico: bool = False
    assumindo_id: int | None = None
    mensagem_fila: str = ""
    mensagem_detalhe_tecnico: str = ""
    mensagem_assuncao: str = ""

    @staticmethod
    def visoes() -> list[str]:
        return ["nao_atribuidos", "atribuidos_a_mim"]

    def _limpar_mensagens_tecnico(self) -> None:
        self.mensagem_fila = ""
        self.mensagem_detalhe_tecnico = ""
        self.mensagem_assuncao = ""

    async def _validar_tecnico(self) -> str | None:
        return await self._revalidar("tecnico")

    def _registrar_erro_tecnico(self, erro: Exception, destino: str) -> str | None:
        if isinstance(erro, XanoNaoAutenticado):
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            return "/login"
        if isinstance(erro, XanoNaoAutorizado):
            setattr(self, destino, MENSAGEM_NAO_AUTORIZADO)
            return None
        if isinstance(erro, XanoNaoEncontrado):
            setattr(self, destino, "Chamado não encontrado.")
            return None
        if isinstance(erro, XanoEntradaInvalida):
            setattr(self, destino, "Os dados informados são inválidos.")
            return None
        if isinstance(erro, XanoConflito):
            setattr(self, destino, "Este chamado foi assumido por outro Técnico.")
            return None
        if isinstance(erro, XanoIndisponivel):
            setattr(self, destino, MENSAGEM_INDISPONIVEL)
            return None
        if isinstance(erro, XanoContratoInvalido):
            setattr(self, destino, MENSAGEM_IDENTIDADE_INVALIDA)
            return None
        setattr(self, destino, MENSAGEM_INDISPONIVEL)
        return None

    @rx.event
    async def selecionar_visao(self, visao: str):
        if visao not in self.visoes():
            self.mensagem_fila = "Visão inválida."
            return
        self.visao = visao
        async for evento in self.carregar_fila():
            yield evento

    @rx.event
    async def carregar_fila(self):
        if self.carregando_fila:
            return
        self.carregando_fila = True
        self._limpar_mensagens_tecnico()
        yield
        try:
            destino = await self._validar_tecnico()
            if destino is not None:
                yield rx.redirect(destino)
                return
            if not self.sessao_confirmada:
                return
            try:
                resultado = await criar_cliente_service_desk().listar_chamados_tecnico(
                    self._auth_token,
                    self.visao,
                )
                self.chamados = [_tecnico_para_dict(item) for item in resultado]
            except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
                destino = self._registrar_erro_tecnico(erro, "mensagem_fila")
                if destino is not None:
                    yield rx.redirect(destino)
                    return
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            self._registrar_erro_tecnico(erro, "mensagem_fila")
        finally:
            self.carregando_fila = False

    @rx.event
    async def carregar_detalhe_tecnico(self):
        if self.carregando_detalhe_tecnico:
            return
        self.carregando_detalhe_tecnico = True
        self._limpar_mensagens_tecnico()
        yield
        destino = await self._validar_tecnico()
        if destino is not None:
            self.carregando_detalhe_tecnico = False
            yield rx.redirect(destino)
            return
        if not self.sessao_confirmada:
            self.carregando_detalhe_tecnico = False
            return
        try:
            chamado_id = int(str(self.chamado_id))
            if chamado_id <= 0:
                raise ValueError
        except (AttributeError, TypeError, ValueError):
            self.mensagem_detalhe_tecnico = "Chamado não encontrado."
            self.carregando_detalhe_tecnico = False
            return
        try:
            resultado = await criar_cliente_service_desk().obter_chamado_tecnico(
                self._auth_token,
                chamado_id,
            )
            self.chamado = _detalhe_para_dict(resultado)
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro_tecnico(erro, "mensagem_detalhe_tecnico")
            if destino is not None:
                self.carregando_detalhe_tecnico = False
                yield rx.redirect(destino)
                return
        self.carregando_detalhe_tecnico = False

    @rx.event
    async def assumir(self, chamado_id: int):
        if self.assumindo_id is not None:
            return
        self.assumindo_id = chamado_id
        self.mensagem_assuncao = ""
        try:
            yield
            destino = await self._validar_tecnico()
            if destino is not None:
                yield rx.redirect(destino)
                return
            if not self.sessao_confirmada:
                return
            try:
                resultado = await criar_cliente_service_desk().assumir_chamado_tecnico(
                    self._auth_token,
                    chamado_id,
                )
                self.chamado = _detalhe_para_dict(resultado)
                self.mensagem_assuncao = "Chamado assumido com sucesso."
            except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
                destino = self._registrar_erro_tecnico(erro, "mensagem_assuncao")
                if destino is not None:
                    yield rx.redirect(destino)
                    return
            mensagem_assuncao = self.mensagem_assuncao
            async for evento in self.carregar_fila():
                yield evento
            self.mensagem_assuncao = mensagem_assuncao
            yield
        finally:
            self.assumindo_id = None
