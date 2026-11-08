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
ERROS_FUNCIONAIS_ADMINISTRACAO = frozenset({
    "O último Administrador deve permanecer.",
    "Não é permitido excluir a própria conta.",
    "Loja possui vínculos ou histórico impeditivos.",
    "Totem possui vínculos ou histórico impeditivos.",
    "Totem possui transferência histórica.",
    "Usuário possui vínculos ou histórico impeditivos.",
    "Loja inexistente ou Inativa.",
    "Loja de destino inexistente ou Inativa.",
    "Loja inexistente ou Inativa para novo vínculo.",
    "Técnico possui chamado atribuído.",
    "E-mail já cadastrado.",
    "Loja incompatível com o perfil.",
    "Situação inválida.",
})


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


class XanoRateLimitado(XanoIndisponivel):
    """O Xano aplicou limite transitório de requisições."""

    def __init__(
        self,
        mensagem: str = "O serviço está temporariamente ocupado. Tente novamente.",
        *,
        retry_after_segundos: float | None = None,
    ) -> None:
        super().__init__(mensagem)
        self.retry_after_segundos = retry_after_segundos


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


@dataclass(frozen=True, slots=True)
class LojaAdministrativaXano:
    id: int
    nome: str | None
    endereco: str | None
    regiao: str | None
    status: str | None


@dataclass(frozen=True, slots=True)
class TotemAdministrativoXano:
    id: int
    identificacao: str | None
    nome: str | None
    lojas_id: int | None
    status_atual: str | None


@dataclass(frozen=True, slots=True)
class UsuarioCadastroXano:
    id: int
    nome: str
    email: str
    role: str
    lojas_id: int | None


def _inteiro_positivo(valor: Any) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool) and valor > 0


def _loja_administrativa(dados: dict[str, Any]) -> LojaAdministrativaXano:
    if (
        set(dados) != {"id", "nome", "endereco", "regiao", "status"}
        or not _inteiro_positivo(dados.get("id"))
        or any(dados.get(campo) is not None and not isinstance(dados[campo], str) for campo in ("nome", "endereco", "regiao"))
        or dados["status"] not in {"Ativa", "Inativa", "ativa", "inativa", "Ativo", None}
    ):
        raise XanoContratoInvalido("O Xano retornou uma Loja inválida.")
    return LojaAdministrativaXano(**dados)


def _totem_administrativo(dados: dict[str, Any]) -> TotemAdministrativoXano:
    if (
        set(dados) != {"id", "identificacao", "nome", "lojas_id", "status_atual"}
        or not _inteiro_positivo(dados.get("id"))
        or (dados.get("nome") is not None and not isinstance(dados["nome"], str))
        or (dados.get("identificacao") is not None and not isinstance(dados["identificacao"], str))
        or (dados.get("lojas_id") is not None and not _inteiro_positivo(dados["lojas_id"]))
        or (dados.get("status_atual") is not None and not isinstance(dados["status_atual"], str))
    ):
        raise XanoContratoInvalido("O Xano retornou um Totem inválido.")
    return TotemAdministrativoXano(**dados)


def _usuario_cadastro(dados: dict[str, Any]) -> UsuarioCadastroXano:
    # Registros anteriores ao contrato administrativo usam 0 como ausência de
    # Loja para perfis sem vínculo obrigatório. A projeção não altera o dado.
    if dados.get("role") != "gerente" and dados.get("lojas_id") == 0:
        dados = {**dados, "lojas_id": None}
    if (
        set(dados) != {"id", "nome", "email", "role", "lojas_id"}
        or not _inteiro_positivo(dados.get("id"))
        or not isinstance(dados.get("nome"), str)
        or not dados["nome"].strip()
        or not isinstance(dados.get("email"), str)
        or not dados["email"].strip()
        or dados.get("role") not in PERFIS_OFICIAIS
        or (dados.get("lojas_id") is not None and not _inteiro_positivo(dados["lojas_id"]))
    ):
        raise XanoContratoInvalido("O Xano retornou um usuário inválido.")
    return UsuarioCadastroXano(**dados)


def _lista_administrativa(dados: dict[str, Any], parser: Any) -> tuple[Any, ...]:
    if set(dados) != {"items"} or not isinstance(dados["items"], list):
        raise XanoContratoInvalido("O Xano retornou uma lista administrativa inválida.")
    if not all(isinstance(item, dict) for item in dados["items"]):
        raise XanoContratoInvalido("O Xano retornou uma lista administrativa inválida.")
    return tuple(parser(item) for item in dados["items"])


