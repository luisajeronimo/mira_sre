"""Regressão do catálogo mínimo de Lojas na criação administrativa."""

from __future__ import annotations

import asyncio
from importlib import import_module

import pytest

import app.states.auth as auth_module
from app.pages.administracao import AdministracaoState, administracao
from app.services.xano import (
    IdentidadeXano,
    LojaOpcaoAdministracaoXano,
    XanoEntradaInvalida,
    XanoIndisponivel,
)
from app.states.auth import AuthState, MENSAGEM_INDISPONIVEL

administracao_module = import_module("app.pages.administracao")


ADMIN_CONCLUIDO = IdentidadeXano(
    id=12,
    nome="Administradora de teste",
    email="admin@example.test",
    role="administrador",
    lojas_id=None,
    deve_trocar_senha=False,
)


class ClienteAdminFalso:
    def __init__(
        self, *, identidade=ADMIN_CONCLUIDO, erro_lojas=None, erro_criacao=None
    ):
        self.identidade = identidade
        self.erro_lojas = erro_lojas
        self.erro_criacao = erro_criacao
        self.chamadas_me = []
        self.chamadas_lojas = []
        self.criacoes = []

    async def obter_identidade(self, token):
        self.chamadas_me.append(token)
        return self.identidade

    async def listar_lojas_administracao(self, token):
        self.chamadas_lojas.append(token)
        if self.erro_lojas:
            raise self.erro_lojas
        return (LojaOpcaoAdministracaoXano(id=1, nome="Loja Paulista"),)

    async def criar_usuario_administrativo(self, token, **dados):
        if self.erro_criacao:
            raise self.erro_criacao
        self.criacoes.append((token, dados))


def coletar(gerador):
    async def _coletar():
        return [evento async for evento in gerador]

    return asyncio.run(_coletar())


def executar_evento(handler, estado, *args):
    resultado = handler.fn(estado, *args)
    if hasattr(resultado, "__aiter__"):
        return coletar(resultado)
    return []


def novo_estado():
    raiz = AuthState(_reflex_internal_init=True)
    estado = AdministracaoState(parent_state=raiz, _reflex_internal_init=True)
    raiz._auth_token = "token-local-de-teste"
    return estado


def redirecionamento(evento):
    return evento.args[0][1]._var_value


def instalar_cliente(monkeypatch, cliente):
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente)
    monkeypatch.setattr(administracao_module, "criar_cliente_xano", lambda: cliente)


def percorrer_componentes(componente):
    vistos = set()
    pendentes = [componente]
    while pendentes:
        atual = pendentes.pop()
        if id(atual) in vistos:
            continue
        vistos.add(id(atual))
        yield atual
        pendentes.extend(
            filho
            for filho in getattr(atual, "children", [])
            if hasattr(filho, "children")
        )


def test_entrada_na_administracao_revalida_e_carrega_opcoes_uma_vez(monkeypatch):
    cliente = ClienteAdminFalso()
    instalar_cliente(monkeypatch, cliente)
    estado = novo_estado()

    executar_evento(AdministracaoState.carregar_administracao, estado)
    executar_evento(AdministracaoState.carregar_administracao, estado)

    assert cliente.chamadas_me == ["token-local-de-teste"] * 2
    assert cliente.chamadas_lojas == ["token-local-de-teste"]
    assert cliente.criacoes == []
    assert estado.opcoes_lojas == [{"id": 1, "nome": "Loja Paulista"}]
    assert estado.opcoes_lojas_carregadas is True


def test_administrador_pendente_revalida_sem_carregar_catalogo(monkeypatch):
    identidade = IdentidadeXano(
        id=12,
        nome="Administradora de teste",
        email="admin@example.test",
        role="administrador",
        lojas_id=None,
        deve_trocar_senha=True,
    )
    cliente = ClienteAdminFalso(identidade=identidade)
    instalar_cliente(monkeypatch, cliente)
    estado = novo_estado()

    eventos = executar_evento(AdministracaoState.carregar_administracao, estado)

    assert redirecionamento(eventos[-1]) == "/primeiro-acesso"
    assert cliente.chamadas_lojas == []
    assert estado.sessao_confirmada is True


