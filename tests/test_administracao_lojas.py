"""Regressões da criação de usuários no modal da gestão administrativa."""

from __future__ import annotations

import asyncio
from importlib import import_module

import pytest

from app.pages.administracao import primeiro_acesso
from app.pages.gestao_administrativa import GestaoAdministrativaState, gestao_administrativa
from app.services.xano import XanoEntradaInvalida
from app.states.auth import AuthState

modulo = import_module("app.pages.gestao_administrativa")


def coletar(gerador):
    async def interno():
        return [evento async for evento in gerador]
    return asyncio.run(interno())


def estado_admin():
    raiz = AuthState(_reflex_internal_init=True)
    estado = GestaoAdministrativaState(parent_state=raiz, _reflex_internal_init=True)
    raiz._auth_token = "token-ficticio"
    raiz.usuario_id = 12
    raiz.role = "administrador"
    raiz.sessao_confirmada = True
    estado.usuario_id_contexto = raiz.usuario_id
    estado._token_contexto_admin = raiz._auth_token
    estado._versao_contexto_admin = raiz._versao_sessao
    estado.lojas = [
        {"id": 1, "nome": "Ativa", "endereco": "Rua A", "regiao": "Sul", "status": "Ativa"},
        {"id": 2, "nome": "Inativa", "endereco": "Rua B", "regiao": "Sul", "status": "Inativa"},
    ]
    estado._atualizar_destinos()
    estado.nome_form = "Pessoa"
    estado.email_form = "PESSOA@example.test"
    return estado


class ClienteFalso:
    def __init__(self, erro=None):
        self.criacoes = []
        self.erro = erro

    async def criar_usuario_administrativo(self, token, **dados):
        if self.erro:
            raise self.erro
        self.criacoes.append((token, dados))

    async def listar_usuarios_administracao(self, token):
        return ()


def criar(estado, cliente, monkeypatch, **dados):
    monkeypatch.setattr(modulo, "criar_cliente_xano", lambda: cliente)
    return coletar(GestaoAdministrativaState.criar_usuario.fn(estado, {
        "senha_temporaria": "senha-ficticia", "confirmacao": "senha-ficticia", **dados,
    }))


def percorrer(componente):
    vistos = set()
    pendentes = [componente]
    while pendentes:
        atual = pendentes.pop()
        if id(atual) in vistos:
            continue
        vistos.add(id(atual))
        yield atual
        pendentes.extend(x for x in getattr(atual, "children", []) if hasattr(x, "children"))


def test_campos_do_modal_e_primeiro_acesso_tem_rotulos_persistentes():
    for pagina, ids in [
        (gestao_administrativa, {"gestao-nome-usuario", "gestao-email-usuario", "gestao-senha-temporaria", "gestao-confirmacao-senha"}),
        (primeiro_acesso, {"nova-senha", "confirmacao-nova-senha"}),
    ]:
        componentes = list(percorrer(pagina()))
        controles = {x.id for x in componentes if getattr(x, "id", None)}
        rotulos = {str(x.html_for).strip('"') for x in componentes if x.__class__.__name__ == "Label"}
        assert ids <= controles
        assert ids <= rotulos


def test_modal_abre_cancela_e_nao_envia_mutacao(monkeypatch):
    estado = estado_admin()
    cliente = ClienteFalso()
    monkeypatch.setattr(modulo, "criar_cliente_xano", lambda: cliente)
    GestaoAdministrativaState.abrir_modal.fn(estado, "usuario")
    assert estado.modal == "usuario"
    GestaoAdministrativaState.fechar_modal.fn(estado)
    assert estado.modal == ""
    assert cliente.criacoes == []


def test_gerente_exige_loja_ativa_e_rejeita_id_forged(monkeypatch):
    estado = estado_admin()
    estado.perfil_usuario = "gerente"
    cliente = ClienteFalso()
    criar(estado, cliente, monkeypatch)
    assert estado.erro == "Gerente exige Loja Ativa."
    estado.loja_form_id = "2"
    criar(estado, cliente, monkeypatch)
    assert estado.erro == "Selecione uma Loja válida."
    estado.loja_form_id = "999"
    criar(estado, cliente, monkeypatch)
    assert estado.erro == "Selecione uma Loja válida."
    assert cliente.criacoes == []


