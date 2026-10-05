import asyncio

import httpx
import pytest

from app.services.xano import (
    CredenciaisInvalidas,
    XanoCliente,
    XanoContratoInvalido,
    XanoEntradaInvalida,
    XanoIndisponivel,
    XanoNaoAutenticado,
    XanoNaoAutorizado,
    criar_cliente_xano,
)


BASE_URL = "https://xano.example/api:mira-auth"


def executar(corrotina):
    return asyncio.run(corrotina)


def test_login_e_me_usam_contratos_minimos_e_token_bearer():
    requisicoes = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        if requisicao.url.path.endswith("/login"):
            return httpx.Response(200, json={"authToken": "token-teste"})
        return httpx.Response(
            200,
            json={
                "id": 8,
                "nome": "Gerente",
                "email": "gerente@example.test",
                "role": "gerente",
                "lojas_id": 1,
                "deve_trocar_senha": False,
            },
        )

    cliente = XanoCliente(BASE_URL, transport=httpx.MockTransport(responder))
    token = executar(cliente.login("gerente@example.test", "senha-teste"))
    identidade = executar(cliente.obter_identidade(token))

    assert token == "token-teste"
    assert identidade.role == "gerente"
    assert identidade.lojas_id == 1
    assert requisicoes[0].method == "POST"
    assert str(requisicoes[0].url) == f"{BASE_URL}/login"
    assert requisicoes[0].read() == (
        b'{"email":"gerente@example.test","senha":"senha-teste"}'
    )
    assert requisicoes[1].method == "GET"
    assert str(requisicoes[1].url) == f"{BASE_URL}/me"
    assert requisicoes[1].headers["Authorization"] == "Bearer token-teste"


@pytest.mark.parametrize("role", ["tecnico", "diretoria", "administrador"])
def test_cliente_admin_usa_endpoint_e_dto_publico_sem_loja_para_perfis_globais(
    monkeypatch, role
):
    cliente = XanoCliente(BASE_URL)
    sentinela_sensivel = object()
    chamadas = []

    async def requisitar(metodo, caminho, **kwargs):
        chamadas.append((metodo, caminho, kwargs))
        return {"id": 9, "nome": "Novo", "email": "novo@example.test", "role": role, "lojas_id": None, "deve_trocar_senha": True}

    monkeypatch.setattr(cliente, "_requisitar", requisitar)
    usuario = executar(cliente.criar_usuario_administrativo("token", nome="Novo", email="novo@example.test", role=role, lojas_id=None, senha_temporaria=sentinela_sensivel))
    assert usuario.role == role
    assert usuario.deve_trocar_senha is True
    metodo, caminho, kwargs = chamadas[0]
    assert (metodo, caminho) == ("POST", "/administracao/usuarios")
    assert kwargs["token"] == "token"
    assert kwargs["json"]["senha_temporaria"] is sentinela_sensivel
    assert "lojas_id" not in kwargs["json"]
    assert kwargs["erro_400_como_entrada"] is True


def test_criacao_admin_classifica_rejeicao_http_400_como_entrada_invalida():
    cliente = XanoCliente(
        BASE_URL,
        transport=httpx.MockTransport(
            lambda _: httpx.Response(400, json={"message": "não expor"})
        ),
    )

    with pytest.raises(XanoEntradaInvalida, match="dados informados"):
        executar(
            cliente.criar_usuario_administrativo(
                "token",
                nome="Novo",
                email="novo@example.test",
                role="tecnico",
                lojas_id=None,
                senha_temporaria="senha-ficticia",
            )
        )


def test_http_400_de_outro_endpoint_continua_contrato_invalido():
    cliente = XanoCliente(
        BASE_URL,
        transport=httpx.MockTransport(
            lambda _: httpx.Response(400, json={"message": "não expor"})
        ),
    )

    with pytest.raises(XanoContratoInvalido):
        executar(cliente.obter_identidade("token"))


def test_cliente_busca_opcoes_minimas_de_loja_sem_enviar_credencial_no_corpo():
    requisicoes = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        return httpx.Response(
            200,
            json={"lojas": [{"id": 1, "nome": "Loja Paulista"}]},
        )

    cliente = XanoCliente(
        BASE_URL, transport=httpx.MockTransport(responder)
    )
    lojas = executar(cliente.listar_lojas_administracao("token-admin"))

    assert lojas[0].id == 1
    assert lojas[0].nome == "Loja Paulista"
    assert requisicoes[0].method == "GET"
    assert str(requisicoes[0].url) == f"{BASE_URL}/administracao/lojas"
    assert requisicoes[0].headers["Authorization"] == "Bearer token-admin"
    assert requisicoes[0].read() == b""


