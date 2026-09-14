"""Estado da sessão autenticada da aplicação Reflex."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import reflex as rx

from app.services.xano import (
    CredenciaisInvalidas,
    IdentidadeXano,
    XanoContratoInvalido,
    XanoIndisponivel,
    XanoNaoAutenticado,
    XanoNaoAutorizado,
    criar_cliente_xano,
)


DESTINOS_POR_PERFIL = {
    "gerente": "/gerente",
    "tecnico": "/tecnico",
    "diretoria": "/diretoria",
}

MENSAGEM_CREDENCIAIS = "Credenciais inválidas."
MENSAGEM_EXPIRADA = "Sua sessão expirou. Entre novamente."
MENSAGEM_INDISPONIVEL = (
    "O serviço está indisponível no momento. Tente novamente."
)
MENSAGEM_NAO_AUTORIZADO = "Acesso não autorizado."
MENSAGEM_IDENTIDADE_INVALIDA = "Não foi possível validar sua identidade."


class AuthState(rx.State):
    """Mantém a identidade pública e o token apenas no backend da sessão."""

    _auth_token: str = ""

    usuario_id: int | None = None
    nome: str = ""
    email: str = ""
    role: str = ""
    lojas_id: int | None = None

    carregando: bool = False
    sessao_confirmada: bool = False
    mensagem_erro: str = ""

    def _iniciar_carregamento(self) -> None:
        self.carregando = True
        self.sessao_confirmada = False
        self.mensagem_erro = ""

    def _finalizar_carregamento(self) -> None:
        self.carregando = False

    def _limpar_identidade(self) -> None:
        self.usuario_id = None
        self.nome = ""
        self.email = ""
        self.role = ""
        self.lojas_id = None
        self.sessao_confirmada = False

    def _limpar_sessao(self, mensagem: str = "") -> None:
        self._auth_token = ""
        self._limpar_identidade()
        self.carregando = False
        self.mensagem_erro = mensagem

    def _publicar_identidade(self, identidade: IdentidadeXano) -> None:
        destino = DESTINOS_POR_PERFIL.get(identidade.role)
        if destino is None:
            raise XanoContratoInvalido(
                "A identidade não possui um perfil oficial."
            )

        self.usuario_id = identidade.id
        self.nome = identidade.nome
        self.email = identidade.email
        self.role = identidade.role
        self.lojas_id = identidade.lojas_id
        self.sessao_confirmada = True
        self.mensagem_erro = ""

    @staticmethod
    def destino_por_perfil(role: str) -> str | None:
        return DESTINOS_POR_PERFIL.get(role)

    async def _revalidar(
        self,
        perfil_esperado: str | None = None,
    ) -> str | None:
        if not self._auth_token:
            self._limpar_sessao()
            return "/login"

        try:
            identidade = await criar_cliente_xano().obter_identidade(
                self._auth_token
            )
            self._publicar_identidade(identidade)
        except XanoNaoAutenticado:
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            return "/login"
        except XanoNaoAutorizado:
            self.sessao_confirmada = False
            self.mensagem_erro = MENSAGEM_NAO_AUTORIZADO
            return None
        except XanoIndisponivel:
            self.sessao_confirmada = False
            self.mensagem_erro = MENSAGEM_INDISPONIVEL
            return None
        except XanoContratoInvalido:
            self._limpar_sessao(MENSAGEM_IDENTIDADE_INVALIDA)
            return "/login"

        destino = self.destino_por_perfil(self.role)
        if perfil_esperado is not None and self.role != perfil_esperado:
            return destino
        return None

    @rx.event
    async def login(
        self,
        form_data: dict[str, Any],
    ) -> AsyncIterator[Any]:
        if self.carregando:
            return

        self._limpar_sessao()
        self.carregando = True
        yield

        email = str(form_data.get("email", "")).strip().lower()
        senha = str(form_data.get("senha", ""))

        try:
            cliente = criar_cliente_xano()
            self._auth_token = await cliente.login(email, senha)
            identidade = await cliente.obter_identidade(self._auth_token)
            self._publicar_identidade(identidade)
        except CredenciaisInvalidas:
            self._limpar_sessao(MENSAGEM_CREDENCIAIS)
            return
        except XanoNaoAutenticado:
            self._limpar_sessao(MENSAGEM_CREDENCIAIS)
            return
        except XanoNaoAutorizado:
            self._limpar_sessao(MENSAGEM_NAO_AUTORIZADO)
            return
        except XanoIndisponivel:
            self._limpar_sessao(MENSAGEM_INDISPONIVEL)
            return
        except XanoContratoInvalido:
            self._limpar_sessao(MENSAGEM_IDENTIDADE_INVALIDA)
            return

        self._finalizar_carregamento()
        destino = self.destino_por_perfil(self.role)
        if destino is None:
            self._limpar_sessao(MENSAGEM_IDENTIDADE_INVALIDA)
            return
        yield rx.redirect(destino)

    async def _executar_guard(
        self,
        perfil_esperado: str | None,
        redirecionar_ao_confirmar: bool,
    ) -> AsyncIterator[Any]:
        self._iniciar_carregamento()
        yield
        destino = await self._revalidar(perfil_esperado)
        self._finalizar_carregamento()

        if destino is not None:
            yield rx.redirect(destino)
            return
        if redirecionar_ao_confirmar and self.sessao_confirmada:
            destino = self.destino_por_perfil(self.role)
            if destino is not None:
                yield rx.redirect(destino)

    @rx.event
    async def carregar_raiz(self) -> AsyncIterator[Any]:
        async for evento in self._executar_guard(None, True):
            yield evento

    @rx.event
    async def carregar_login(self) -> AsyncIterator[Any]:
        if not self._auth_token:
            self._limpar_identidade()
            self.carregando = False
            return

        async for evento in self._executar_guard(None, True):
            yield evento

    @rx.event
    async def carregar_gerente(self) -> AsyncIterator[Any]:
        async for evento in self._executar_guard("gerente", False):
            yield evento

    @rx.event
    async def carregar_tecnico(self) -> AsyncIterator[Any]:
        async for evento in self._executar_guard("tecnico", False):
            yield evento

    @rx.event
    async def carregar_diretoria(self) -> AsyncIterator[Any]:
        async for evento in self._executar_guard("diretoria", False):
            yield evento

    @rx.event
    def logout(self):
        self._limpar_sessao()
        return rx.redirect("/login")
