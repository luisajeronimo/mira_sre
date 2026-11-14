"""Gestão dos cadastros administrativos pelos contratos específicos do Xano."""

from __future__ import annotations

from typing import Any, TypedDict

import reflex as rx

from app.components.layout import casca_conteudo, estado_carregamento, estado_revalidacao
from app.components.visual import BORDA, SOMBRA_BAIXA, SUPERFICIE, SUPERFICIE_SUAVE, TEXTO, TEXTO_SECUNDARIO
from app.services.xano import (
    XanoConflito, XanoContratoInvalido, XanoEntradaInvalida, XanoIndisponivel,
    XanoNaoAutenticado, XanoNaoAutorizado, XanoNaoEncontrado, criar_cliente_xano,
)
from app.states.auth import AuthState, MENSAGEM_EXPIRADA, MENSAGEM_INDISPONIVEL, MENSAGEM_NAO_AUTORIZADO


class LojaView(TypedDict):
    id: int
    nome: str
    endereco: str
    regiao: str
    status: str


class TotemView(TypedDict):
    id: int
    identificacao: str
    nome: str
    lojas_id: int
    loja_nome: str
    status_atual: str


class UsuarioView(TypedDict):
    id: int
    nome: str
    email: str
    role: str
    lojas_id: int
    loja_nome: str