@pytest.mark.parametrize(
    "resposta",
    [
        {"items": []},
        {"lojas": [{"id": True, "nome": "Loja Paulista"}]},
        {"lojas": [{"id": 1, "nome": "Loja Paulista", "endereco": "interno"}]},
        {"lojas": [{"id": 1, "nome": "  "}]},
        {"lojas": [], "extra": "não permitido"},
    ],
)
def test_cliente_rejeita_dto_de_opcoes_de_loja_fora_do_contrato(resposta):
    cliente = XanoCliente(
        BASE_URL,
        transport=httpx.MockTransport(
            lambda _: httpx.Response(200, json=resposta)
        ),
    )

    with pytest.raises(XanoContratoInvalido):
        executar(cliente.listar_lojas_administracao("token-admin"))


@pytest.mark.parametrize("status", [400, 401, 403, 422])
def test_login_rejeitado_produz_erro_generico(status):
    transporte = httpx.MockTransport(
        lambda _: httpx.Response(status, json={"message": "não expor"})
    )
    cliente = XanoCliente(BASE_URL, transport=transporte)

    with pytest.raises(CredenciaisInvalidas, match="Credenciais inválidas"):
        executar(cliente.login("usuario@example.test", "senha"))


@pytest.mark.parametrize(
    ("status", "erro_esperado"),
    [(401, XanoNaoAutenticado), (403, XanoNaoAutorizado)],
)
def test_me_diferencia_autenticacao_e_autorizacao(status, erro_esperado):
    transporte = httpx.MockTransport(
        lambda _: httpx.Response(status, json={"message": "não expor"})
    )
    cliente = XanoCliente(BASE_URL, transport=transporte)

    with pytest.raises(erro_esperado):
        executar(cliente.obter_identidade("token"))


@pytest.mark.parametrize("status", [500, 502, 503])
def test_erros_de_servidor_sao_indisponibilidade(status):
    transporte = httpx.MockTransport(
        lambda _: httpx.Response(status, json={"message": "não expor"})
    )
    cliente = XanoCliente(BASE_URL, transport=transporte)

    with pytest.raises(XanoIndisponivel):
        executar(cliente.obter_identidade("token"))


def test_timeout_e_conexao_sao_indisponibilidade():
    for erro in (
        httpx.ReadTimeout("timeout"),
        httpx.ConnectError("conexão"),
    ):
        def falhar(requisicao: httpx.Request, erro=erro):
            raise erro

        cliente = XanoCliente(
            BASE_URL,
            transport=httpx.MockTransport(falhar),
        )
        with pytest.raises(XanoIndisponivel):
            executar(cliente.obter_identidade("token"))


@pytest.mark.parametrize(
    "resposta",
    [
        {},
        {"authToken": ""},
        {"authToken": 123},
    ],
)
def test_login_rejeita_resposta_sem_token_valido(resposta):
    cliente = XanoCliente(
        BASE_URL,
        transport=httpx.MockTransport(
            lambda _: httpx.Response(200, json=resposta)
        ),
    )
    with pytest.raises(XanoContratoInvalido):
        executar(cliente.login("usuario@example.test", "senha"))


@pytest.mark.parametrize(
    "resposta",
    [
        {},
        {
            "id": 1,
            "nome": "Legado",
            "email": "legado@example.test",
            "role": "admin",
            "lojas_id": None,
        },
        {
            "id": 1,
            "nome": "Sem e-mail",
            "email": None,
            "role": "tecnico",
            "lojas_id": None,
        },
    ],
)
def test_me_falha_fechado_para_identidade_invalida(resposta):
    cliente = XanoCliente(
        BASE_URL,
        transport=httpx.MockTransport(
            lambda _: httpx.Response(200, json=resposta)
        ),
    )
    with pytest.raises(XanoContratoInvalido):
        executar(cliente.obter_identidade("token"))


def test_configuracao_ausente_ou_timeout_invalido_falha_explicitamente(
    monkeypatch,
):
    monkeypatch.delenv("XANO_AUTH_BASE_URL", raising=False)
    monkeypatch.setenv(
        "XANO_BASE_URL",
        "https://xano.example/api:grupo-operacional",
    )
    monkeypatch.setenv("XANO_REQUEST_TIMEOUT_SECONDS", "10")
    with pytest.raises(XanoContratoInvalido, match="XANO_AUTH_BASE_URL"):
        criar_cliente_xano()

    monkeypatch.setenv("XANO_AUTH_BASE_URL", BASE_URL)
    monkeypatch.setenv("XANO_REQUEST_TIMEOUT_SECONDS", "zero")
    with pytest.raises(XanoContratoInvalido, match="deve ser numérico"):
        criar_cliente_xano()


def test_cliente_de_autenticacao_nao_reutiliza_base_operacional(monkeypatch):
    monkeypatch.setenv(
        "XANO_BASE_URL",
        "https://xano.example/api:grupo-operacional",
    )
    monkeypatch.setenv("XANO_AUTH_BASE_URL", BASE_URL)
    monkeypatch.setenv("XANO_REQUEST_TIMEOUT_SECONDS", "10")

    cliente = criar_cliente_xano()

    assert cliente._base_url == BASE_URL
