"""State da jornada de chamados do Gerente."""

from __future__ import annotations

import asyncio
from typing import Any

import reflex as rx

from app.chamados.shared import (
    ChamadoView,
    ComentarioView,
    DetalheView,
    _detalhe_para_dict,
    _resumo_para_dict,
    comentario_publico_para_dict,
)
from app.services.service_desk import PRIORIDADES_CHAMADO, criar_cliente_service_desk
from app.services.xano import (
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


class ChamadosGerenteState(AuthState):
    """Mantém catálogos e dados de chamados separados da autenticação."""

    chamados: list[ChamadoView] = []
    ativos: list[str] = []
    categorias: list[str] = []
    chamado: DetalheView = {}
    comentarios: list[ComentarioView] = []
    rascunho_comentario: str = ""

    carregando_chamados: bool = False
    carregando_formulario: bool = False
    carregando_detalhe: bool = False
    carregando_comentarios: bool = False
    detalhe_carregado: bool = False
    enviando: bool = False
    enviando_comentario: bool = False
    mensagem_chamados: str = ""
    mensagem_formulario: str = ""
    mensagem_detalhe: str = ""
    mensagem_comentarios: str = ""
    mensagem_sucesso: str = ""

    @staticmethod
    def prioridades() -> list[str]:
        return list(PRIORIDADES_CHAMADO)

    def _limpar_mensagens_funcionais(self) -> None:
        self.mensagem_chamados = ""
        self.mensagem_formulario = ""
        self.mensagem_detalhe = ""
        self.mensagem_comentarios = ""
        self.mensagem_sucesso = ""

    def _registrar_erro(self, erro: Exception, destino: str) -> str | None:
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
        if isinstance(erro, XanoIndisponivel):
            setattr(self, destino, MENSAGEM_INDISPONIVEL)
            return None
        if isinstance(erro, XanoContratoInvalido):
            setattr(self, destino, MENSAGEM_IDENTIDADE_INVALIDA)
            return None
        setattr(self, destino, MENSAGEM_INDISPONIVEL)
        return None

    async def _validar_gerente(self) -> str | None:
        return await self._revalidar("gerente")

    @rx.event
    async def carregar_lista(self):
        if self.carregando_chamados:
            return
        self.carregando_chamados = True
        self._limpar_mensagens_funcionais()
        yield
        destino = await self._validar_gerente()
        if destino is not None:
            self.carregando_chamados = False
            yield rx.redirect(destino)
            return
        if not self.sessao_confirmada:
            self.carregando_chamados = False
            return
        try:
            resultado = await criar_cliente_service_desk().listar_chamados(self._auth_token)
            self.chamados = [_resumo_para_dict(item) for item in resultado]
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro(erro, "mensagem_chamados")
            if destino is not None:
                self.carregando_chamados = False
                yield rx.redirect(destino)
                return
        self.carregando_chamados = False

    @rx.event
    async def carregar_formulario(self):
        if self.carregando_formulario:
            return
        self.carregando_formulario = True
        self._limpar_mensagens_funcionais()
        yield
        destino = await self._validar_gerente()
        if destino is not None:
            self.carregando_formulario = False
            yield rx.redirect(destino)
            return
        if not self.sessao_confirmada:
            self.carregando_formulario = False
            return
        try:
            cliente = criar_cliente_service_desk()
            ativos, categorias = await asyncio.gather(
                cliente.listar_ativos(self._auth_token),
                cliente.listar_categorias(self._auth_token),
            )
            self.ativos = [f"{item.id} — {item.nome_ativo}" for item in ativos]
            self.categorias = [f"{item.id} — {item.nome}" for item in categorias]
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro(erro, "mensagem_formulario")
            if destino is not None:
                self.carregando_formulario = False
                yield rx.redirect(destino)
                return
        self.carregando_formulario = False

    @rx.event
    async def carregar_detalhe(self):
        if self.carregando_detalhe:
            return
        self.carregando_detalhe = True
        self.detalhe_carregado = False
        self.chamado = {}
        self.comentarios = []
        self.rascunho_comentario = ""
        self._limpar_mensagens_funcionais()
        yield
        destino = await self._validar_gerente()
        if destino is not None:
            self.carregando_detalhe = False
            yield rx.redirect(destino)
            return
        if not self.sessao_confirmada:
            self.carregando_detalhe = False
            return
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
            resultado = await cliente.obter_chamado(self._auth_token, chamado_id)
            self.chamado = _detalhe_para_dict(resultado)
            self.detalhe_carregado = True
            self.carregando_comentarios = True
            try:
                comentarios = await cliente.listar_comentarios_publicos(
                    self._auth_token,
                    chamado_id,
                )
                self.comentarios = [
                    comentario_publico_para_dict(comentario)
                    for comentario in comentarios
                ]
            except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
                destino = self._registrar_erro(erro, "mensagem_comentarios")
                if destino is not None:
                    self.carregando_detalhe = False
                    yield rx.redirect(destino)
                    return
            finally:
                self.carregando_comentarios = False
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro(erro, "mensagem_detalhe")
            if destino is not None:
                self.carregando_detalhe = False
                yield rx.redirect(destino)
            return
        self.carregando_detalhe = False

    @rx.event
    async def publicar_comentario(self):
        if self.enviando_comentario:
            return
        self.enviando_comentario = True
        self.mensagem_comentarios = ""
        yield
        destino = await self._validar_gerente()
        if destino is not None:
            self.enviando_comentario = False
            yield rx.redirect(destino)
            return
        if not self.sessao_confirmada:
            self.enviando_comentario = False
            return
        try:
            chamado_id = int(str(self.chamado_id))
            if chamado_id <= 0:
                raise ValueError
        except (AttributeError, TypeError, ValueError):
            self.mensagem_comentarios = "Chamado não encontrado."
            self.enviando_comentario = False
            return
        try:
            cliente = criar_cliente_service_desk()
            comentario = await cliente.criar_comentario_publico(
                self._auth_token,
                chamado_id,
                conteudo=self.rascunho_comentario,
            )
            self.comentarios = [comentario_publico_para_dict(comentario)] + self.comentarios
            self.rascunho_comentario = ""
            resultado = await cliente.obter_chamado(self._auth_token, chamado_id)
            self.chamado = _detalhe_para_dict(resultado)
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro(erro, "mensagem_comentarios")
            if destino is not None:
                self.enviando_comentario = False
                yield rx.redirect(destino)
                return
        self.enviando_comentario = False

    @rx.event
    def descartar_rascunho_comentario(self):
        """Descarta somente o rascunho local, sem chamada ao backend."""
        self.rascunho_comentario = ""

    @rx.event
    def alterar_rascunho_comentario(self, conteudo: str):
        """Mantém o rascunho exclusivamente no State local."""
        self.rascunho_comentario = conteudo

    @rx.event
    async def abrir_chamado(self, form_data: dict[str, Any]):
        if self.enviando:
            return
        self.enviando = True
        self.mensagem_formulario = ""
        self.mensagem_sucesso = ""
        yield
        try:
            ativo_id = int(str(form_data.get("ativos_referencia_id", "")).split(" — ", 1)[0])
            categoria_id = int(str(form_data.get("categorias_servico_id", "")).split(" — ", 1)[0])
        except (TypeError, ValueError):
            self.mensagem_formulario = "Selecione um ativo e uma categoria."
            self.enviando = False
            return
        try:
            resultado = await criar_cliente_service_desk().abrir_chamado(
                self._auth_token,
                ativos_referencia_id=ativo_id,
                categorias_servico_id=categoria_id,
                prioridade=str(form_data.get("prioridade", "")),
                titulo=str(form_data.get("titulo", "")),
                descricao=str(form_data.get("descricao", "")),
            )
            self.chamado = _detalhe_para_dict(resultado)
            self.mensagem_sucesso = "Chamado aberto com sucesso."
            self.enviando = False
            yield rx.redirect(f"/gerente/chamados/{resultado.id}")
            return
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro(erro, "mensagem_formulario")
            self.enviando = False
            if destino is not None:
                yield rx.redirect(destino)
                return