class GestaoAdministrativaState(AuthState):
    aba: str = ""
    modal: str = ""
    busca: str = ""
    lojas: list[LojaView] = []
    lojas_destino: list[LojaView] = []
    totens: list[TotemView] = []
    usuarios: list[UsuarioView] = []
    carregando_cadastros: bool = False
    processando: bool = False
    erro: str = ""
    sucesso: str = ""
    edicao_id: int = 0
    exclusao_id: int = 0
    exclusao_tipo: str = ""
    erro_exclusao: str = ""
    nome_form: str = ""
    endereco: str = ""
    regiao: str = ""
    status: str = "Ativa"
    identificacao: str = ""
    email_form: str = ""
    perfil_usuario: str = "gerente"
    loja_form_id: str = ""
    usuario_id_contexto: int = 0
    _token_contexto_admin: str = ""
    _versao_contexto_admin: int = -1

    def _atualizar_destinos(self) -> None:
        self.lojas_destino = [
            loja for loja in self.lojas
            if loja["status"] in {"Ativa", "Ativo"}
            or (self.edicao_id > 0 and str(loja["id"]) == self.loja_form_id)
        ]

    @rx.event
    def set_nome_form(self, valor: str):
        self.nome_form = valor

    @rx.event
    def set_endereco(self, valor: str):
        self.endereco = valor

    @rx.event
    def set_regiao(self, valor: str):
        self.regiao = valor

    @rx.event
    def set_status(self, valor: str):
        self.status = valor

    @rx.event
    def set_identificacao(self, valor: str):
        self.identificacao = valor

    @rx.event
    def set_email_form(self, valor: str):
        self.email_form = valor

    @rx.event
    def set_perfil_usuario(self, valor: str):
        self.perfil_usuario = valor
        if valor != "gerente":
            self.loja_form_id = ""

    @rx.event
    def set_loja_form_id(self, valor: str):
        self.loja_form_id = valor

    @rx.event
    def set_busca(self, valor: str):
        self.busca = valor


    def _limpar_formulario(self) -> None:
        self.edicao_id = 0
        self.nome_form = ""
        self.endereco = ""
        self.regiao = ""
        self.status = "Ativa"
        self.identificacao = ""
        self.email_form = ""
        self.perfil_usuario = "gerente"
        self.loja_form_id = ""
        self.exclusao_id = 0
        self.exclusao_tipo = ""
        self.erro_exclusao = ""
        self._atualizar_destinos()

    @rx.event
    def abrir_modal(self, tipo: str):
        if tipo in {"loja", "totem", "usuario"}:
            self._limpar_formulario()
            self.modal = tipo
            self.erro = self.sucesso = ""

    @rx.event
    def fechar_modal(self):
        if not self.processando:
            self.modal = ""
            self._limpar_formulario()
            self.erro = ""

    @rx.event
    def definir_modal_aberto(self, aberto: bool):
        if not aberto and not self.processando:
            self.modal = ""
            self._limpar_formulario()
            self.erro = ""

    def _mensagem_erro(self, erro: Exception) -> str:
        if isinstance(erro, XanoNaoAutorizado):
            return MENSAGEM_NAO_AUTORIZADO
        if isinstance(erro, XanoEntradaInvalida):
            mensagem = str(erro)
            return mensagem if mensagem != "Os dados informados são inválidos." else "Operação rejeitada. Verifique os dados e as dependências do cadastro."
        if isinstance(erro, XanoNaoEncontrado):
            return "Cadastro não encontrado. Atualize a lista e tente novamente."
        if isinstance(erro, XanoConflito):
            return "O cadastro foi alterado por outra operação. Atualize a lista."
        if isinstance(erro, XanoContratoInvalido):
            return "A resposta do serviço não pôde ser confirmada."
        return MENSAGEM_INDISPONIVEL

    def _limpar_cadastros(self) -> None:
        self.lojas = []
        self.lojas_destino = []
        self.totens = []
        self.usuarios = []
        self._limpar_formulario()
        self.modal = self.aba = self.busca = ""

    async def _atualizar_listas(self, apenas: str | None = None) -> None:
        cliente = criar_cliente_xano()
        token = self._auth_token
        usuario_id = self.usuario_id
        versao = self._versao_sessao
        lojas = await cliente.listar_registros_lojas(token) if apenas in (None, "lojas") else None
        totens = await cliente.listar_totens_administracao(token) if apenas in (None, "totens") else None
        usuarios = await cliente.listar_usuarios_administracao(token) if apenas in (None, "usuarios") else None
        if token != self._auth_token or usuario_id != self.usuario_id or versao != self._versao_sessao:
            return
        if lojas is not None:
            self.lojas = [
                {"id": x.id, "nome": x.nome or "", "endereco": x.endereco or "", "regiao": x.regiao or "",
                 "status": {"ativa": "Ativa", "inativa": "Inativa"}.get(x.status or "", x.status or "Não informada")}
                for x in lojas
            ]
            self._atualizar_destinos()
            for totem in self.totens:
                totem["loja_nome"] = next(
                    (loja["nome"] for loja in self.lojas if loja["id"] == totem["lojas_id"]),
                    "Loja não encontrada" if totem["lojas_id"] else "Não informada",
                )
            for usuario in self.usuarios:
                usuario["loja_nome"] = next(
                    (loja["nome"] for loja in self.lojas if loja["id"] == usuario["lojas_id"]),
                    "Loja não encontrada" if usuario["lojas_id"] else "—",
                )
        if totens is not None:
            self.totens = [
                {"id": x.id, "identificacao": x.identificacao or "", "nome": x.nome or "",
                 "lojas_id": x.lojas_id or 0,
                 "loja_nome": next((loja["nome"] for loja in self.lojas if loja["id"] == x.lojas_id),
                                    "Loja não encontrada" if x.lojas_id else "Não informada"),
                 "status_atual": {"online": "Online", "offline": "Offline"}.get(
                     (x.status_atual or "").casefold(), x.status_atual or "Não informado")}
                for x in totens
            ]
        if usuarios is not None:
            self.usuarios = [
                {"id": x.id, "nome": x.nome, "email": x.email, "role": x.role,
                 "lojas_id": x.lojas_id or 0,
                 "loja_nome": next((loja["nome"] for loja in self.lojas if loja["id"] == x.lojas_id),
                                    "Loja não encontrada" if x.lojas_id else "—")}
                for x in usuarios
            ]

    @rx.event
    async def carregar(self):
        if self.carregando_cadastros:
            return
        self.carregando_cadastros = True
        self.erro = ""
        async for evento in self._executar_guard("administrador", False):
            yield evento
        if not self.sessao_confirmada or self.role != "administrador" or self.deve_trocar_senha:
            self._limpar_cadastros()
            self.carregando_cadastros = False
            return
        if (self.usuario_id_contexto != self.usuario_id or self._token_contexto_admin != self._auth_token
                or self._versao_contexto_admin != self._versao_sessao):
            self._limpar_cadastros()
            self.usuario_id_contexto = self.usuario_id or 0
            self._token_contexto_admin = self._auth_token
            self._versao_contexto_admin = self._versao_sessao
        try:
            await self._atualizar_listas()
        except XanoNaoAutenticado:
            self._limpar_cadastros()
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            yield rx.redirect("/login")
        except (XanoNaoAutorizado, XanoNaoEncontrado, XanoConflito, XanoEntradaInvalida, XanoContratoInvalido, XanoIndisponivel) as erro:
            self.erro = self._mensagem_erro(erro)
        finally:
            self.carregando_cadastros = False

    @rx.event
    def selecionar_aba(self, aba: str):
        if aba in {"", "lojas", "totens", "usuarios"}:
            self.aba = aba
            self._limpar_formulario()
            self.modal = ""
            self.busca = ""
            self.erro = ""
            self.sucesso = ""

    @rx.event
    def editar_loja(self, loja_id: int):
        loja = next((item for item in self.lojas if item["id"] == loja_id), None)
        if loja is None:
            return
        self._limpar_formulario()
        self.edicao_id = loja_id
        self.modal = "loja"
        self.nome_form, self.endereco, self.regiao, self.status = loja["nome"], loja["endereco"], loja["regiao"], loja["status"]

    @rx.event
    def editar_totem(self, totem_id: int):
        totem = next((item for item in self.totens if item["id"] == totem_id), None)
        if totem is None:
            return
        self._limpar_formulario()
        self.edicao_id = totem_id
        self.modal = "totem"
        self.nome_form, self.identificacao, self.loja_form_id = totem["nome"], totem["identificacao"], str(totem["lojas_id"])
        self._atualizar_destinos()

    @rx.event
    def editar_usuario(self, usuario_id: int):
        usuario = next((item for item in self.usuarios if item["id"] == usuario_id), None)
        if usuario is None:
            return
        self._limpar_formulario()
        self.edicao_id = usuario_id
        self.modal = "usuario"
        self.nome_form, self.email_form, self.perfil_usuario = usuario["nome"], usuario["email"], usuario["role"]
        self.loja_form_id = str(usuario["lojas_id"]) if usuario["lojas_id"] else ""
        self._atualizar_destinos()

    @rx.event
    def confirmar_exclusao(self, tipo: str, registro_id: int):
        if tipo in {"loja", "totem", "usuario"}:
            self.exclusao_tipo, self.exclusao_id = tipo, registro_id
            self.erro = self.erro_exclusao = ""

    @rx.var
    def lojas_filtradas(self) -> list[LojaView]:
        termo = self.busca.strip().casefold()
        return [x for x in self.lojas if termo in f'{x["nome"]} {x["regiao"]} {x["endereco"]} {x["status"]}'.casefold()]

    @rx.var
    def totens_filtrados(self) -> list[TotemView]:
        termo = self.busca.strip().casefold()
        return [x for x in self.totens if termo in f'{x["identificacao"]} {x["nome"]} {x["loja_nome"]} {x["status_atual"]}'.casefold()]

    @rx.var
    def usuarios_filtrados(self) -> list[UsuarioView]:
        termo = self.busca.strip().casefold()
        return [x for x in self.usuarios if termo in f'{x["nome"]} {x["email"]} {x["role"]} {x["loja_nome"]}'.casefold()]

    @rx.var
    def lojas_ativas_total(self) -> int:
        return sum(x["status"] in {"Ativa", "Ativo"} for x in self.lojas)

    @rx.var
    def gerentes_total(self) -> int:
        return sum(x["role"] == "gerente" for x in self.usuarios)

    @rx.var
    def administradores_total(self) -> int:
        return sum(x["role"] == "administrador" for x in self.usuarios)

    @rx.var
    def tecnicos_total(self) -> int:
        return sum(x["role"] == "tecnico" for x in self.usuarios)

    @rx.var
    def diretoria_total(self) -> int:
        return sum(x["role"] == "diretoria" for x in self.usuarios)

    @rx.var
    def totens_online_total(self) -> int:
        return sum(x["status_atual"] == "Online" for x in self.totens)

    @rx.var
    def exclusao_nome(self) -> str:
        colecao = {"loja": self.lojas, "totem": self.totens, "usuario": self.usuarios}.get(self.exclusao_tipo, [])
        registro = next((x for x in colecao if x["id"] == self.exclusao_id), None)
        return registro["nome"] if registro else ""

    @rx.event
    def cancelar_exclusao(self):
        self.exclusao_tipo, self.exclusao_id = "", 0
        self.erro_exclusao = ""

    def _pode_operar(self) -> bool:
        return bool(
            self.sessao_confirmada
            and self.role == "administrador"
            and not self.deve_trocar_senha
            and self._auth_token
            and self.usuario_id_contexto == self.usuario_id
            and self._token_contexto_admin == self._auth_token
            and self._versao_contexto_admin == self._versao_sessao
        )

    @rx.event
    async def salvar_loja(self, _: dict[str, Any]):
        if self.processando or not self._pode_operar():
            return
        self.processando = True
        self.erro = self.sucesso = ""
        try:
            cliente = criar_cliente_xano()
            dados = {"nome": self.nome_form, "endereco": self.endereco, "regiao": self.regiao}
            if self.edicao_id:
                await cliente.editar_loja(self._auth_token, self.edicao_id, **dados, status=self.status)
            else:
                await cliente.criar_loja(self._auth_token, **dados)
            await self._atualizar_listas("lojas")
            self._limpar_formulario()
            self.modal = ""
            self.sucesso = "Loja salva com sucesso."
        except XanoNaoAutenticado:
            self._limpar_cadastros()
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            yield rx.redirect("/login")
        except (XanoNaoAutorizado, XanoNaoEncontrado, XanoConflito, XanoEntradaInvalida, XanoContratoInvalido, XanoIndisponivel) as erro:
            self.erro = self._mensagem_erro(erro)
        finally:
            self.processando = False

    @rx.event
    async def salvar_totem(self, _: dict[str, Any]):
        if self.processando or not self._pode_operar():
            return
        self.processando = True
        self.erro = self.sucesso = ""
        try:
            loja_id = int(self.loja_form_id)
            cliente = criar_cliente_xano()
            dados = {"identificacao": self.identificacao, "nome": self.nome_form, "lojas_id": loja_id}
            if self.edicao_id:
                await cliente.editar_totem(self._auth_token, self.edicao_id, **dados)
            else:
                await cliente.criar_totem(self._auth_token, **dados)
            await self._atualizar_listas("totens")
            self._limpar_formulario()
            self.modal = ""
            self.sucesso = "Totem salvo com sucesso."
        except (ValueError, TypeError):
            self.erro = "Selecione uma Loja Ativa."
        except XanoNaoAutenticado:
            self._limpar_cadastros()
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            yield rx.redirect("/login")
        except (XanoNaoAutorizado, XanoNaoEncontrado, XanoConflito, XanoEntradaInvalida, XanoContratoInvalido, XanoIndisponivel) as erro:
            self.erro = self._mensagem_erro(erro)
        finally:
            self.processando = False

    @rx.event
    async def salvar_usuario(self, _: dict[str, Any]):
        if self.processando or not self.edicao_id or not self._pode_operar():
            return
        self.processando = True
        self.erro = self.sucesso = ""
        try:
            loja_id = int(self.loja_form_id) if self.perfil_usuario == "gerente" else None
            await criar_cliente_xano().editar_usuario_administrativo(
                self._auth_token, self.edicao_id, nome=self.nome_form, email=self.email_form,
                role=self.perfil_usuario, lojas_id=loja_id,
            )
            await self._atualizar_listas("usuarios")
            self._limpar_formulario()
            self.modal = ""
            self.sucesso = "Usuário salvo com sucesso."
        except (ValueError, TypeError):
            self.erro = "Gerente exige Loja Ativa."
        except XanoNaoAutenticado:
            self._limpar_cadastros()
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            yield rx.redirect("/login")
        except (XanoNaoAutorizado, XanoNaoEncontrado, XanoConflito, XanoEntradaInvalida, XanoContratoInvalido, XanoIndisponivel) as erro:
            self.erro = self._mensagem_erro(erro)
        finally:
            self.processando = False

    @rx.event
    async def criar_usuario(self, dados: dict[str, Any]):
        if self.processando or self.edicao_id or not self._pode_operar():
            return
        self.erro = self.sucesso = ""
        if self.perfil_usuario not in {"gerente", "tecnico", "diretoria", "administrador"}:
            self.erro = "Selecione um perfil válido."
            return
        senha = str(dados.get("senha_temporaria", ""))
        if len(senha) < 8:
            self.erro = "A senha deve ter pelo menos 8 caracteres."
            return
        if senha != str(dados.get("confirmacao", "")):
            self.erro = "A confirmação de senha não confere."
            return
        try:
            loja_id = int(self.loja_form_id) if self.perfil_usuario == "gerente" else None
        except (ValueError, TypeError):
            self.erro = "Gerente exige Loja Ativa."
            return
        if loja_id is not None and str(loja_id) not in {str(x["id"]) for x in self.lojas_destino}:
            self.erro = "Selecione uma Loja válida."
            return
        self.processando = True
        yield
        try:
            await criar_cliente_xano().criar_usuario_administrativo(
                self._auth_token, nome=self.nome_form, email=self.email_form.strip().lower(),
                role=self.perfil_usuario, lojas_id=loja_id,
                senha_temporaria=senha,
            )
            await self._atualizar_listas("usuarios")
            self._limpar_formulario()
            self.modal = ""
            self.sucesso = "Usuário criado com sucesso."
        except XanoNaoAutenticado:
            self._limpar_cadastros()
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            yield rx.redirect("/login")
        except (XanoNaoAutorizado, XanoNaoEncontrado, XanoConflito, XanoEntradaInvalida, XanoContratoInvalido, XanoIndisponivel) as erro:
            self.erro = self._mensagem_erro(erro)
        finally:
            self.processando = False

    @rx.event
    async def submeter_usuario(self, dados: dict[str, Any]):
        handler = GestaoAdministrativaState.salvar_usuario if self.edicao_id else GestaoAdministrativaState.criar_usuario
        async for evento in handler.fn(self, dados):
            yield evento

    @rx.event
    async def excluir_confirmado(self):
        if self.processando or not self.exclusao_id or not self._pode_operar():
            return
        self.processando = True
        self.erro = self.erro_exclusao = self.sucesso = ""
        try:
            cliente = criar_cliente_xano()
            if self.exclusao_tipo == "loja":
                await cliente.excluir_loja(self._auth_token, self.exclusao_id)
            elif self.exclusao_tipo == "totem":
                await cliente.excluir_totem(self._auth_token, self.exclusao_id)
            elif self.exclusao_tipo == "usuario":
                await cliente.excluir_usuario_administrativo(self._auth_token, self.exclusao_id)
            await self._atualizar_listas({"loja": "lojas", "totem": "totens", "usuario": "usuarios"}[self.exclusao_tipo])
            self._limpar_formulario()
            self.sucesso = "Cadastro excluído com sucesso."
        except XanoNaoAutenticado:
            self._limpar_cadastros()
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            yield rx.redirect("/login")
        except (XanoNaoAutorizado, XanoNaoEncontrado, XanoConflito, XanoEntradaInvalida, XanoContratoInvalido, XanoIndisponivel) as erro:
            mensagem = str(erro)
            self.erro_exclusao = {
                "Totem possui vínculos ou histórico impeditivos.":
                    "Este Totem não pode ser excluído porque possui vínculos ou registros no histórico.",
                "Totem possui transferência histórica.":
                    "Este Totem não pode ser excluído porque já foi transferido entre Lojas.",
            }.get(mensagem, self._mensagem_erro(erro))
        finally:
            self.processando = False

