"""Cobertura explícita dos dispatchers e aliases de rotas Reflex."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from app.app import app
from app.chamados.gerente import ChamadosGerenteState
from app.chamados.tecnico import ChamadosTecnicoState
import app.chamados.tecnico.state as tecnico_module
from app.pages.administracao import AdministracaoState
import app.states.auth as auth_module
from app.services.xano import IdentidadeXano
from app.states.auth import AuthState


def _coletar(handler, estado, *args):
    async def coletar():
        return [evento async for evento in handler.fn(estado, *args)]

    return asyncio.run(coletar())


def _destino(evento):
    return evento.args[0][1]._var_value


def _estado(state_cls, *, role="", token="", confirmado=False, pendente=False):
    raiz = AuthState(_reflex_internal_init=True)
    estado = (
        raiz
        if state_cls is AuthState
        else state_cls(parent_state=raiz, _reflex_internal_init=True)
    )
    object.__setattr__(raiz, "_auth_token", token)
    object.__setattr__(estado, "_auth_token", token)
    object.__setattr__(raiz, "role", role)
    object.__setattr__(raiz, "sessao_confirmada", confirmado)
    object.__setattr__(raiz, "deve_trocar_senha", pendente)
    return estado


def _estado_direto(state_cls, *, role):
    """State isolado para exercitar os fast paths das jornadas protegidas."""
    estado = state_cls(_reflex_internal_init=True)
    object.__setattr__(estado, "_auth_token", "token")
    object.__setattr__(estado, "role", role)
    object.__setattr__(estado, "sessao_confirmada", True)
    object.__setattr__(estado, "deve_trocar_senha", True)
    return estado


class _ClienteFilaRastreado:
    def __init__(self):
        self.consultas = []

    async def listar_chamados_tecnico(self, token, **filtros):
        self.consultas.append((token, filtros))
        return SimpleNamespace(items=[], total=0)

    async def listar_ativos_tecnico(self, _token):
        return []


class _ClienteSessaoAlternada:
    def __init__(self, identidade):
        self.identidade = identidade
        self.chamadas = []

    async def login(self, email, senha):
        self.chamadas.append(("login", email, senha))
        return f"token-{self.identidade.role}"

    async def obter_identidade(self, token):
        self.chamadas.append(("me", token))
        return self.identidade


def _identidade(perfil, usuario_id):
    return IdentidadeXano(
        id=usuario_id,
        nome=perfil.title(),
        email=f"{perfil}@example.test",
        role=perfil,
        lojas_id=1 if perfil == "gerente" else None,
    )


def test_registro_contem_mapa_completo_de_rotas_canonicas_e_aliases():
    rotas = set(app._unevaluated_pages)

    assert {
        "index",
        "login",
        "primeiro-acesso",
        "inicio",
        "chamados",
        "chamados/novo",
        "chamados/[chamado_id]",
        "monitoramento",
        "administracao/usuarios",
        "gerente",
        "gerente/chamados/novo",
        "gerente/chamados/[chamado_id]",
        "tecnico",
        "tecnico/chamados/[chamado_id]",
        "diretoria",
        "administracao",
    } <= rotas

    ordem = list(app._unevaluated_pages)
    assert ordem.index("chamados/novo") < ordem.index("chamados/[chamado_id]")
    assert ordem.index("gerente/chamados/novo") < ordem.index(
        "gerente/chamados/[chamado_id]"
    )


@pytest.mark.parametrize(
    ("role", "esperado"),
    [
        ("gerente", ChamadosGerenteState),
        ("tecnico", ChamadosTecnicoState),
        ("diretoria", ChamadosTecnicoState),
        ("administrador", ChamadosTecnicoState),
    ],
)
@pytest.mark.parametrize("handler", [AuthState.carregar_inicio, AuthState.carregar_chamados])
def test_dispatcher_de_lista_aguarda_revalidacao_e_escolhe_jornada_por_perfil(
    monkeypatch, role, esperado, handler
):
    estado = _estado(AuthState)
    estados_solicitados = []

    async def revalidar(self):
        self.role = role
        self.sessao_confirmada = True
        self._auth_token = "token"
        return None

    async def get_state(self, state_cls):
        estados_solicitados.append(state_cls)
        return state_cls(_reflex_internal_init=True)

    monkeypatch.setattr(AuthState, "_revalidar", revalidar)
    monkeypatch.setattr(AuthState, "get_state", get_state)

    async def executar():
        gerador = handler.fn(estado)
        assert await gerador.__anext__() is None
        assert estados_solicitados == []
        return await gerador.__anext__()

    resultado = asyncio.run(executar())

    assert estados_solicitados == [esperado]
    assert resultado is None


@pytest.mark.parametrize(
    ("role", "esperado"),
    [
        ("gerente", ChamadosGerenteState),
        ("tecnico", ChamadosTecnicoState),
        ("diretoria", ChamadosTecnicoState),
        ("administrador", ChamadosTecnicoState),
    ],
)
def test_dispatcher_de_detalhe_escolhe_o_handler_contextual(monkeypatch, role, esperado):
    estado = _estado(AuthState)
    estados_solicitados = []

    async def revalidar(self, _perfil_esperado=None):
        self.role = role
        self.sessao_confirmada = True
        self._auth_token = "token"
        return None

    async def get_state(self, state_cls):
        estados_solicitados.append(state_cls)
        return state_cls(_reflex_internal_init=True)

    monkeypatch.setattr(AuthState, "_revalidar", revalidar)
    monkeypatch.setattr(AuthState, "get_state", get_state)

    async def executar():
        gerador = AuthState.carregar_detalhe_chamado.fn(estado)
        assert await gerador.__anext__() is None
        return await gerador.__anext__()

    evento = asyncio.run(executar())

    assert estados_solicitados == [esperado]
    assert evento is None


@pytest.mark.parametrize("handler", [AuthState.carregar_inicio, AuthState.carregar_chamados])
@pytest.mark.parametrize(
    "perfil,usuario_id",
    [("tecnico", 9), ("diretoria", 18), ("administrador", 19), ("gerente", 20)],
)
def test_troca_real_de_sessao_nao_reutiliza_contexto_tecnico_nas_rotas_canonicas(
    monkeypatch, handler, perfil, usuario_id
):
    cliente = _ClienteFilaRastreado()
    monkeypatch.setattr(
        tecnico_module, "criar_cliente_service_desk", lambda: cliente
    )
    cliente_sessao = _ClienteSessaoAlternada(_identidade("tecnico", 9))
    monkeypatch.setattr(auth_module, "criar_cliente_xano", lambda: cliente_sessao)
    sessao = AuthState(_reflex_internal_init=True)
    fila = ChamadosTecnicoState(parent_state=sessao, _reflex_internal_init=True)
    gerente = ChamadosGerenteState(parent_state=sessao, _reflex_internal_init=True)

    _coletar(
        AuthState.login,
        sessao,
        {"email": "tecnico@example.test", "senha": "segredo"},
    )
    fila.numero_aplicado = 38
    _coletar(
        ChamadosTecnicoState.selecionar_escopo_rapido,
        fila,
        "atribuidos_a_mim",
    )
    assert cliente.consultas[-1][1]["somente_atribuidos_a_mim"] is True
    cliente.consultas.clear()

    AuthState.logout.fn(sessao)
    cliente_sessao.identidade = _identidade(perfil, usuario_id)
    _coletar(
        AuthState.login,
        sessao,
        {"email": f"{perfil}@example.test", "senha": "segredo"},
    )

    async def get_state(_self, state_cls):
        esperado = ChamadosGerenteState if perfil == "gerente" else ChamadosTecnicoState
        assert state_cls is esperado
        return gerente if perfil == "gerente" else fila

    monkeypatch.setattr(AuthState, "get_state", get_state)
    if perfil == "gerente":
        async def iniciar_apenas():
            gerador = handler.fn(sessao)
            primeiro = await gerador.__anext__()
            segundo = await gerador.__anext__()
            await gerador.aclose()
            return primeiro, segundo

        assert asyncio.run(iniciar_apenas()) == (None, None)
        assert cliente.consultas == []
    else:
        eventos = _coletar(handler, sessao)
        numero_esperado = 38 if perfil == "tecnico" else None
        assert eventos[0] is None
        assert cliente.consultas == [
            (
                f"token-{perfil}",
                {
                    "numero": numero_esperado,
                    "status": None,
                    "ativo_id": None,
                    "data_inicio": None,
                    "data_fim": None,
                    "somente_atribuidos_a_mim": False,
                },
            )
        ]
        assert fila.escopo_rapido == "todos"
        assert fila.numero_aplicado == numero_esperado

    assert cliente_sessao.chamadas == [
        ("login", "tecnico@example.test", "segredo"),
        ("me", "token-tecnico"),
        ("login", f"{perfil}@example.test", "segredo"),
        ("me", f"token-{perfil}"),
        ("me", f"token-{perfil}"),
    ]
    assert sessao._versao_sessao == 3


def test_aliases_de_detalhe_preservam_chamado_id_e_abertura_e_exclusiva_gerente(
    monkeypatch,
):
    gerente = _estado(
        ChamadosGerenteState, role="gerente", token="token", confirmado=True
    )
    object.__setattr__(gerente.router._page, "params", {"chamado_id": "42"})
    tecnico = _estado(
        ChamadosTecnicoState, role="tecnico", token="token", confirmado=True
    )
    object.__setattr__(tecnico.router._page, "params", {"chamado_id": "73"})

    async def gerente_autorizado(_):
        return None

    async def tecnico_autorizado(_):
        return None

    async def negar_gerente(_):
        return "/inicio"

    monkeypatch.setattr(ChamadosGerenteState, "_garantir_gerente", gerente_autorizado)
    monkeypatch.setattr(ChamadosTecnicoState, "_validar_acesso_fila", tecnico_autorizado)
    assert _destino(_coletar(ChamadosGerenteState.redirecionar_alias_detalhe, gerente)[-1]) == "/chamados/42"
    assert _destino(_coletar(ChamadosTecnicoState.redirecionar_alias_detalhe, tecnico)[-1]) == "/chamados/73"
    assert _destino(_coletar(ChamadosGerenteState.redirecionar_alias_novo, gerente)[-1]) == "/chamados/novo"

    global_state = _estado(
        ChamadosGerenteState, role="tecnico", token="token", confirmado=True
    )
    monkeypatch.setattr(ChamadosGerenteState, "_garantir_gerente", negar_gerente)
    assert _destino(_coletar(ChamadosGerenteState.redirecionar_alias_novo, global_state)[-1]) == "/inicio"


def test_alias_sem_sessao_exibe_estado_neutro_antes_do_login(monkeypatch):
    estado = _estado(ChamadosGerenteState)

    async def sem_sessao(_):
        return "/login"

    monkeypatch.setattr(ChamadosGerenteState, "_garantir_gerente", sem_sessao)

    eventos = _coletar(ChamadosGerenteState.redirecionar_alias_lista, estado)

    assert eventos[0] is None
    assert _destino(eventos[-1]) == "/login"


@pytest.mark.parametrize(
    "handler",
    [
        AuthState.carregar_inicio,
        AuthState.carregar_chamados,
        AuthState.carregar_detalhe_chamado,
    ],
)
def test_rotas_canonicas_de_chamados_sem_sessao_redirecionam_para_login(handler):
    estado = _estado(AuthState)

    eventos = _coletar(handler, estado)

    assert eventos[0] is None
    assert _destino(eventos[-1]) == "/login"


def test_abertura_e_administracao_canonicas_sem_sessao_redirecionam_para_login():
    gerente = _estado(ChamadosGerenteState)
    admin = _estado(AdministracaoState)

    abertura = _coletar(ChamadosGerenteState.carregar_formulario, gerente)
    administracao = _coletar(AdministracaoState.carregar_administracao, admin)

    assert _destino(abertura[-1]) == "/login"
    assert _destino(administracao[-1]) == "/login"


def test_alias_401_limpa_a_sessao_e_redireciona_para_login(monkeypatch):
    estado = _estado(
        ChamadosGerenteState, role="gerente", token="token", confirmado=True
    )

    async def expirado(self):
        self._limpar_sessao("Sua sessão expirou. Entre novamente.")
        return "/login"

    monkeypatch.setattr(ChamadosGerenteState, "_garantir_gerente", expirado)

    eventos = _coletar(ChamadosGerenteState.redirecionar_alias_lista, estado)

    assert estado.sessao_confirmada is False
    assert _destino(eventos[-1]) == "/login"


def test_pendencia_bloqueia_abertura_e_aliases_do_gerente_sem_chamar_cliente(
    monkeypatch,
):
    estado = _estado_direto(ChamadosGerenteState, role="gerente")

    def cliente_indevido():
        raise AssertionError("catálogo ou chamado não deve ser carregado")

    monkeypatch.setattr(
        "app.chamados.gerente.state.criar_cliente_service_desk", cliente_indevido
    )

    abertura = _coletar(ChamadosGerenteState.carregar_formulario, estado)
    lista = _coletar(ChamadosGerenteState.redirecionar_alias_lista, estado)
    novo = _coletar(ChamadosGerenteState.redirecionar_alias_novo, estado)
    detalhe = _coletar(ChamadosGerenteState.redirecionar_alias_detalhe, estado)

    for eventos in (abertura, lista, novo, detalhe):
        assert _destino(eventos[-1]) == "/primeiro-acesso"


@pytest.mark.parametrize("role", ["tecnico", "diretoria", "administrador"])
def test_pendencia_bloqueia_fila_e_aliases_globais_sem_chamar_cliente(
    monkeypatch, role
):
    estado = _estado_direto(ChamadosTecnicoState, role=role)

    def cliente_indevido():
        raise AssertionError("fila ou detalhe não deve ser carregado")

    monkeypatch.setattr(
        "app.chamados.tecnico.state.criar_cliente_service_desk", cliente_indevido
    )

    fila = _coletar(ChamadosTecnicoState.carregar_fila, estado)
    alias_fila = _coletar(ChamadosTecnicoState.redirecionar_alias_fila, estado)
    alias_detalhe = _coletar(
        ChamadosTecnicoState.redirecionar_alias_detalhe, estado
    )

    for eventos in (fila, alias_fila, alias_detalhe):
        assert _destino(eventos[-1]) == "/primeiro-acesso"


def test_alias_pendente_e_perfil_invalido_nao_expoem_jornada(monkeypatch):
    pendente = _estado(ChamadosGerenteState)
    invalido = _estado(ChamadosGerenteState)

    async def pendencia(self):
        return "/primeiro-acesso"

    async def perfil_invalido(self):
        return "/inicio"

    monkeypatch.setattr(ChamadosGerenteState, "_garantir_gerente", pendencia)
    assert _destino(_coletar(ChamadosGerenteState.redirecionar_alias_lista, pendente)[-1]) == "/primeiro-acesso"

    monkeypatch.setattr(ChamadosGerenteState, "_garantir_gerente", perfil_invalido)
    assert _destino(_coletar(ChamadosGerenteState.redirecionar_alias_lista, invalido)[-1]) == "/inicio"


def test_alias_403_preserva_sessao_e_redireciona_sem_conceder_acesso(monkeypatch):
    estado = _estado(
        ChamadosGerenteState, role="gerente", token="token", confirmado=True
    )

    async def revalidar_403(self, *_args):
        self.mensagem_erro = "Acesso não autorizado."
        return None

    monkeypatch.setattr(AuthState, "_revalidar", revalidar_403)

    async def revalidar_alias(self):
        return await self._revalidar()

    monkeypatch.setattr(ChamadosGerenteState, "_garantir_gerente", revalidar_alias)

    eventos = _coletar(ChamadosGerenteState.redirecionar_alias_lista, estado)

    assert estado.sessao_confirmada is True
    assert _destino(eventos[-1]) == "/chamados"


def test_alias_administrativo_e_diretoria_redirecionam_somente_perfis_autorizados(
    monkeypatch,
):
    admin = _estado(
        AdministracaoState, role="administrador", token="token", confirmado=True
    )
    diretoria = _estado(
        AuthState, role="diretoria", token="token", confirmado=True
    )

    async def guard_admin(self, *_args):
        yield None

    async def guard_diretoria(self, *_args):
        yield None

    monkeypatch.setattr(AdministracaoState, "_executar_guard", guard_admin)
    monkeypatch.setattr(AuthState, "_executar_guard", guard_diretoria)

    assert _destino(
        _coletar(AdministracaoState.redirecionar_alias_administracao, admin)[-1]
    ) == "/administracao/usuarios"
    assert _destino(_coletar(AuthState.redirecionar_alias_diretoria, diretoria)[-1]) == "/inicio"
