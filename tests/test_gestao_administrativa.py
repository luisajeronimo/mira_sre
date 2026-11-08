"""Fluxos locais da gestão: contratos HTTP e estado Reflex com dados fictícios."""

from __future__ import annotations

import asyncio
import inspect
import json
from importlib import import_module

import httpx
import pytest

from app.pages.gestao_administrativa import GestaoAdministrativaState, gestao_administrativa
from app.services.xano import (
    IdentidadeXano, LojaAdministrativaXano, TotemAdministrativoXano, UsuarioCadastroXano,
    XanoCliente, XanoContratoInvalido, XanoEntradaInvalida,
)
from app.states.auth import AuthState
import app.states.auth as auth_module


BASE = "https://xano.example/api:mira-auth"
modulo_gestao = import_module("app.pages.gestao_administrativa")


def executar(corrotina):
    return asyncio.run(corrotina)


def coletar(gerador):
    async def interno():
        return [item async for item in gerador]
    return executar(interno())


def criar_cliente_falso_http(respostas):
    requisicoes = []

    def responder(requisicao: httpx.Request):
        requisicoes.append(requisicao)
        chave = (requisicao.method, requisicao.url.path.removeprefix("/api:mira-auth"))
        status, payload = respostas[chave]
        return httpx.Response(status, json=payload)

    return XanoCliente(BASE, transport=httpx.MockTransport(responder)), requisicoes


def test_crud_de_lojas_usa_contratos_especificos_e_situacao_do_backend():
    loja = {"id": 7, "nome": "Centro", "endereco": "Rua A", "regiao": "Sul", "status": "Ativa"}
    cliente, requisicoes = criar_cliente_falso_http({
        ("POST", "/administracao/lojas/registros"): (200, loja),
        ("GET", "/administracao/lojas/registros"): (200, {"items": [loja]}),
        ("PATCH", "/administracao/lojas/7"): (200, {**loja, "status": "Inativa"}),
        ("DELETE", "/administracao/lojas/7"): (200, {"success": True}),
    })
    assert executar(cliente.criar_loja("token", nome="Centro", endereco="Rua A", regiao="Sul")).status == "Ativa"
    assert executar(cliente.listar_registros_lojas("token"))[0].id == 7
    assert executar(cliente.editar_loja("token", 7, nome="Centro", endereco="Rua A", regiao="Sul", status="Inativa")).status == "Inativa"
    executar(cliente.excluir_loja("token", 7))
    assert all(req.headers["Authorization"] == "Bearer token" for req in requisicoes)
    assert "status" not in json.loads(requisicoes[0].content)


def test_totem_sem_telemetria_e_usuario_sem_credencial_sao_aceitos():
    cliente, _ = criar_cliente_falso_http({
        ("GET", "/administracao/totens"): (200, {"items": [
            {"id": 3, "identificacao": "T-03", "nome": "Totem 03", "lojas_id": 7, "status_atual": None}
        ]}),
        ("GET", "/administracao/usuarios"): (200, {"items": [
            {"id": 9, "nome": "Gerente", "email": "g@example.test", "role": "gerente", "lojas_id": 7}
        ]}),
    })
    totem = executar(cliente.listar_totens_administracao("token"))[0]
    usuario = executar(cliente.listar_usuarios_administracao("token"))[0]
    assert totem.status_atual is None
    assert not hasattr(usuario, "senha")
    assert not hasattr(usuario, "token")


def test_listas_administrativas_leem_valores_legados_sem_mudar_destinos():
    cliente, _ = criar_cliente_falso_http({
        ("GET", "/administracao/lojas/registros"): (200, {"items": [
            {"id": 1, "nome": "Legada", "endereco": "Rua A", "regiao": "Sul", "status": "Ativo"}
        ]}),
        ("GET", "/administracao/usuarios"): (200, {"items": [
            {"id": 10, "nome": "Diretoria", "email": "d@example.test", "role": "diretoria", "lojas_id": 0}
        ]}),
    })
    loja = executar(cliente.listar_registros_lojas("token"))[0]
    usuario = executar(cliente.listar_usuarios_administracao("token"))[0]
    assert loja.status == "Ativo"
    assert usuario.lojas_id is None


