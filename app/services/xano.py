"""Cliente HTTP centralizado para os contratos autenticados do Xano."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv()

PERFIS_OFICIAIS = frozenset({"gerente", "tecnico", "diretoria"})
TIMEOUT_PADRAO_SEGUNDOS = 10.0


class XanoErro(RuntimeError):
    """Erro sanitizado ao consumir um contrato do Xano."""


class CredenciaisInvalidas(XanoErro):
    """O Xano rejeitou as credenciais de login."""


class XanoNaoAutenticado(XanoErro):
    """O Xano não reconheceu o token informado."""


class XanoNaoAutorizado(XanoErro):
    """O Xano reconheceu a sessão, mas negou a operação."""


class XanoContratoInvalido(XanoErro):
    """A resposta não corresponde ao contrato consolidado."""


class XanoIndisponivel(XanoErro):
    """O Xano não pôde responder temporariamente."""


@dataclass(frozen=True, slots=True)
class IdentidadeXano:
    """Dados públicos retornados pelo contrato GET /me."""

    id: int
    nome: str
    email: str
    role: str
    lojas_id: int | None


def _ler_timeout(valor: str | None) -> float:
    if valor is None or not valor.strip():
        return TIMEOUT_PADRAO_SEGUNDOS

    try:
        timeout = float(valor)
    except ValueError as erro:
        raise XanoContratoInvalido(
            "XANO_REQUEST_TIMEOUT_SECONDS deve ser numérico."
        ) from erro

    if timeout <= 0:
        raise XanoContratoInvalido(
            "XANO_REQUEST_TIMEOUT_SECONDS deve ser maior que zero."
        )

    return timeout


class XanoCliente:
    """Adaptador assíncrono dos contratos necessários nesta change."""

    def __init__(
        self,
        base_url: str,
        timeout_segundos: float = TIMEOUT_PADRAO_SEGUNDOS,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        base_url = base_url.strip().rstrip("/")
        placeholders = {
            "url_da_api_do_xano",
            "url_do_grupo_de_autenticacao_do_xano",
        }
        if not base_url or base_url in placeholders:
            raise XanoContratoInvalido(
                "XANO_AUTH_BASE_URL não configurada."
            )
        if timeout_segundos <= 0:
            raise XanoContratoInvalido(
                "O timeout do cliente Xano deve ser maior que zero."
            )

        self._base_url = base_url
        self._timeout_segundos = timeout_segundos
        self._transport = transport

    async def _requisitar(
        self,
        metodo: str,
        caminho: str,
        *,
        token: str | None = None,
        json: dict[str, Any] | None = None,
        login: bool = False,
    ) -> dict[str, Any]:
        cabecalhos: dict[str, str] = {}
        if token:
            cabecalhos["Authorization"] = f"Bearer {token}"

        try:
            async with httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout_segundos,
                transport=self._transport,
            ) as cliente:
                resposta = await cliente.request(
                    metodo,
                    caminho,
                    headers=cabecalhos,
                    json=json,
                )
        except (httpx.TimeoutException, httpx.NetworkError) as erro:
            raise XanoIndisponivel(
                "Não foi possível acessar o Xano temporariamente."
            ) from erro
        except httpx.RequestError as erro:
            raise XanoIndisponivel(
                "Não foi possível concluir a requisição ao Xano."
            ) from erro

        if login and resposta.status_code in {400, 401, 403, 422}:
            raise CredenciaisInvalidas("Credenciais inválidas.")
        if resposta.status_code == 401:
            raise XanoNaoAutenticado("Sessão não autenticada.")
        if resposta.status_code == 403:
            raise XanoNaoAutorizado("Acesso não autorizado.")
        if resposta.status_code >= 500:
            raise XanoIndisponivel("O Xano está indisponível temporariamente.")
        if resposta.is_error:
            raise XanoContratoInvalido("O Xano rejeitou a requisição.")

        try:
            dados = resposta.json()
        except ValueError as erro:
            raise XanoContratoInvalido(
                "O Xano retornou uma resposta inválida."
            ) from erro

        if not isinstance(dados, dict):
            raise XanoContratoInvalido(
                "O Xano retornou um formato inesperado."
            )
        return dados

    async def login(self, email: str, senha: str) -> str:
        dados = await self._requisitar(
            "POST",
            "/login",
            json={"email": email, "senha": senha},
            login=True,
        )
        token = dados.get("authToken")
        if not isinstance(token, str) or not token:
            raise XanoContratoInvalido(
                "O login não retornou o token esperado."
            )
        return token

    async def obter_identidade(self, token: str) -> IdentidadeXano:
        if not token:
            raise XanoNaoAutenticado("Sessão não autenticada.")

        dados = await self._requisitar("GET", "/me", token=token)
        usuario_id = dados.get("id")
        nome = dados.get("nome")
        email = dados.get("email")
        role = dados.get("role")
        lojas_id = dados.get("lojas_id")

        identidade_valida = (
            isinstance(usuario_id, int)
            and not isinstance(usuario_id, bool)
            and isinstance(nome, str)
            and bool(nome.strip())
            and isinstance(email, str)
            and bool(email.strip())
            and role in PERFIS_OFICIAIS
            and (
                lojas_id is None
                or (isinstance(lojas_id, int) and not isinstance(lojas_id, bool))
            )
        )
        if not identidade_valida:
            raise XanoContratoInvalido(
                "A identidade retornada pelo Xano é inválida."
            )

        return IdentidadeXano(
            id=usuario_id,
            nome=nome,
            email=email,
            role=role,
            lojas_id=lojas_id,
        )


def criar_cliente_xano() -> XanoCliente:
    """Cria o cliente da API de autenticação a partir do ambiente."""

    return XanoCliente(
        base_url=os.getenv("XANO_AUTH_BASE_URL", ""),
        timeout_segundos=_ler_timeout(
            os.getenv("XANO_REQUEST_TIMEOUT_SECONDS")
        ),
    )
