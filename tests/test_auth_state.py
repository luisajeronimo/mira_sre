import asyncio
from pathlib import Path

import pytest

import app.states.auth as auth_module
from app.services.xano import (
    CredenciaisInvalidas,
    IdentidadeXano,
    XanoIndisponivel,
    XanoContratoInvalido,
    XanoNaoAutenticado,
    XanoNaoAutorizado,
)
from app.states.auth import (
    MENSAGEM_CREDENCIAIS,
    MENSAGEM_EXPIRADA,
    MENSAGEM_IDENTIDADE_INVALIDA,
    MENSAGEM_INDISPONIVEL,
    MENSAGEM_NAO_AUTORIZADO,
    AuthState,
)


IDENTIDADES = {
    perfil: IdentidadeXano(
        id=indice,
        nome=perfil.title(),
        email=f"{perfil}@example.test",
        role=perfil,
        lojas_id=1 if perfil == "gerente" else None,
    )
    for indice, perfil in enumerate(
        ("gerente", "tecnico", "diretoria", "administrador"),
        start=1,
    )
}


class ClienteFalso:
    def __init__(
        self,
        identidade=IDENTIDADES["gerente"],
        erro_login=None,
        erro_me=None,
    ):
        self.identidade = identidade
        self.erro_login = erro_login
        self.erro_me = erro_me
        self.chamadas = []

    async def login(self, email, senha):
        self.chamadas.append(("login", email, senha))
        if self.erro_login:
            raise self.erro_login
        return "token-backend"

    async def obter_identidade(self, token):
        self.chamadas.append(("me", token))
        if self.erro_me:
            raise self.erro_me
        return self.identidade


def novo_estado():
    return AuthState(_reflex_internal_init=True)


async def coletar(gerador):
    return [evento async for evento in gerador]


def executar_evento(handler, estado, *args):
    return asyncio.run(coletar(handler.fn(estado, *args)))


def destino_redirect(evento):
    return evento.args[0][1]._var_value


def test_token_e_backend_only_e_nao_usa_armazenamento_cliente():
    assert "_auth_token" in AuthState.backend_vars
    assert "_auth_token" not in AuthState.base_vars

    fonte = "\n".join(
        arquivo.read_text(encoding="utf-8")
        for arquivo in Path("app").rglob("*.py")
    )
    for mecanismo in ("LocalStorage", "SessionStorage", "Cookie", "refresh"):
        assert mecanismo not in fonte


@pytest.mark.parametrize(
    ("perfil", "destino"),
    [
        ("gerente", "/gerente"),
        ("tecnico", "/tecnico"),
        ("diretoria", "/diretoria"),
        ("administrador", "/administracao"),
    ],
)
def test_login_confirma_me_e_redireciona_por_perfil(
    monkeypatch,
    perfil,
    destino,
):
    cliente = ClienteFalso(identidade=IDENTIDADES[perfil])
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente)
    estado = novo_estado()

    eventos = executar_evento(
        AuthState.login,
        estado,
        {"email": " USUARIO@EXAMPLE.TEST ", "senha": "segredo"},
    )

    assert cliente.chamadas == [
        ("login", "usuario@example.test", "segredo"),
        ("me", "token-backend"),
    ]
    assert estado._auth_token == "token-backend"
    assert estado.sessao_confirmada is True
    assert estado.role == perfil
    assert destino_redirect(eventos[-1]) == destino


def test_login_em_processamento_ignora_envio_concorrente(monkeypatch):
    cliente = ClienteFalso()
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente)
    estado = novo_estado()
    estado.carregando = True

    eventos = executar_evento(
        AuthState.login,
        estado,
        {"email": "usuario@example.test", "senha": "segredo"},
    )

    assert eventos == []
    assert cliente.chamadas == []


def test_credenciais_invalidas_limpam_sessao_e_mensagem_e_generica(
    monkeypatch,
):
    cliente = ClienteFalso(erro_login=CredenciaisInvalidas("detalhe"))
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente)
    estado = novo_estado()

    executar_evento(
        AuthState.login,
        estado,
        {"email": "usuario@example.test", "senha": "segredo"},
    )

    assert estado._auth_token == ""
    assert estado.sessao_confirmada is False
    assert estado.mensagem_erro == MENSAGEM_CREDENCIAIS
    assert "detalhe" not in estado.mensagem_erro


def test_login_so_publica_sessao_depois_do_me(monkeypatch):
    cliente = ClienteFalso(erro_me=XanoIndisponivel("detalhe"))
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente)
    estado = novo_estado()

    executar_evento(
        AuthState.login,
        estado,
        {"email": "usuario@example.test", "senha": "segredo"},
    )

    assert estado._auth_token == ""
    assert estado.usuario_id is None
    assert estado.sessao_confirmada is False
    assert estado.mensagem_erro == MENSAGEM_INDISPONIVEL