def test_cliente_recusa_material_de_credencial_em_resposta_administrativa():
    cliente, _ = criar_cliente_falso_http({
        ("GET", "/administracao/usuarios"): (200, {"items": [
            {"id": 9, "nome": "Pessoa", "email": "p@example.test", "role": "tecnico",
             "lojas_id": None, "senha": "valor-que-nao-deve-aparecer"}
        ]}),
    })
    with pytest.raises(XanoContratoInvalido):
        executar(cliente.listar_usuarios_administracao("token"))


def test_exclusao_bloqueada_por_dependencia_retorna_erro_funcional():
    cliente, _ = criar_cliente_falso_http({
        ("DELETE", "/administracao/totens/3"): (400, {"message": "dependência interna"}),
    })
    with pytest.raises(XanoEntradaInvalida, match="dados informados"):
        executar(cliente.excluir_totem("token", 3))


def test_erro_aprovado_do_ultimo_administrador_e_exibido_sem_texto_interno():
    cliente, _ = criar_cliente_falso_http({
        ("PATCH", "/administracao/usuarios/8"): (
            400, {"message": "O último Administrador deve permanecer."}
        ),
    })
    with pytest.raises(XanoEntradaInvalida, match="último Administrador"):
        executar(cliente.editar_usuario_administrativo(
            "token", 8, nome="Pessoa", email="p@example.test",
            role="tecnico", lojas_id=None,
        ))


class ClienteFalso:
    def __init__(self):
        self.lojas = (
            LojaAdministrativaXano(1, "Ativa", "Rua A", "Sul", "Ativa"),
            LojaAdministrativaXano(2, "Inativa", "Rua B", "Sul", "Inativa"),
            LojaAdministrativaXano(3, "Legada", "Rua C", "Sul", "Ativo"),
        )
        self.totens = (TotemAdministrativoXano(4, "T-04", "Totem 04", 2, None),)
        self.usuarios = (UsuarioCadastroXano(8, "Gerente", "g@example.test", "gerente", 2),)
        self.edicoes = []
        self.exclusoes = []
        self.consultas_lojas = 0

    async def obter_identidade(self, token):
        return IdentidadeXano(
            id=12, nome="Pessoa", email="p@example.test",
            role="tecnico", lojas_id=None, deve_trocar_senha=False,
        )

    async def listar_registros_lojas(self, token):
        self.consultas_lojas += 1
        return self.lojas

    async def listar_totens_administracao(self, token):
        return self.totens

    async def listar_usuarios_administracao(self, token):
        return self.usuarios

    async def listar_categorias_administracao(self, token):
        return ({"id": 5, "nome": "Rede"},)

    async def editar_usuario_administrativo(self, token, usuario_id, **dados):
        self.edicoes.append((usuario_id, dados))

    async def excluir_totem(self, token, totem_id):
        self.exclusoes.append(totem_id)


def novo_estado():
    raiz = AuthState(_reflex_internal_init=True)
    estado = GestaoAdministrativaState(parent_state=raiz, _reflex_internal_init=True)
    raiz._auth_token = "token-teste"
    raiz.usuario_id = 12
    raiz.nome = "Pessoa autenticada"
    raiz.email = "pessoa@example.test"
    raiz.role = "administrador"
    raiz.sessao_confirmada = True
    estado.usuario_id_contexto = raiz.usuario_id
    estado._token_contexto_admin = raiz._auth_token
    estado._versao_contexto_admin = raiz._versao_sessao
    return raiz, estado


def test_estado_preserva_loja_inativa_atual_ao_editar_gerente(monkeypatch):
    cliente = ClienteFalso()
    monkeypatch.setattr(modulo_gestao, "criar_cliente_xano", lambda: cliente)
    _, estado = novo_estado()
    executar(estado._atualizar_listas())
    assert [loja["id"] for loja in estado.lojas_destino] == [1, 3]

    GestaoAdministrativaState.editar_usuario.fn(estado, 8)
    assert [loja["id"] for loja in estado.lojas_destino] == [1, 2, 3]
    assert estado.perfil_usuario == "gerente"
    assert estado.loja_form_id == "2"

    assert estado.nome_form == "Gerente"
    assert estado.nome == "Pessoa autenticada"
    assert estado.email == "pessoa@example.test"

    coletar(GestaoAdministrativaState.salvar_usuario.fn(estado, {}))
    assert cliente.edicoes == [(8, {
        "nome": "Gerente", "email": "g@example.test",
        "role": "gerente", "lojas_id": 2,
    })]