def _seletor_loja() -> rx.Component:
    return rx.vstack(
        rx.el.label("Loja", html_for="gestao-loja"),
        rx.select.root(
            rx.select.trigger(id="gestao-loja", placeholder="Selecione uma Loja", width="100%"),
            rx.select.content(
                rx.foreach(
                    GestaoAdministrativaState.lojas_destino,
                    lambda loja: rx.select.item(
                        loja["nome"], value=loja["id"].to_string()
                    ),
                ),
            ),
            value=GestaoAdministrativaState.loja_form_id,
            on_change=GestaoAdministrativaState.set_loja_form_id,
            name="lojas_id", required=True, width="100%",
        ),
        spacing="2", align="start", width="100%",
    )


def _painel_lista(titulo: str, descricao: str, total: rx.Var, filtrados: rx.Var,
                  placeholder_busca: str, tabela: rx.Component) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.vstack(rx.heading(titulo, size="5", color=TEXTO), rx.text(descricao, size="2", color=TEXTO_SECUNDARIO), spacing="1", align="start"),
                rx.spacer(),
                rx.hstack(
                    rx.icon("list_filter", size=16, color="var(--accent-10)"),
                    rx.text(rx.cond(GestaoAdministrativaState.busca != "",
                                    filtrados.to_string() + " de " + total.to_string() + " registros",
                                    total.to_string() + " registros"),
                            size="2", weight="medium", color="var(--accent-11)"),
                    spacing="2", align="center", padding="0.5rem 0.75rem",
                    background="var(--accent-3)", border="1px solid var(--accent-5)",
                    border_radius="999px",
                ),
                width="100%", align="center", wrap="wrap"),
            rx.input(
                rx.input.slot(rx.icon("search", size=18, color=TEXTO_SECUNDARIO)),
                rx.cond(GestaoAdministrativaState.busca != "",
                    rx.input.slot(
                        rx.icon_button(rx.icon("x", size=16), variant="ghost", color_scheme="gray",
                                       size="1", aria_label="Limpar busca",
                                       on_click=GestaoAdministrativaState.set_busca("")),
                        side="right")),
                placeholder=placeholder_busca, value=GestaoAdministrativaState.busca,
                on_change=GestaoAdministrativaState.set_busca, aria_label="Buscar nesta listagem",
                size="3", width="100%", max_width="28rem", min_height="2.75rem",
                background=SUPERFICIE, border_radius="10px",
            ),
            tabela,
            spacing="5", align="start", width="100%"),
        width="100%", padding="1.5rem", background=SUPERFICIE,
        border=f"1px solid {BORDA}", box_shadow=SOMBRA_BAIXA,
    )


