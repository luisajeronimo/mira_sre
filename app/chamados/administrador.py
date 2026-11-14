"""Abertura manual global dos perfis operacionais na jornada compartilhada de chamados."""

from __future__ import annotations

from typing import Any

import reflex as rx

from app.chamados.gerente.pages import formulario_abertura
from app.components.layout import casca_conteudo, estado_carregamento, estado_revalidacao
from app.services.service_desk import criar_cliente_service_desk
from app.services.xano import (
    XanoContratoInvalido, XanoEntradaInvalida, XanoIndisponivel,
    XanoNaoAutenticado, XanoNaoAutorizado,
)
from app.states.auth import AuthState, MENSAGEM_EXPIRADA, MENSAGEM_INDISPONIVEL, MENSAGEM_NAO_AUTORIZADO


class AberturaAdminState(AuthState):
    ativos_formulario: list[dict[str, Any]] = []
    categorias_formulario: list[dict[str, Any]] = []
    ativo_formulario: str = ""
    categoria_formulario: str = ""
    prioridade_formulario: str = ""
    titulo_formulario: str = ""
    descricao_formulario: str = ""
    carregando_formulario: bool = False
    enviando: bool = False
    mensagem_formulario: str = ""
    usuario_id_contexto_abertura: int = 0

    @staticmethod
    def prioridades() -> list[str]:
        return ["Baixa", "Média", "Alta", "Urgente"]

    def _contexto(self) -> tuple[int | None, str, int]:
        return self.usuario_id, self._auth_token, self._versao_sessao

    def _contexto_valido(self, contexto: tuple[int | None, str, int]) -> bool:
        return self.sessao_confirmada and self.perfil_operacional and self._contexto() == contexto

    def _limpar(self) -> None:
        self.ativos_formulario = []
        self.categorias_formulario = []
        self.ativo_formulario = ""
        self.categoria_formulario = ""
        self.prioridade_formulario = ""
        self.titulo_formulario = ""
        self.descricao_formulario = ""
        self.mensagem_formulario = ""

    @rx.event
    def alterar_ativo_formulario(self, valor: str):
        self.ativo_formulario = valor

    @rx.event
    def alterar_categoria_formulario(self, valor: str):
        self.categoria_formulario = valor

    @rx.event
    def alterar_prioridade_formulario(self, valor: str):
        self.prioridade_formulario = valor

    @rx.event
    def alterar_titulo_formulario(self, valor: str):
        self.titulo_formulario = valor

    @rx.event
    def alterar_descricao_formulario(self, valor: str):
        self.descricao_formulario = valor

    @rx.event
    def limpar_formulario(self):
        self.ativo_formulario = self.categoria_formulario = self.prioridade_formulario = ""
        self.titulo_formulario = self.descricao_formulario = self.mensagem_formulario = ""

    @rx.event
    def descartar_formulario(self):
        self._limpar()
        return rx.redirect("/inicio")

    @rx.event
    def voltar_para_lista(self):
        return rx.redirect("/inicio")

    @rx.event
    async def carregar_formulario(self):
        if self.carregando_formulario:
            return
        self.carregando_formulario = True
        self.mensagem_formulario = ""
        yield
        async for evento in self._executar_guard(None, False):
            yield evento
        if not self.sessao_confirmada or not self.perfil_operacional or self.deve_trocar_senha:
            self._limpar()
            self.carregando_formulario = False
            return
        if self.usuario_id_contexto_abertura != self.usuario_id:
            self._limpar()
            self.usuario_id_contexto_abertura = self.usuario_id or 0
        contexto = self._contexto()
        try:
            opcoes = await criar_cliente_service_desk().opcoes_abertura_global(self._auth_token)
            if not self._contexto_valido(contexto):
                return
            self.ativos_formulario = opcoes["ativos"]
            self.categorias_formulario = opcoes["categorias"]
        except XanoNaoAutenticado:
            self._limpar()
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            yield rx.redirect("/login")
        except XanoNaoAutorizado:
            self.mensagem_formulario = MENSAGEM_NAO_AUTORIZADO
        except (XanoEntradaInvalida, XanoContratoInvalido, XanoIndisponivel):
            self.mensagem_formulario = MENSAGEM_INDISPONIVEL
        finally:
            self.carregando_formulario = False

    @rx.event
    async def abrir_chamado(self, _dados: dict[str, Any] | None = None):
        if self.enviando:
            return
        self.enviando = True
        self.mensagem_formulario = ""
        yield
        async for evento in self._executar_guard(None, False):
            yield evento
        if not self.sessao_confirmada or not self.perfil_operacional or self.deve_trocar_senha:
            self.enviando = False
            return
        contexto = self._contexto()
        try:
            ativo_id = int(self.ativo_formulario)
            categoria_id = int(self.categoria_formulario)
            if not self.prioridade_formulario or not self.titulo_formulario.strip() or not self.descricao_formulario.strip():
                raise ValueError
            resultado = await criar_cliente_service_desk().abrir_chamado_global(
                self._auth_token, ativos_referencia_id=ativo_id, categorias_servico_id=categoria_id,
                prioridade=self.prioridade_formulario, titulo=self.titulo_formulario,
                descricao=self.descricao_formulario,
            )
            if not self._contexto_valido(contexto):
                return
            self._limpar()
            yield rx.toast.success("Chamado aberto com sucesso.")
            yield rx.redirect(f"/chamados/{resultado['id']}")
        except (ValueError, TypeError):
            self.mensagem_formulario = "Preencha Totem, Categoria, prioridade, título e descrição."
        except XanoNaoAutenticado:
            self._limpar()
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            yield rx.redirect("/login")
        except XanoNaoAutorizado:
            self.mensagem_formulario = MENSAGEM_NAO_AUTORIZADO
        except XanoEntradaInvalida as erro:
            self.mensagem_formulario = str(erro)
        except (XanoContratoInvalido, XanoIndisponivel):
            self.mensagem_formulario = MENSAGEM_INDISPONIVEL
        finally:
            self.enviando = False


def novo_chamado_administrador() -> rx.Component:
    return rx.cond(
        AuthState.carregando, estado_carregamento(),
        rx.cond(AuthState.sessao_confirmada & AuthState.perfil_operacional,
                casca_conteudo(formulario_abertura(AberturaAdminState, "qualquer Totem da rede"), "/inicio"),
                estado_revalidacao(AberturaAdminState.carregar_formulario)),
    )
