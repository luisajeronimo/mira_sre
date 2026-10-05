"""Cliente HTTP centralizado para os contratos autenticados do Xano."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx
from dotenv import load_dotenv


load_dotenv()

PERFIS_OFICIAIS = frozenset({"gerente", "tecnico", "diretoria", "administrador"})
TIMEOUT_PADRAO_SEGUNDOS = 10.0


class XanoErro(RuntimeError):
    """Erro sanitizado ao consumir um contrato do Xano."""


class CredenciaisInvalidas(XanoErro):
    """O Xano rejeitou as credenciais de login."""


class XanoNaoAutenticado(XanoErro):
    """O Xano não reconheceu o token informado."""


class XanoNaoAutorizado(XanoErro):
    """O Xano reconheceu a sessão, mas negou a operação."""


class XanoNaoEncontrado(XanoErro):
    """O recurso solicitado não existe."""


class XanoConflito(XanoErro):
    """A operação perdeu uma disputa concorrente."""


class XanoEntradaInvalida(XanoErro):
    """O Xano rejeitou os dados funcionais enviados."""


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
    deve_trocar_senha: bool = False


@dataclass(frozen=True, slots=True)
class UsuarioAdministrativoXano:
    """Identidade pública retornada ao provisionar um usuário."""

    id: int
    nome: str
    email: str
    role: str
    lojas_id: int | None
    deve_trocar_senha: bool


@dataclass(frozen=True, slots=True)
class LojaOpcaoAdministracaoXano:
    """Opção mínima de Loja disponível na criação administrativa de Gerente."""

    id: int
    nome: str


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
        nome_configuracao: str = "XANO_AUTH_BASE_URL",
    ) -> None:
        base_url = base_url.strip().rstrip("/")
        placeholders = {
            "url_da_api_do_xano",
            "url_do_grupo_de_autenticacao_do_xano",
            "url_do_grupo_de_service_desk_do_xano",
        }
        if not base_url or base_url in placeholders:
            raise XanoContratoInvalido(
                f"{nome_configuracao} não configurada."
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
        erro_400_como_entrada: bool = False,
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
        if resposta.status_code == 404:
            raise XanoNaoEncontrado("Recurso não encontrado.")
        if resposta.status_code == 409:
            raise XanoConflito("O chamado foi assumido por outro Técnico.")
        if resposta.status_code == 422:
            raise XanoEntradaInvalida("Os dados informados são inválidos.")
        if resposta.status_code == 400 and erro_400_como_entrada:
            raise XanoEntradaInvalida("Os dados informados são inválidos.")
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
        deve_trocar_senha = dados.get("deve_trocar_senha")

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
            and isinstance(deve_trocar_senha, bool)
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
            deve_trocar_senha=deve_trocar_senha,
        )

    async def criar_usuario_administrativo(
        self,
        token: str,
        *,
        nome: str,
        email: str,
        role: str,
        lojas_id: int | None,
        senha_temporaria: str,
    ) -> UsuarioAdministrativoXano:
        payload = {
            "nome": nome,
            "email": email,
            "role": role,
            "senha_temporaria": senha_temporaria,
        }
        if lojas_id is not None:
            payload["lojas_id"] = lojas_id
        dados = await self._requisitar(
            "POST",
            "/administracao/usuarios",
            token=token,
            json=payload,
            erro_400_como_entrada=True,
        )
        try:
            usuario = UsuarioAdministrativoXano(
                id=dados["id"], nome=dados["nome"], email=dados["email"],
                role=dados["role"], lojas_id=dados.get("lojas_id"),
                deve_trocar_senha=dados["deve_trocar_senha"],
            )
        except (KeyError, TypeError) as erro:
            raise XanoContratoInvalido("O Xano retornou um usuário inválido.") from erro
        if (
            not isinstance(usuario.id, int) or isinstance(usuario.id, bool)
            or not isinstance(usuario.nome, str) or not usuario.nome.strip()
            or not isinstance(usuario.email, str) or not usuario.email.strip()
            or usuario.role not in PERFIS_OFICIAIS
            or not isinstance(usuario.deve_trocar_senha, bool)
            or (usuario.lojas_id is not None and (not isinstance(usuario.lojas_id, int) or isinstance(usuario.lojas_id, bool)))
        ):
            raise XanoContratoInvalido("O Xano retornou um usuário inválido.")
        return usuario

    async def listar_lojas_administracao(
        self, token: str
    ) -> tuple[LojaOpcaoAdministracaoXano, ...]:
        """Obtém somente opções de Loja para criação administrativa de Gerente."""

        if not token:
            raise XanoNaoAutenticado("Sessão não autenticada.")

        dados = await self._requisitar(
            "GET", "/administracao/lojas", token=token
        )
        lojas = dados.get("lojas")
        if set(dados) != {"lojas"} or not isinstance(lojas, list):
            raise XanoContratoInvalido(
                "O Xano retornou uma lista de Lojas inválida."
            )

        opcoes: list[LojaOpcaoAdministracaoXano] = []
        for loja in lojas:
            if (
                not isinstance(loja, dict)
                or set(loja) != {"id", "nome"}
                or not isinstance(loja.get("id"), int)
                or isinstance(loja.get("id"), bool)
                or loja["id"] < 1
                or not isinstance(loja.get("nome"), str)
                or not loja["nome"].strip()
            ):
                raise XanoContratoInvalido(
                    "O Xano retornou uma opção de Loja inválida."
                )
            opcoes.append(
                LojaOpcaoAdministracaoXano(id=loja["id"], nome=loja["nome"])
            )
        return tuple(opcoes)

    async def trocar_senha_primeiro_acesso(self, token: str, nova_senha: str) -> None:
        dados = await self._requisitar(
            "POST", "/primeiro-acesso/trocar-senha", token=token,
            json={"nova_senha": nova_senha},
        )
        if dados.get("success") is not True:
            raise XanoContratoInvalido("O Xano não confirmou a troca de senha.")


def criar_cliente_xano() -> XanoCliente:
    """Cria o cliente da API de autenticação a partir do ambiente."""

    return XanoCliente(
        base_url=os.getenv("XANO_AUTH_BASE_URL", ""),
        timeout_segundos=_ler_timeout(
            os.getenv("XANO_REQUEST_TIMEOUT_SECONDS")
        ),
    )