def _acoes_linha(tipo: str, registro_id: rx.Var) -> rx.Component:
    editores = {
        "loja": GestaoAdministrativaState.editar_loja,
        "totem": GestaoAdministrativaState.editar_totem,
        "usuario": GestaoAdministrativaState.editar_usuario,
    }
    return rx.hstack(
        rx.button("Editar", variant="soft", size="2", on_click=editores[tipo](registro_id)),
        rx.button("Excluir", variant="outline", color_scheme="red", size="2",
                  on_click=GestaoAdministrativaState.confirmar_exclusao(tipo, registro_id)),
        spacing="2", wrap="wrap",
    )


def _tabela(cabecalhos: list[str], linhas: rx.Component, vazia: rx.Var, mensagem_vazia: str) -> rx.Component:
    return rx.cond(
        vazia,
        rx.center(rx.vstack(rx.icon("inbox", size=28, color=TEXTO_SECUNDARIO),
                            rx.text(mensagem_vazia, color=TEXTO_SECUNDARIO),
                            spacing="2", align="center"), padding="3rem", width="100%",
                  background=SUPERFICIE_SUAVE, border_radius="12px"),
        rx.box(rx.table.root(
            rx.table.header(rx.table.row(*[rx.table.column_header_cell(x) for x in cabecalhos])),
            rx.table.body(linhas), width="100%", variant="surface",
        ), overflow_x="auto", width="100%"),
    )


