"""Criação administrativa mínima de usuários."""

from __future__ import annotations

from typing import Any, TypedDict

import reflex as rx

from app.components.layout import casca_conteudo, estado_carregamento, estado_revalidacao
from app.services.xano import (
    LojaOpcaoAdministracaoXano,
    XanoContratoInvalido,
    XanoEntradaInvalida,
    XanoIndisponivel,
    XanoNaoAutenticado,
    XanoNaoAutorizado,
    criar_cliente_xano,
)
from app.states.auth import AuthState, MENSAGEM_EXPIRADA, MENSAGEM_INDISPONIVEL, MENSAGEM_NAO_AUTORIZADO


class LojaOpcaoView(TypedDict):
    id: int
    nome: str


class AdministracaoState(AuthState):
    """Estado não sensível da criação administrativa."""

    enviando_usuario: bool = False
    mensagem_usuario: str = ""
    sucesso_usuario: str = ""
    perfil_selecionado: str = ""
    opcoes_lojas: list[LojaOpcaoView] = []
    loja_selecionada: str = ""
    carregando_lojas: bool = False
    opcoes_lojas_carregadas: bool = False
    erro_lojas: str = ""

    @staticmethod
    def perfis_criaveis() -> list[str]:
        return ["gerente", "tecnico", "diretoria", "administrador"]

    @rx.event
    def selecionar_perfil(self, role: str):
        self.perfil_selecionado = role
        if role != "gerente":
            self.loja_selecionada = ""

    @rx.event
    def selecionar_loja(self, loja_id: str):
        self.loja_selecionada = loja_id

    @rx.event
    async def carregar_administracao(self):
        if self.carregando_lojas:
            return
        self.carregando_lojas = True
        self.erro_lojas = ""
        async for evento in self._executar_guard("administrador", False):
            yield evento

        if (
            not self.sessao_confirmada
            or self.role != "administrador"
            or self.deve_trocar_senha
        ):
            self.carregando_lojas = False
            return
        if self.opcoes_lojas_carregadas:
            self.carregando_lojas = False
            return

        try:
            lojas = await criar_cliente_xano().listar_lojas_administracao(
                self._auth_token
            )
            self.opcoes_lojas = [
                {"id": loja.id, "nome": loja.nome} for loja in lojas
            ]
            self.opcoes_lojas_carregadas = True
        except XanoNaoAutenticado:
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            yield rx.redirect("/login")
        except XanoNaoAutorizado:
            self.erro_lojas = MENSAGEM_NAO_AUTORIZADO
        except XanoIndisponivel:
            self.erro_lojas = MENSAGEM_INDISPONIVEL
        except XanoContratoInvalido:
            self.erro_lojas = "Não foi possível carregar a lista de Lojas."
        finally:
            self.carregando_lojas = False

    @rx.event
    async def criar_usuario(self, form_data: dict[str, Any]):
        if self.enviando_usuario:
            return
        self.mensagem_usuario = ""
        self.sucesso_usuario = ""
        role = str(form_data.get("role", ""))
        senha = str(form_data.get("senha_temporaria", ""))
        confirmacao = str(form_data.get("confirmacao", ""))
        loja_texto = str(form_data.get("lojas_id", "")).strip()
        if role not in self.perfis_criaveis():
            self.mensagem_usuario = "Selecione um perfil válido."
            return
        if len(senha) < 8:
            self.mensagem_usuario = "A senha deve ter pelo menos 8 caracteres."
            return
        if senha != confirmacao:
            self.mensagem_usuario = "A confirmação de senha não confere."
            return
        lojas_id = None
        if role == "gerente":
            ids_validos = {str(loja["id"]) for loja in self.opcoes_lojas}
            if not loja_texto:
                self.mensagem_usuario = "Gerente exige Loja."
                return
            if loja_texto not in ids_validos:
                self.mensagem_usuario = "Selecione uma Loja válida."
                return
            try:
                lojas_id = int(loja_texto)
            except ValueError:
                self.mensagem_usuario = "Selecione uma Loja válida."
                return
        self.enviando_usuario = True
        yield
        try:
            await criar_cliente_xano().criar_usuario_administrativo(
                self._auth_token,
                nome=str(form_data.get("nome", "")),
                email=str(form_data.get("email", "")).strip().lower(),
                role=role,
                lojas_id=lojas_id,
                senha_temporaria=senha,
            )
            self.sucesso_usuario = "Usuário criado com sucesso."
        except XanoNaoAutenticado:
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            yield rx.redirect("/login")
        except XanoNaoAutorizado:
            self.mensagem_usuario = MENSAGEM_NAO_AUTORIZADO
        except XanoEntradaInvalida:
            self.mensagem_usuario = "Não foi possível criar o usuário. Verifique os dados informados."
        except XanoContratoInvalido:
            self.mensagem_usuario = "Não foi possível confirmar a criação do usuário."
        except XanoIndisponivel:
            self.mensagem_usuario = MENSAGEM_INDISPONIVEL
        finally:
            self.enviando_usuario = False