def test_state_perdido_exige_nova_autenticacao():
    estado = novo_estado()

    eventos = executar_evento(AuthState.carregar_gerente, estado)

    assert estado._auth_token == ""
    assert estado.sessao_confirmada is False
    assert destino_redirect(eventos[-1]) == "/login"


def test_raiz_sem_state_exige_nova_autenticacao():
    estado = novo_estado()

    eventos = executar_evento(AuthState.carregar_raiz, estado)

    assert destino_redirect(eventos[-1]) == "/login"


def test_token_expirado_limpa_sessao(monkeypatch):
    cliente = ClienteFalso(erro_me=XanoNaoAutenticado("expirado"))
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente)
    estado = novo_estado()
    estado._auth_token = "token-expirado"
    estado.nome = "Anterior"

    eventos = executar_evento(AuthState.carregar_gerente, estado)

    assert estado._auth_token == ""
    assert estado.nome == ""
    assert estado.mensagem_erro == MENSAGEM_EXPIRADA
    assert destino_redirect(eventos[-1]) == "/login"


def test_indisponibilidade_preserva_sessao_confirmada(
    monkeypatch,
):
    cliente = ClienteFalso(erro_me=XanoIndisponivel("indisponível"))
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente)
    estado = novo_estado()
    estado._auth_token = "token-valido"
    estado.usuario_id = 7
    estado.nome = "Usuário anterior"
    estado.email = "anterior@example.test"
    estado.role = "gerente"
    estado.sessao_confirmada = True

    eventos = executar_evento(AuthState.carregar_gerente, estado)

    assert estado._auth_token == "token-valido"
    assert estado.nome == "Usuário anterior"
    assert estado.role == "gerente"
    assert estado.sessao_confirmada is True
    assert estado.mensagem_erro == MENSAGEM_INDISPONIVEL
    assert eventos == [None]


def test_contrato_invalido_na_revalidacao_preserva_sessao_confirmada(
    monkeypatch,
):
    cliente = ClienteFalso(erro_me=XanoContratoInvalido("contrato"))
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente)
    estado = novo_estado()
    estado._auth_token = "token-valido"
    estado.usuario_id = 7
    estado.nome = "Usuário anterior"
    estado.email = "anterior@example.test"
    estado.role = "gerente"
    estado.sessao_confirmada = True

    eventos = executar_evento(AuthState.carregar_gerente, estado)

    assert estado._auth_token == "token-valido"
    assert estado.role == "gerente"
    assert estado.sessao_confirmada is True
    assert estado.mensagem_erro == MENSAGEM_INDISPONIVEL
    assert eventos == [None]


def test_403_preserva_sessao_e_nao_vira_expiracao(monkeypatch):
    cliente = ClienteFalso(erro_me=XanoNaoAutorizado("negado"))
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente)
    estado = novo_estado()
    estado._auth_token = "token-valido"
    estado.usuario_id = 7
    estado.nome = "Usuário anterior"
    estado.email = "anterior@example.test"
    estado.role = "tecnico"
    estado.sessao_confirmada = True

    eventos = executar_evento(AuthState.carregar_tecnico, estado)

    assert estado._auth_token == "token-valido"
    assert estado.nome == "Usuário anterior"
    assert estado.sessao_confirmada is False
    assert estado.mensagem_erro == MENSAGEM_NAO_AUTORIZADO
    assert estado.mensagem_erro != MENSAGEM_EXPIRADA
    assert eventos == [None]


def test_guard_permite_perfil_correto_e_redireciona_perfil_diferente(
    monkeypatch,
):
    cliente = ClienteFalso(identidade=IDENTIDADES["tecnico"])
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente)
    estado = novo_estado()
    estado._auth_token = "token"

    eventos = executar_evento(AuthState.carregar_tecnico, estado)
    assert eventos == [None]
    assert estado.sessao_confirmada is True

    estado._auth_token = "token"
    eventos = executar_evento(AuthState.carregar_gerente, estado)
    assert destino_redirect(eventos[-1]) == "/tecnico"


def test_raiz_e_login_redirecionam_sessao_valida(monkeypatch):
    cliente = ClienteFalso(identidade=IDENTIDADES["diretoria"])
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente)

    for handler in (AuthState.carregar_raiz, AuthState.carregar_login):
        estado = novo_estado()
        estado._auth_token = "token"
        eventos = executar_evento(handler, estado)
        assert destino_redirect(eventos[-1]) == "/diretoria"