def _lista_lojas() -> rx.Component:
    linhas = rx.foreach(GestaoAdministrativaState.lojas_filtradas,
        lambda loja: rx.table.row(
            rx.table.cell(rx.text(loja["nome"], weight="bold")),
            rx.table.cell(loja["regiao"]), rx.table.cell(loja["endereco"]),
            rx.table.cell(rx.badge(rx.text(loja["status"], text_transform="uppercase"),
                                   color_scheme=rx.cond(loja["status"] == "Inativa", "gray", "green"))),
            rx.table.cell(_acoes_linha("loja", loja["id"])),
        ))
    return _painel_lista("Lojas & Unidades", "Unidades cadastradas e sua situação atual.",
        GestaoAdministrativaState.lojas.length(), GestaoAdministrativaState.lojas_filtradas.length(),
        "Buscar por nome, região ou situação",
        _tabela(["Loja", "Região", "Endereço", "Situação", "Ações"], linhas,
                GestaoAdministrativaState.lojas_filtradas.length() == 0, "Nenhuma Loja encontrada."))


def _lista_totens() -> rx.Component:
    linhas = rx.foreach(GestaoAdministrativaState.totens_filtrados,
        lambda totem: rx.table.row(
            rx.table.cell(rx.text(totem["nome"], weight="bold")),
            rx.table.cell(totem["loja_nome"]),
            rx.table.cell(rx.badge(rx.text(totem["status_atual"], text_transform="uppercase"),
                                   color_scheme=rx.cond(totem["status_atual"] == "Online", "green", "gray"))),
            rx.table.cell(_acoes_linha("totem", totem["id"])),
        ))
    return _painel_lista("Ativos & Totens", "Equipamentos e vínculo atual com as Lojas.",
        GestaoAdministrativaState.totens.length(), GestaoAdministrativaState.totens_filtrados.length(),
        "Buscar por Totem, Loja ou situação",
        _tabela(["Totem", "Loja", "Estado", "Ações"], linhas,
                GestaoAdministrativaState.totens_filtrados.length() == 0, "Nenhum Totem encontrado."))


