import asyncio

import httpx
import pytest

from app.services.xano import (
    CredenciaisInvalidas,
    XanoCliente,
    XanoContratoInvalido,
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