def test_criacao_de_gerente_atualiza_lista_e_fecha_modal(monkeypatch):
    estado = estado_admin()
    estado.perfil_usuario = "gerente"
    estado.loja_form_id = "1"
    estado.modal = "usuario"
    cliente = ClienteFalso()
    criar(estado, cliente, monkeypatch)
    assert cliente.criacoes == [("token-ficticio", {
        "nome": "Pessoa", "email": "pessoa@example.test", "role": "gerente",
        "lojas_id": 1, "senha_temporaria": "senha-ficticia",
    })]
    assert estado.modal == ""
    assert estado.sucesso == "Usuário criado com sucesso."


@pytest.mark.parametrize("perfil", ["tecnico", "diretoria", "administrador"])
def test_perfil_global_nao_envia_loja_residual(monkeypatch, perfil):
    estado = estado_admin()
    estado.perfil_usuario = perfil
    estado.loja_form_id = "1"
    cliente = ClienteFalso()
    criar(estado, cliente, monkeypatch)
    assert cliente.criacoes[0][1]["lojas_id"] is None


@pytest.mark.parametrize("perfil,senha,confirmacao,mensagem", [
    ("admin", "senha-ficticia", "senha-ficticia", "Selecione um perfil válido."),
    ("tecnico", "curta", "curta", "A senha deve ter pelo menos 8 caracteres."),
    ("tecnico", "senha-ficticia", "outra-ficticia", "A confirmação de senha não confere."),
])
def test_formulario_rejeita_perfil_e_senha_invalidos(monkeypatch, perfil, senha, confirmacao, mensagem):
    estado = estado_admin()
    estado.perfil_usuario = perfil
    cliente = ClienteFalso()
    criar(estado, cliente, monkeypatch, senha_temporaria=senha, confirmacao=confirmacao)
    assert estado.erro == mensagem
    assert cliente.criacoes == []


def test_erro_funcional_nao_confirma_criacao(monkeypatch):
    estado = estado_admin()
    estado.perfil_usuario = "tecnico"
    cliente = ClienteFalso(XanoEntradaInvalida("E-mail já cadastrado."))
    criar(estado, cliente, monkeypatch)
    assert estado.erro == "E-mail já cadastrado."
    assert estado.sucesso == ""
    assert estado.modal == ""


def test_senha_nao_e_var_persistida_no_state():
    assert {"senha", "senha_temporaria", "confirmacao"}.isdisjoint(GestaoAdministrativaState.base_vars)


def test_evento_de_criacao_nao_envia_dados_sem_permissao(monkeypatch):
    estado = estado_admin()
    estado.perfil_usuario = "tecnico"
    cliente = ClienteFalso()
    monkeypatch.setattr(modulo, "criar_cliente_xano", lambda: cliente)
    estado.parent_state.role = "gerente"
    coletar(GestaoAdministrativaState.criar_usuario.fn(estado, {
        "senha_temporaria": "senha-ficticia", "confirmacao": "senha-ficticia",
    }))
    assert cliente.criacoes == []


def test_evento_de_criacao_nao_envia_dados_apos_expiracao(monkeypatch):
    estado = estado_admin()
    estado.perfil_usuario = "tecnico"
    cliente = ClienteFalso()
    monkeypatch.setattr(modulo, "criar_cliente_xano", lambda: cliente)
    estado.parent_state._auth_token = ""
    coletar(GestaoAdministrativaState.criar_usuario.fn(estado, {
        "senha_temporaria": "senha-ficticia", "confirmacao": "senha-ficticia",
    }))
    assert cliente.criacoes == []


def test_evento_de_criacao_nao_usa_formulario_de_sessao_anterior(monkeypatch):
    estado = estado_admin()
    estado.perfil_usuario = "tecnico"
    cliente = ClienteFalso()
    monkeypatch.setattr(modulo, "criar_cliente_xano", lambda: cliente)
    estado.parent_state._auth_token = "token-de-outra-pessoa"
    estado.parent_state.usuario_id = 33
    coletar(GestaoAdministrativaState.criar_usuario.fn(estado, {
        "senha_temporaria": "senha-ficticia", "confirmacao": "senha-ficticia",
    }))
    assert cliente.criacoes == []