def _lista_usuarios() -> rx.Component:
    linhas = rx.foreach(GestaoAdministrativaState.usuarios_filtrados,
        lambda usuario: rx.table.row(
            rx.table.cell(rx.vstack(rx.text(usuario["nome"], weight="bold"),
                                    rx.text(usuario["email"], size="1", color=TEXTO_SECUNDARIO), spacing="1", align="start")),
            rx.table.cell(rx.badge(rx.text(usuario["role"], text_transform="uppercase"), color_scheme="gray")),
            rx.table.cell(usuario["loja_nome"]),
            rx.table.cell(_acoes_linha("usuario", usuario["id"])),
        ))
    return _painel_lista("Usuários & Acessos", "Pessoas, perfis e vínculos cadastrados.",
        GestaoAdministrativaState.usuarios.length(), GestaoAdministrativaState.usuarios_filtrados.length(),
        "Buscar por nome, e-mail, perfil ou Loja",
        _tabela(["Usuário", "Perfil", "Loja", "Ações"], linhas,
                GestaoAdministrativaState.usuarios_filtrados.length() == 0, "Nenhum usuário encontrado."))


def _campo_modal(rotulo: str, nome: str, valor: rx.Var, evento: Any, *, tipo: str = "text") -> rx.Component:
    return rx.vstack(
        rx.el.label(rotulo, html_for=f"gestao-{nome}"),
        rx.input(id=f"gestao-{nome}", name=nome, value=valor, on_change=evento,
                 type=tipo, auto_complete=False, required=True, width="100%"),
        spacing="2", align="start", width="100%",
    )


def _formulario_loja() -> rx.Component:
    return rx.form(rx.vstack(
        _campo_modal("Nome", "nome-loja", GestaoAdministrativaState.nome_form, GestaoAdministrativaState.set_nome_form),
        _campo_modal("Endereço", "endereco", GestaoAdministrativaState.endereco, GestaoAdministrativaState.set_endereco),
        _campo_modal("Região", "regiao", GestaoAdministrativaState.regiao, GestaoAdministrativaState.set_regiao),
        rx.cond(GestaoAdministrativaState.edicao_id > 0,
            rx.vstack(rx.el.label("Situação", html_for="gestao-status"),
                rx.select.root(
                    rx.select.trigger(id="gestao-status", width="100%"),
                    rx.select.content(
                        rx.select.item("ATIVA", value="Ativa"),
                        rx.select.item("INATIVA", value="Inativa"),
                    ),
                    name="status", value=GestaoAdministrativaState.status,
                    on_change=GestaoAdministrativaState.set_status, width="100%"),
                align="start", width="100%")),
        _acoes_modal("Loja"), width="100%", align="start", spacing="4"),
        on_submit=GestaoAdministrativaState.salvar_loja, width="100%")


def _formulario_totem() -> rx.Component:
    return rx.form(rx.vstack(
        _campo_modal("Identificação", "identificacao", GestaoAdministrativaState.identificacao, GestaoAdministrativaState.set_identificacao),
        _campo_modal("Nome", "nome-totem", GestaoAdministrativaState.nome_form, GestaoAdministrativaState.set_nome_form),
        _seletor_loja(), _acoes_modal("Totem"),
        width="100%", align="start", spacing="4"),
        on_submit=GestaoAdministrativaState.salvar_totem, width="100%")