def test_logout_e_apenas_local_e_limpa_estado():
    estado = novo_estado()
    estado._auth_token = "token"
    estado.usuario_id = 1
    estado.nome = "Usuário"
    estado.email = "usuario@example.test"
    estado.role = "gerente"
    estado.lojas_id = 1
    estado.sessao_confirmada = True
    estado.mensagem_erro = "erro"

    evento = AuthState.logout.fn(estado)

    assert estado._auth_token == ""
    assert estado.usuario_id is None
    assert estado.nome == ""
    assert estado.email == ""
    assert estado.role == ""
    assert estado.lojas_id is None
    assert estado.sessao_confirmada is False
    assert estado.mensagem_erro == ""
    assert destino_redirect(evento) == "/login"

    eventos = executar_evento(AuthState.carregar_gerente, estado)
    assert destino_redirect(eventos[-1]) == "/login"


def test_sessao_pendente_prioriza_primeiro_acesso(monkeypatch):
    identidade = IdentidadeXano(
        id=4, nome="Admin", email="admin@example.test", role="administrador",
        lojas_id=None, deve_trocar_senha=True,
    )
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: ClienteFalso(identidade))
    estado = novo_estado()
    estado._auth_token = "token"

    eventos = executar_evento(AuthState.carregar_administracao, estado)

    assert estado.deve_trocar_senha is True
    assert destino_redirect(eventos[-1]) == "/primeiro-acesso"


def identidade_pendente() -> IdentidadeXano:
    return IdentidadeXano(
        id=4,
        nome="Admin",
        email="admin@example.test",
        role="administrador",
        lojas_id=None,
        deve_trocar_senha=True,
    )


def test_login_administrador_pendente_vai_para_primeiro_acesso(monkeypatch):
    cliente = ClienteFalso(identidade=identidade_pendente())
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente)
    estado = novo_estado()

    eventos = executar_evento(
        AuthState.login,
        estado,
        {"email": "admin@example.test", "senha": "segredo"},
    )

    assert estado.sessao_confirmada is True
    assert estado.deve_trocar_senha is True
    assert destino_redirect(eventos[-1]) == "/primeiro-acesso"


def test_primeiro_acesso_pendente_revalida_sem_redirecionar(monkeypatch):
    cliente = ClienteFalso(identidade=identidade_pendente())
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente)
    estado = novo_estado()
    estado._auth_token = "token"

    eventos = executar_evento(AuthState.carregar_primeiro_acesso, estado)

    assert cliente.chamadas == [("me", "token")]
    assert estado.sessao_confirmada is True
    assert estado.deve_trocar_senha is True
    assert eventos == [None]


def test_visitante_em_primeiro_acesso_redireciona_para_login():
    estado = novo_estado()

    eventos = executar_evento(AuthState.carregar_primeiro_acesso, estado)

    assert estado.sessao_confirmada is False
    assert destino_redirect(eventos[-1]) == "/login"


def test_primeiro_acesso_pendente_revalidacoes_repetidas_nao_criam_loop(
    monkeypatch,
):
    cliente = ClienteFalso(identidade=identidade_pendente())
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente)
    estado = novo_estado()
    estado._auth_token = "token"

    for _ in range(2):
        eventos = executar_evento(AuthState.carregar_primeiro_acesso, estado)
        assert eventos == [None]
        assert estado.sessao_confirmada is True
        assert estado.deve_trocar_senha is True

    assert cliente.chamadas == [("me", "token"), ("me", "token")]


@pytest.mark.parametrize(
    ("perfil", "destino"),
    [
        ("gerente", "/gerente"),
        ("tecnico", "/tecnico"),
        ("diretoria", "/diretoria"),
        ("administrador", "/administracao"),
    ],
)
def test_primeiro_acesso_concluido_redireciona_para_destino_do_perfil(
    monkeypatch,
    perfil,
    destino,
):
    cliente = ClienteFalso(identidade=IDENTIDADES[perfil])
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente)
    estado = novo_estado()
    estado._auth_token = "token"

    eventos = executar_evento(AuthState.carregar_primeiro_acesso, estado)

    assert estado.sessao_confirmada is True
    assert estado.deve_trocar_senha is False
    assert destino_redirect(eventos[-1]) == destino


def test_primeiro_acesso_com_identidade_invalida_limpa_sessao(monkeypatch):
    identidade_invalida = IdentidadeXano(
        id=4,
        nome="Legado",
        email="legado@example.test",
        role="admin",
        lojas_id=None,
        deve_trocar_senha=True,
    )
    monkeypatch.setattr(
        auth_module,
        "criar_cliente_xano",
        lambda: ClienteFalso(identidade=identidade_invalida),
    )
    estado = novo_estado()
    estado._auth_token = "token"

    eventos = executar_evento(AuthState.carregar_primeiro_acesso, estado)

    assert estado._auth_token == ""
    assert estado.sessao_confirmada is False
    assert estado.mensagem_erro == MENSAGEM_IDENTIDADE_INVALIDA
    assert destino_redirect(eventos[-1]) == "/login"
