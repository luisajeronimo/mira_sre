"""Estado da jornada de chamados do Gerente."""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, TypedDict

import reflex as rx

from app.services.service_desk import (
    PRIORIDADES_CHAMADO,
    ChamadoDetalhe,
    ChamadoResumo,
    criar_cliente_service_desk,
)
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


def _timestamp_para_texto(valor: int | None) -> str:
    if valor is None:
        return "Não informado"
    try:
        return datetime.fromtimestamp(
            valor / 1000,
            tz=timezone.utc,
        ).astimezone().strftime("%d/%m/%Y %H:%M")
    except (OverflowError, OSError, TypeError, ValueError):
        return "Não informado"


def _numero_para_texto(valor: float | None) -> str:
    if valor is None:
        return "Não informado"
    return f"{valor:g} h"


def _resumo_para_dict(chamado: ChamadoResumo) -> dict[str, Any]:
    return {
        "id": chamado.id,
        "titulo": chamado.titulo,
        "status": chamado.status,
        "prioridade": chamado.prioridade,
        "origem": chamado.origem or "Não informado",
        "criado_em_texto": _timestamp_para_texto(chamado.criado_em),
        "categoria_nome": chamado.categoria.nome,
    }


def _detalhe_para_dict(chamado: ChamadoDetalhe) -> dict[str, Any]:
    dados = asdict(chamado)
    dados["criado_em_texto"] = _timestamp_para_texto(chamado.criado_em)
    dados["sla_horas_texto"] = _numero_para_texto(
        chamado.sla_horas_aplicado
    )
    dados["atribuido_em_texto"] = _timestamp_para_texto(chamado.atribuido_em)
    dados["tecnico_nome"] = (
        chamado.tecnico.nome if chamado.tecnico is not None else "Não atribuído"
    )
    dados["pode_assumir"] = chamado.status == "Novo" and chamado.tecnico is None
    return dados


def _tecnico_para_dict(chamado: ChamadoResumo) -> dict[str, Any]:
    tecnico = chamado.tecnico
    return {
        "id": chamado.id,
        "titulo": chamado.titulo,
        "descricao": chamado.descricao or "",
        "status": chamado.status,
        "prioridade": chamado.prioridade,
        "origem": chamado.origem or "Não informado",
        "criado_em_texto": _timestamp_para_texto(chamado.criado_em),
        "sla_horas_texto": _numero_para_texto(chamado.sla_horas_aplicado),
        "atribuido_em_texto": _timestamp_para_texto(chamado.atribuido_em),
        "categoria_nome": chamado.categoria.nome,
        "tecnico_nome": tecnico.nome if tecnico is not None else "Não atribuído",
        "pode_assumir": chamado.status == "Novo" and tecnico is None,
    }


class ChamadoView(TypedDict):
    id: int
    titulo: str
    status: str
    prioridade: str
    origem: str
    criado_em_texto: str
    categoria_nome: str


class DetalheView(TypedDict, total=False):
    id: int
    titulo: str
    descricao: str
    status: str
    prioridade: str
    origem: str
    criado_em_texto: str
    sla_horas_texto: str
    atribuido_em_texto: str
    tecnico_nome: str
    pode_assumir: bool


class TecnicoView(TypedDict, total=False):
    id: int
    titulo: str
    descricao: str
    status: str
    prioridade: str
    origem: str
    criado_em_texto: str
    sla_horas_texto: str
    atribuido_em_texto: str
    categoria_nome: str
    tecnico_nome: str
    pode_assumir: bool


class CatalogoView(TypedDict):
    id: int
    nome: str


class ChamadosGerenteState(AuthState):
    """Mantém catálogos e dados de chamados separados da autenticação."""

    chamados: list[ChamadoView] = []
    ativos: list[str] = []
    categorias: list[str] = []
    chamado: DetalheView = {}

    carregando_chamados: bool = False
    carregando_formulario: bool = False
    carregando_detalhe: bool = False
    enviando: bool = False
    mensagem_chamados: str = ""
    mensagem_formulario: str = ""
    mensagem_detalhe: str = ""
    mensagem_sucesso: str = ""

    @staticmethod
    def prioridades() -> list[str]:
        return list(PRIORIDADES_CHAMADO)

    def _limpar_mensagens_funcionais(self) -> None:
        self.mensagem_chamados = ""
        self.mensagem_formulario = ""
        self.mensagem_detalhe = ""
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
            resultado = await criar_cliente_service_desk().listar_chamados(
                self._auth_token
            )
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
            resultado = await criar_cliente_service_desk().obter_chamado(
                self._auth_token,
                chamado_id,
            )
            self.chamado = _detalhe_para_dict(resultado)
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro(erro, "mensagem_detalhe")
            if destino is not None:
                self.carregando_detalhe = False
                yield rx.redirect(destino)
            return
        self.carregando_detalhe = False

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

            # A recarga limpa as mensagens funcionais da jornada técnica.
            # Preserve o resultado da assunção para que sucesso/409 continue
            # visível depois que a fila for atualizada.
            mensagem_assuncao = self.mensagem_assuncao
            async for evento in self.carregar_fila():
                yield evento
            self.mensagem_assuncao = mensagem_assuncao
            yield
        finally:
            self.assumindo_id = None