def _formulario_usuario() -> rx.Component:
    return rx.form(rx.vstack(
        _campo_modal("Nome", "nome-usuario", GestaoAdministrativaState.nome_form, GestaoAdministrativaState.set_nome_form),
        _campo_modal("E-mail", "email-usuario", GestaoAdministrativaState.email_form, GestaoAdministrativaState.set_email_form, tipo="email"),
        rx.vstack(rx.el.label("Perfil", html_for="gestao-perfil"),
                  rx.select.root(
                      rx.select.trigger(id="gestao-perfil", width="100%"),
                      rx.select.content(
                          rx.select.item("GERENTE", value="gerente"),
                          rx.select.item("TÉCNICO", value="tecnico"),
                          rx.select.item("DIRETORIA", value="diretoria"),
                          rx.select.item("ADMINISTRADOR", value="administrador"),
                      ),
                      name="role", value=GestaoAdministrativaState.perfil_usuario,
                      on_change=GestaoAdministrativaState.set_perfil_usuario, width="100%"),
                  align="start", width="100%"),
        rx.cond(GestaoAdministrativaState.perfil_usuario == "gerente", _seletor_loja()),
        rx.cond(GestaoAdministrativaState.edicao_id == 0,
            rx.vstack(
                rx.vstack(rx.el.label("Senha temporária", html_for="gestao-senha-temporaria"),
                          rx.input(id="gestao-senha-temporaria", name="senha_temporaria", type="password",
                                   min_length=8, auto_complete=False, required=True, width="100%"), align="start", width="100%"),
                rx.vstack(rx.el.label("Confirmar senha temporária", html_for="gestao-confirmacao-senha"),
                          rx.input(id="gestao-confirmacao-senha", name="confirmacao", type="password",
                                   min_length=8, auto_complete=False, required=True, width="100%"), align="start", width="100%"),
                width="100%", spacing="4")),
        _acoes_modal("usuário"), width="100%", align="start", spacing="4"),
        on_submit=GestaoAdministrativaState.submeter_usuario, width="100%")


def _acoes_modal(tipo: str) -> rx.Component:
    return rx.hstack(
        rx.button("Cancelar", type="button", variant="soft", on_click=GestaoAdministrativaState.fechar_modal,
                  disabled=GestaoAdministrativaState.processando),
        rx.button(rx.cond(GestaoAdministrativaState.processando, "Salvando...", "Salvar " + tipo),
                  type="submit", disabled=GestaoAdministrativaState.processando),
        justify="end", width="100%", spacing="2")


def _modal_cadastro() -> rx.Component:
    titulo = rx.cond(GestaoAdministrativaState.modal == "usuario",
        rx.cond(GestaoAdministrativaState.edicao_id > 0, "Editar usuário", "Criar usuário"),
        rx.cond(GestaoAdministrativaState.modal == "loja",
            rx.cond(GestaoAdministrativaState.edicao_id > 0, "Editar Loja", "Criar Loja"),
            rx.cond(GestaoAdministrativaState.edicao_id > 0, "Editar Totem", "Criar Totem")))
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.dialog.title(titulo),
                rx.dialog.description("Preencha os campos obrigatórios para continuar."),
                rx.cond(GestaoAdministrativaState.erro != "",
                        rx.callout(GestaoAdministrativaState.erro, color_scheme="red", width="100%")),
                rx.cond(GestaoAdministrativaState.modal == "loja", _formulario_loja(),
                        rx.cond(GestaoAdministrativaState.modal == "totem", _formulario_totem(), _formulario_usuario())),
                align="start", width="100%", spacing="4"),
            max_width="34rem", width="calc(100vw - 2rem)"),
        open=GestaoAdministrativaState.modal != "", on_open_change=GestaoAdministrativaState.definir_modal_aberto,
    )


def _confirmacao_exclusao() -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.content(
            rx.alert_dialog.title("Excluir cadastro?"),
            rx.alert_dialog.description("Confirme a exclusão de “" + GestaoAdministrativaState.exclusao_nome + "”. Esta ação não pode ser desfeita."),
            rx.cond(GestaoAdministrativaState.erro_exclusao != "",
                    rx.callout(GestaoAdministrativaState.erro_exclusao, color_scheme="red", width="100%")),
            rx.hstack(
                rx.button("Cancelar", variant="soft", on_click=GestaoAdministrativaState.cancelar_exclusao),
                rx.button("Confirmar exclusão", color_scheme="red", disabled=GestaoAdministrativaState.processando,
                          on_click=GestaoAdministrativaState.excluir_confirmado),
                justify="end", width="100%", margin_top="1rem"),
        ), open=GestaoAdministrativaState.exclusao_id > 0)