def administracao() -> rx.Component:
    seletor_loja = rx.select.root(
        rx.select.trigger(placeholder="Selecione uma Loja", width="100%"),
        rx.select.content(
            rx.select.group(
                rx.foreach(
                    AdministracaoState.opcoes_lojas,
                    lambda loja: rx.select.item(
                        loja["nome"], value=loja["id"].to_string()
                    ),
                )
            )
        ),
        name="lojas_id",
        value=AdministracaoState.loja_selecionada,
        on_change=AdministracaoState.selecionar_loja,
        required=True,
        width="100%",
    )
    seletor_condicional = rx.cond(
        AdministracaoState.carregando_lojas,
        rx.hstack(rx.spinner(size="2"), rx.text("Carregando Lojas...")),
        rx.cond(
            AdministracaoState.erro_lojas != "",
            rx.vstack(
                rx.callout(AdministracaoState.erro_lojas, color_scheme="red"),
                rx.button(
                    "Tentar carregar Lojas novamente",
                    type="button",
                    on_click=AdministracaoState.carregar_administracao,
                ),
                width="100%",
                align="start",
            ),
            rx.cond(
                AdministracaoState.opcoes_lojas.length() == 0,
                rx.callout("Nenhuma Loja disponível para associação.", icon="info"),
                seletor_loja,
            ),
        ),
    )
    formulario = rx.form(
        rx.vstack(
            rx.input(name="nome", placeholder="Nome", required=True, width="100%"),
            rx.input(name="email", type="email", placeholder="E-mail", required=True, width="100%"),
            rx.select(AdministracaoState.perfis_criaveis(), name="role", placeholder="Perfil", required=True, on_change=AdministracaoState.selecionar_perfil, width="100%"),
            rx.cond(
                AdministracaoState.perfil_selecionado == "gerente",
                seletor_condicional,
            ),
            rx.input(name="senha_temporaria", type="password", placeholder="Senha temporária", min_length=8, required=True, width="100%"),
            rx.input(name="confirmacao", type="password", placeholder="Confirme a senha temporária", min_length=8, required=True, width="100%"),
            rx.cond(AdministracaoState.mensagem_usuario != "", rx.callout(AdministracaoState.mensagem_usuario, color_scheme="red", width="100%")),
            rx.cond(AdministracaoState.sucesso_usuario != "", rx.callout(AdministracaoState.sucesso_usuario, color_scheme="green", width="100%")),
            rx.button(rx.cond(AdministracaoState.enviando_usuario, "Criando...", "Criar usuário"), type="submit", disabled=AdministracaoState.enviando_usuario),
            width="100%", spacing="3",
        ), on_submit=AdministracaoState.criar_usuario, reset_on_submit=True, width="100%",
    )
    conteudo = rx.card(rx.vstack(rx.heading("Usuários", size="6"), rx.text("Crie uma conta com senha temporária."), formulario, align="start", width="100%", spacing="4"), max_width="34rem", width="100%")
    return rx.cond(
        AuthState.carregando,
        estado_carregamento(),
        rx.cond(
            AuthState.sessao_confirmada & (AuthState.role == "administrador"),
            casca_conteudo(conteudo, "/administracao"),
            estado_revalidacao(AdministracaoState.carregar_administracao),
        ),
    )


def primeiro_acesso() -> rx.Component:
    formulario = rx.form(
        rx.vstack(
            rx.input(name="nova_senha", type="password", placeholder="Nova senha", min_length=8, required=True, width="100%"),
            rx.input(name="confirmacao", type="password", placeholder="Confirme a nova senha", min_length=8, required=True, width="100%"),
            rx.cond(AuthState.mensagem_erro != "", rx.callout(AuthState.mensagem_erro, color_scheme="red", width="100%")),
            rx.button(rx.cond(AuthState.carregando, "Salvando...", "Salvar nova senha"), type="submit", disabled=AuthState.carregando),
            width="100%", spacing="3",
        ), on_submit=AuthState.trocar_senha_primeiro_acesso, reset_on_submit=True, width="100%",
    )
    return rx.center(rx.card(rx.vstack(rx.heading("Defina uma nova senha", size="6"), rx.text("Para continuar, substitua sua senha temporária."), formulario, width="100%", spacing="4"), max_width="28rem", width="100%"), min_height="100vh", padding="2rem")