def test_erro_de_carregamento_e_sanitizado_e_permanece_tentavel(monkeypatch):
    cliente = ClienteAdminFalso(erro_lojas=XanoIndisponivel("detalhe interno"))
    instalar_cliente(monkeypatch, cliente)
    estado = novo_estado()

    executar_evento(AdministracaoState.carregar_administracao, estado)

    assert estado.erro_lojas == MENSAGEM_INDISPONIVEL
    assert "detalhe interno" not in estado.erro_lojas
    assert estado.opcoes_lojas_carregadas is False
    assert estado.sessao_confirmada is True


def test_select_usa_nome_como_rotulo_id_como_valor_e_so_aparece_condicionalmente():
    componentes = list(percorrer_componentes(administracao()))
    selects = [
        item
        for item in componentes
        if type(item).__name__ == "SelectRoot"
        and getattr(getattr(item, "name", None), "_var_value", None)
        == "lojas_id"
    ]
    assert len(selects) == 1
    seletor = selects[0]
    assert seletor.required._var_value is True

    condicao_perfil_gerente = [
        item
        for item in componentes
        if type(item).__name__ == "Cond"
        and "perfil_selecionado" in item.cond._js_expr
        and '"gerente"' in item.cond._js_expr
    ]
    assert len(condicao_perfil_gerente) == 1

    item_loja = [
        item
        for item in componentes
        if type(item).__name__ == "SelectItem"
        and '"id"' in item.value._js_expr
    ]
    assert len(item_loja) == 1
    assert '"nome"' in item_loja[0].children[0].contents._js_expr
    assert not any(
        type(item).__name__ == "TextFieldRoot"
        and getattr(getattr(item, "name", None), "_var_value", None)
        == "lojas_id"
        for item in componentes
    )


def test_gerente_sem_selecao_nao_submete(monkeypatch):
    cliente = ClienteAdminFalso()
    instalar_cliente(monkeypatch, cliente)
    estado = novo_estado()
    estado.opcoes_lojas = [{"id": 1, "nome": "Loja Paulista"}]
    executar_evento(AdministracaoState.selecionar_perfil, estado, "gerente")

    executar_evento(
        AdministracaoState.criar_usuario,
        estado,
        {
            "nome": "Gerente de teste",
            "email": "gerente@example.test",
            "role": "gerente",
            "senha_temporaria": "senha-ficticia",
            "confirmacao": "senha-ficticia",
        },
    )

    assert cliente.criacoes == []
    assert estado.mensagem_usuario == "Gerente exige Loja."


def test_rejeicao_backend_de_criacao_e_exibida_com_mensagem_sanitizada(monkeypatch):
    cliente = ClienteAdminFalso(erro_criacao=XanoEntradaInvalida("detalhe interno"))
    instalar_cliente(monkeypatch, cliente)
    estado = novo_estado()

    executar_evento(
        AdministracaoState.criar_usuario,
        estado,
        {
            "nome": "Técnico de teste",
            "email": "tecnico@example.test",
            "role": "tecnico",
            "senha_temporaria": "senha-ficticia",
            "confirmacao": "senha-ficticia",
        },
    )

    assert estado.mensagem_usuario == (
        "Não foi possível criar o usuário. Verifique os dados informados."
    )
    assert "detalhe interno" not in estado.mensagem_usuario
    assert estado.sucesso_usuario == ""


def test_contrato_invalido_na_criacao_mostra_erro_sanitizado(monkeypatch):
    cliente = ClienteAdminFalso(erro_criacao=administracao_module.XanoContratoInvalido("detalhe interno"))
    instalar_cliente(monkeypatch, cliente)
    estado = novo_estado()

    executar_evento(
        AdministracaoState.criar_usuario,
        estado,
        {
            "nome": "Técnico de teste",
            "email": "tecnico@example.test",
            "role": "tecnico",
            "senha_temporaria": "senha-ficticia",
            "confirmacao": "senha-ficticia",
        },
    )

    assert estado.mensagem_usuario == (
        "Não foi possível confirmar a criação do usuário."
    )
    assert "detalhe interno" not in estado.mensagem_usuario