def test_listagem_resolve_nome_da_loja_e_recalcula_perfis(monkeypatch):
    cliente = ClienteFalso()
    cliente.usuarios = (
        UsuarioCadastroXano(8, "Gerente", "g@example.test", "gerente", 2),
        UsuarioCadastroXano(9, "Admin", "a@example.test", "administrador", None),
        UsuarioCadastroXano(10, "Técnica", "t@example.test", "tecnico", None),
        UsuarioCadastroXano(11, "Diretora", "d@example.test", "diretoria", None),
    )
    monkeypatch.setattr(modulo_gestao, "criar_cliente_xano", lambda: cliente)
    _, estado = novo_estado()
    executar(estado._atualizar_listas())
    assert estado.usuarios[0]["loja_nome"] == "Inativa"
    assert estado.usuarios[1]["loja_nome"] == "—"
    assert estado.totens[0]["loja_nome"] == "Inativa"
    assert (estado.administradores_total, estado.gerentes_total,
            estado.tecnicos_total, estado.diretoria_total) == (1, 1, 1, 1)

    cliente.lojas = (
        cliente.lojas[0],
        LojaAdministrativaXano(2, "Loja renomeada", "Rua B", "Sul", "Inativa"),
        cliente.lojas[2],
    )
    executar(estado._atualizar_listas("lojas"))
    assert estado.usuarios[0]["loja_nome"] == "Loja renomeada"
    assert estado.totens[0]["loja_nome"] == "Loja renomeada"


def test_exclusao_exige_confirmacao_e_cancelamento_nao_chama_backend(monkeypatch):
    cliente = ClienteFalso()
    monkeypatch.setattr(modulo_gestao, "criar_cliente_xano", lambda: cliente)
    _, estado = novo_estado()
    GestaoAdministrativaState.confirmar_exclusao.fn(estado, "totem", 4)
    assert estado.exclusao_id == 4
    GestaoAdministrativaState.cancelar_exclusao.fn(estado)
    assert estado.exclusao_id == 0
    assert cliente.exclusoes == []


@pytest.mark.parametrize("mensagem,esperado", [
    ("Totem possui vínculos ou histórico impeditivos.", "possui vínculos ou registros no histórico"),
    ("Totem possui transferência histórica.", "já foi transferido entre Lojas"),
])
def test_exclusao_impedida_exibe_motivo_no_dialogo(monkeypatch, mensagem, esperado):
    class ClienteBloqueado(ClienteFalso):
        async def excluir_totem(self, token, totem_id):
            raise XanoEntradaInvalida(mensagem)

    monkeypatch.setattr(modulo_gestao, "criar_cliente_xano", ClienteBloqueado)
    _, estado = novo_estado()
    GestaoAdministrativaState.confirmar_exclusao.fn(estado, "totem", 4)
    coletar(GestaoAdministrativaState.excluir_confirmado.fn(estado))
    assert esperado in estado.erro_exclusao
    assert estado.erro == ""
    assert estado.exclusao_id == 4
    assert "GestaoAdministrativaState.erro_exclusao" in inspect.getsource(
        modulo_gestao._confirmacao_exclusao
    )
    GestaoAdministrativaState.cancelar_exclusao.fn(estado)
    assert estado.erro_exclusao == ""


def test_nova_tela_tem_guarda_de_rota():
    componente = gestao_administrativa()
    assert componente is not None


def test_perfil_nao_administrativo_nao_carrega_cadastros(monkeypatch):
    cliente = ClienteFalso()
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente)
    monkeypatch.setattr(modulo_gestao, "criar_cliente_xano", lambda: cliente)
    _, estado = novo_estado()

    coletar(GestaoAdministrativaState.carregar.fn(estado))

    assert cliente.consultas_lojas == 0
    assert estado.lojas == []
    assert estado.totens == []
    assert estado.usuarios == []


def test_troca_de_sessao_durante_consulta_descarta_resposta_antiga(monkeypatch):
    raiz, estado = novo_estado()

    class ClienteComTroca(ClienteFalso):
        async def listar_registros_lojas(self, token):
            raiz._auth_token = "token-da-proxima-sessao"
            raiz.usuario_id = 33
            return self.lojas

    monkeypatch.setattr(modulo_gestao, "criar_cliente_xano", ClienteComTroca)
    executar(estado._atualizar_listas())
    assert estado.lojas == []
    assert estado.totens == []
    assert estado.usuarios == []