def _card_modulo(titulo: str, subtitulo: str, icone: str, total: rx.Var,
                  indicadores: list[tuple[str, rx.Var]], detalhe: str, tipo: str, aba: str) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(rx.center(rx.icon(icone, size=23, color="var(--accent-9)"),
                                width="3rem", height="3rem", border_radius="12px", background="var(--accent-3)"),
                      rx.vstack(rx.heading(titulo, size="4", color=TEXTO),
                                rx.text(subtitulo, size="2", color=TEXTO_SECUNDARIO), spacing="1", align="start"),
                      width="100%", spacing="3", align="center"),
            rx.text(detalhe, size="2", color=TEXTO_SECUNDARIO, min_height="3.25rem"),
            rx.box(rx.vstack(
                rx.hstack(rx.text("Registros cadastrados", size="2", color=TEXTO_SECUNDARIO),
                          rx.spacer(), rx.text(total, size="5", weight="bold", color=TEXTO), width="100%"),
                rx.separator(size="4"),
                rx.grid(*[
                    rx.vstack(rx.text(rotulo.capitalize(), size="1", weight="bold", color=TEXTO_SECUNDARIO, line_height="1.5"),
                              rx.text(valor, size="4", weight="bold", color=TEXTO),
                              spacing="1", align="start", min_width="0")
                    for rotulo, valor in indicadores
                ], columns="2" if len(indicadores) > 1 else "1", gap="0.75rem", width="100%"),
                spacing="3", width="100%"), background=SUPERFICIE_SUAVE,
                padding="1rem", border_radius="10px", width="100%"),
            rx.spacer(),
            rx.vstack(
                rx.button("Criar " + tipo, on_click=GestaoAdministrativaState.abrir_modal({"lojas": "loja", "totens": "totem", "usuarios": "usuario"}[aba]),
                          width="100%"),
                rx.button("Ver listagem", variant="soft", on_click=GestaoAdministrativaState.selecionar_aba(aba),
                          width="100%"),
                spacing="2", width="100%"),
            align="start", spacing="4", width="100%", height="100%"),
        width="100%", min_height="25rem", background=SUPERFICIE,
        border=f"1px solid {BORDA}", box_shadow=SOMBRA_BAIXA, padding="1.5rem",
    )


def gestao_administrativa() -> rx.Component:
    conteudo = rx.vstack(
        rx.vstack(rx.heading("Gestão do sistema", size="7", color=TEXTO),
                  rx.text("Cadastros, unidades e equipamentos da operação MIRA.", size="2", color=TEXTO_SECUNDARIO, line_height="1.7"),
                  spacing="2", align="start", width="100%"),
        rx.cond(GestaoAdministrativaState.sucesso != "",
                rx.callout(GestaoAdministrativaState.sucesso, color_scheme="green", width="100%")),
        rx.cond((GestaoAdministrativaState.erro != "") & (GestaoAdministrativaState.modal == ""),
                rx.callout(GestaoAdministrativaState.erro, color_scheme="red", width="100%")),
        rx.cond(GestaoAdministrativaState.carregando_cadastros,
                rx.center(rx.spinner(size="3"), rx.text("Carregando cadastros..."), width="100%", padding="3rem"),
                rx.vstack(
                    rx.grid(
                        _card_modulo("Usuários & Acessos", "Pessoas e permissões", "users",
                                     GestaoAdministrativaState.usuarios.length(),
                                     [("ADMINISTRADORES", GestaoAdministrativaState.administradores_total),
                                      ("GERENTES", GestaoAdministrativaState.gerentes_total),
                                      ("TÉCNICOS", GestaoAdministrativaState.tecnicos_total),
                                      ("DIRETORIA", GestaoAdministrativaState.diretoria_total)],
                                     "Gerencie contas, perfis e vínculos de Gerentes com Lojas.", "Usuário", "usuarios"),
                        _card_modulo("Lojas & Unidades", "Estrutura da rede", "store",
                                     GestaoAdministrativaState.lojas.length(),
                                     [("LOJAS ATIVAS", GestaoAdministrativaState.lojas_ativas_total)],
                                     "Consulte unidades, situação cadastral e localização.", "Loja", "lojas"),
                        _card_modulo("Ativos & Totens", "Equipamentos", "monitor",
                                     GestaoAdministrativaState.totens.length(),
                                     [("TOTENS ONLINE", GestaoAdministrativaState.totens_online_total)],
                                     "Acompanhe identificação, vínculo atual e situação dos equipamentos.", "Totem", "totens"),
                        columns={"initial": "1", "md": "3"}, gap="1.5rem", width="100%", align="stretch"),
                    rx.cond(GestaoAdministrativaState.aba != "",
                        rx.vstack(rx.hstack(rx.heading("Listagem", size="5"), rx.spacer(),
                                           rx.button("Fechar listagem", variant="ghost", on_click=GestaoAdministrativaState.selecionar_aba("")),
                                           width="100%"),
                                  rx.cond(GestaoAdministrativaState.aba == "usuarios", _lista_usuarios(),
                                          rx.cond(GestaoAdministrativaState.aba == "lojas", _lista_lojas(), _lista_totens())),
                                  spacing="3", width="100%", align="start")),
                    width="100%", spacing="6")),
        _modal_cadastro(), _confirmacao_exclusao(),
        width="100%", align="start", spacing="6",
    )
    return rx.cond(
        AuthState.carregando, estado_carregamento(),
        rx.cond(AuthState.sessao_confirmada & (AuthState.role == "administrador"),
                casca_conteudo(conteudo, "/inicio"),
                estado_revalidacao(GestaoAdministrativaState.carregar)),
    )