def _mensagem_funcional_permitida(resposta: httpx.Response) -> str:
    try:
        dados = resposta.json()
    except ValueError:
        return "Os dados informados são inválidos."
    if isinstance(dados, dict):
        for chave in ("message", "error"):
            mensagem = dados.get(chave)
            if isinstance(mensagem, str) and mensagem in ERROS_FUNCIONAIS_ADMINISTRACAO:
                return mensagem
    return "Os dados informados são inválidos."


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
        params: httpx.QueryParamTypes | None = None,
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
                    params=params,
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
        if resposta.status_code == 429:
            retry_after = resposta.headers.get("Retry-After")
            retry_after_segundos = None
            if retry_after is not None:
                try:
                    valor = float(retry_after)
                except ValueError:
                    valor = None
                if valor is not None and valor >= 0:
                    retry_after_segundos = valor
            raise XanoRateLimitado(retry_after_segundos=retry_after_segundos)
        if resposta.status_code == 422:
            raise XanoEntradaInvalida(_mensagem_funcional_permitida(resposta))
        if resposta.status_code == 400 and erro_400_como_entrada:
            raise XanoEntradaInvalida(_mensagem_funcional_permitida(resposta))
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

    async def listar_registros_lojas(self, token: str) -> tuple[LojaAdministrativaXano, ...]:
        dados = await self._requisitar("GET", "/administracao/lojas/registros", token=token)
        return _lista_administrativa(dados, _loja_administrativa)

    async def obter_registro_loja(self, token: str, loja_id: int) -> LojaAdministrativaXano:
        dados = await self._requisitar("GET", f"/administracao/lojas/{loja_id}", token=token)
        return _loja_administrativa(dados)

    async def criar_loja(self, token: str, *, nome: str, endereco: str, regiao: str) -> LojaAdministrativaXano:
        dados = await self._requisitar(
            "POST", "/administracao/lojas/registros", token=token,
            json={"nome": nome, "endereco": endereco, "regiao": regiao},
            erro_400_como_entrada=True,
        )
        return _loja_administrativa(dados)

    async def editar_loja(self, token: str, loja_id: int, *, nome: str, endereco: str, regiao: str, status: str) -> LojaAdministrativaXano:
        dados = await self._requisitar(
            "PATCH", f"/administracao/lojas/{loja_id}", token=token,
            json={"nome": nome, "endereco": endereco, "regiao": regiao, "status": status},
            erro_400_como_entrada=True,
        )
        return _loja_administrativa(dados)

    async def excluir_loja(self, token: str, loja_id: int) -> None:
        dados = await self._requisitar(
            "DELETE", f"/administracao/lojas/{loja_id}", token=token,
            erro_400_como_entrada=True,
        )
        if dados.get("success") is not True:
            raise XanoContratoInvalido("O Xano não confirmou a exclusão da Loja.")

    async def listar_totens_administracao(self, token: str) -> tuple[TotemAdministrativoXano, ...]:
        dados = await self._requisitar("GET", "/administracao/totens", token=token)
        return _lista_administrativa(dados, _totem_administrativo)

    async def obter_totem_administrativo(self, token: str, totem_id: int) -> TotemAdministrativoXano:
        dados = await self._requisitar("GET", f"/administracao/totens/{totem_id}", token=token)
        return _totem_administrativo(dados)

    async def criar_totem(self, token: str, *, identificacao: str, nome: str, lojas_id: int) -> TotemAdministrativoXano:
        dados = await self._requisitar(
            "POST", "/administracao/totens", token=token,
            json={"identificacao": identificacao, "nome": nome, "lojas_id": lojas_id},
            erro_400_como_entrada=True,
        )
        return _totem_administrativo(dados)

    async def editar_totem(self, token: str, totem_id: int, *, identificacao: str, nome: str, lojas_id: int) -> TotemAdministrativoXano:
        dados = await self._requisitar(
            "PATCH", f"/administracao/totens/{totem_id}", token=token,
            json={"identificacao": identificacao, "nome": nome, "lojas_id": lojas_id},
            erro_400_como_entrada=True,
        )
        return _totem_administrativo(dados)

    async def excluir_totem(self, token: str, totem_id: int) -> None:
        dados = await self._requisitar(
            "DELETE", f"/administracao/totens/{totem_id}", token=token,
            erro_400_como_entrada=True,
        )
        if dados.get("success") is not True:
            raise XanoContratoInvalido("O Xano não confirmou a exclusão do Totem.")

    async def listar_usuarios_administracao(self, token: str) -> tuple[UsuarioCadastroXano, ...]:
        dados = await self._requisitar("GET", "/administracao/usuarios", token=token)
        return _lista_administrativa(dados, _usuario_cadastro)

    async def obter_usuario_administrativo(self, token: str, usuario_id: int) -> UsuarioCadastroXano:
        dados = await self._requisitar("GET", f"/administracao/usuarios/{usuario_id}", token=token)
        return _usuario_cadastro(dados)

    async def editar_usuario_administrativo(self, token: str, usuario_id: int, *, nome: str, email: str, role: str, lojas_id: int | None) -> UsuarioCadastroXano:
        dados = await self._requisitar(
            "PATCH", f"/administracao/usuarios/{usuario_id}", token=token,
            json={"nome": nome, "email": email, "role": role, "lojas_id": lojas_id},
            erro_400_como_entrada=True,
        )
        return _usuario_cadastro(dados)

    async def excluir_usuario_administrativo(self, token: str, usuario_id: int) -> None:
        dados = await self._requisitar(
            "DELETE", f"/administracao/usuarios/{usuario_id}", token=token,
            erro_400_como_entrada=True,
        )
        if dados.get("success") is not True:
            raise XanoContratoInvalido("O Xano não confirmou a exclusão do usuário.")

    async def listar_categorias_administracao(self, token: str) -> tuple[dict[str, Any], ...]:
        dados = await self._requisitar("GET", "/administracao/categorias", token=token)
        if set(dados) != {"items"} or not isinstance(dados["items"], list):
            raise XanoContratoInvalido("O Xano retornou categorias inválidas.")
        return tuple(dados["items"])

    async def abrir_chamado_administrativo(
        self, token: str, *, ativos_referencia_id: int, categorias_servico_id: int,
        prioridade: str, titulo: str, descricao: str,
    ) -> dict[str, Any]:
        dados = await self._requisitar(
            "POST", "/administracao/chamados", token=token,
            json={
                "ativos_referencia_id": ativos_referencia_id,
                "categorias_servico_id": categorias_servico_id,
                "prioridade": prioridade, "titulo": titulo, "descricao": descricao,
            },
            erro_400_como_entrada=True,
        )
        if not isinstance(dados.get("chamado"), dict) or not _inteiro_positivo(dados["chamado"].get("id")):
            raise XanoContratoInvalido("O Xano retornou um chamado inválido.")
        return dados["chamado"]

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