@pytest.mark.parametrize(
    ("role", "senha", "confirmacao", "mensagem"),
    [
        ("admin", "senha-ficticia", "senha-ficticia", "Selecione um perfil válido."),
        ("tecnico", "curta", "curta", "A senha deve ter pelo menos 8 caracteres."),
        ("tecnico", "senha-ficticia", "outra-ficticia", "A confirmação de senha não confere."),
    ],
)
def test_formulario_rejeita_perfil_e_senha_invalidos_localmente(
    monkeypatch, role, senha, confirmacao, mensagem
):
    cliente = ClienteAdminFalso()
    instalar_cliente(monkeypatch, cliente)
    estado = novo_estado()

    executar_evento(
        AdministracaoState.criar_usuario,
        estado,
        {
            "nome": "Usuário de teste",
            "email": "teste@example.test",
            "role": role,
            "senha_temporaria": senha,
            "confirmacao": confirmacao,
        },
    )

    assert cliente.criacoes == []
    assert estado.mensagem_usuario == mensagem


def test_state_de_administracao_nao_persiste_campos_de_senha():
    campos_sensiveis = {
        "senha",
        "password",
        "senha_temporaria",
        "nova_senha",
        "confirmacao",
    }

    assert campos_sensiveis.isdisjoint(AdministracaoState.base_vars)


def test_gerente_envia_id_selecionado_e_rejeita_id_fora_das_opcoes(monkeypatch):
    cliente = ClienteAdminFalso()
    instalar_cliente(monkeypatch, cliente)
    estado = novo_estado()
    estado.opcoes_lojas = [{"id": 1, "nome": "Loja Paulista"}]
    executar_evento(AdministracaoState.selecionar_perfil, estado, "gerente")
    executar_evento(AdministracaoState.selecionar_loja, estado, "1")

    executar_evento(
        AdministracaoState.criar_usuario,
        estado,
        {
            "nome": "Gerente de teste",
            "email": "gerente@example.test",
            "role": "gerente",
            "senha_temporaria": "senha-ficticia",
            "confirmacao": "senha-ficticia",
            "lojas_id": "1",
        },
    )

    assert cliente.criacoes[0][1]["lojas_id"] == 1

    cliente.criacoes.clear()
    estado.mensagem_usuario = ""
    executar_evento(
        AdministracaoState.criar_usuario,
        estado,
        {
            "nome": "Gerente de teste",
            "email": "gerente2@example.test",
            "role": "gerente",
            "senha_temporaria": "senha-ficticia",
            "confirmacao": "senha-ficticia",
            "lojas_id": "999",
        },
    )
    assert cliente.criacoes == []
    assert estado.mensagem_usuario == "Selecione uma Loja válida."


@pytest.mark.parametrize("perfil", ["tecnico", "diretoria", "administrador"])
def test_perfis_globais_nao_exibem_ou_enviam_loja_e_limpam_selecao(
    monkeypatch, perfil
):
    cliente = ClienteAdminFalso()
    instalar_cliente(monkeypatch, cliente)
    estado = novo_estado()
    estado.opcoes_lojas = [{"id": 1, "nome": "Loja Paulista"}]
    executar_evento(AdministracaoState.selecionar_perfil, estado, "gerente")
    executar_evento(AdministracaoState.selecionar_loja, estado, "1")
    executar_evento(AdministracaoState.selecionar_perfil, estado, perfil)

    assert estado.loja_selecionada == ""
    executar_evento(
        AdministracaoState.criar_usuario,
        estado,
        {
            "nome": "Usuário de teste",
            "email": f"{perfil}@example.test",
            "role": perfil,
            "senha_temporaria": "senha-ficticia",
            "confirmacao": "senha-ficticia",
            "lojas_id": "1",  # valor residual não pode ir ao cliente
        },
    )

    assert len(cliente.criacoes) == 1
    assert cliente.criacoes[0][1]["lojas_id"] is None
