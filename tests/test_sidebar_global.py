"""Regressões da sidebar global por perfil e do monitoramento dedicado."""

import asyncio
from pathlib import Path

import httpx
import pytest

from app.components.navegacao import ITENS_NAVEGACAO, item_esta_ativo, itens_visiveis
from app.monitoramento.state import MonitoramentoState
from app.services.service_desk import XanoServiceDeskCliente
from app.states.auth import AuthState


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://xano.example/api:mira-service-desk"


def executar(corrotina):
    return asyncio.run(corrotina)


def novo_estado() -> MonitoramentoState:
    return MonitoramentoState(_reflex_internal_init=True)


@pytest.mark.parametrize(
    ("perfil", "rotas", "rotulos"),
    [
        ("gerente", ["/inicio"], ["Início"]),
        ("tecnico", ["/inicio", "/monitoramento"], ["Início", "Monitoramento"]),
        ("diretoria", ["/inicio", "/monitoramento"], ["Início", "Monitoramento"]),
        (
            "administrador",
            ["/inicio", "/monitoramento", "/administracao/usuarios"],
            ["Início", "Monitoramento", "Administração de usuários"],
        ),
    ],
)
def test_matriz_central_de_navegacao_por_perfil(perfil, rotas, rotulos):
    itens = itens_visiveis(perfil)

    assert [item.rota for item in itens] == rotas
    assert [item.rotulo for item in itens] == rotulos


def test_perfil_nao_oficial_nao_recebe_destinos_de_navegacao():
    assert itens_visiveis("admin") == ()
    assert itens_visiveis("") == ()


def test_inicio_permanece_ativo_na_jornada_canonica_de_chamados():
    rotas = [item.rota for item in ITENS_NAVEGACAO]

    assert "/chamados" not in rotas
    assert "/chamados/novo" not in rotas
    assert "/chamados/[chamado_id]" not in rotas
    inicio = next(item for item in ITENS_NAVEGACAO if item.rota == "/inicio")
    for rota in ("/inicio", "/chamados", "/chamados/novo", "/chamados/[chamado_id]"):
        assert item_esta_ativo(inicio, rota) is True


def test_monitoramento_e_administracao_so_ativam_nas_rotas_configuradas():
    inicio, monitoramento, administracao = ITENS_NAVEGACAO

    assert item_esta_ativo(monitoramento, "/monitoramento") is True
    assert item_esta_ativo(administracao, "/administracao/usuarios") is True
    for rota in ("/inicio", "/chamados", "/chamados/novo", "/chamados/[chamado_id]"):
        assert item_esta_ativo(monitoramento, rota) is False
        assert item_esta_ativo(administracao, rota) is False
    assert item_esta_ativo(inicio, "/monitoramento") is False
    assert item_esta_ativo(inicio, "/administracao/usuarios") is False


def test_asset_do_logo_corresponde_exatamente_a_referencia_oficial():
    assert (ROOT / "assets/mira-logo.svg").read_bytes() == (
        ROOT / "docs/design/references/logo.svg"
    ).read_bytes()


def test_casca_reutiliza_asset_oficial_em_sidebar_desktop_sem_drawer():
    fonte = (ROOT / "app/components/layout.py").read_text(encoding="utf-8")
    app_fonte = (ROOT / "app/app.py").read_text(encoding="utf-8")

    assert 'src="/mira-logo.svg"' in fonte
    assert "on_click=AuthState.logout" in fonte
    assert "_focus_visible" in fonte
    assert "_sidebar_desktop" in fonte
    assert "rx.drawer" not in fonte
    assert "rx.breakpoints" not in fonte
    assert 'accent_color="ruby"' in app_fonte


def test_cliente_de_monitoramento_usa_contrato_dedicado():
    requisicoes = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "id": 1,
                        "nome_ativo": "Totem 01",
                        "tipo": "Totem",
                        "status_atual": "online",
                    }
                ]
            },
        )

    cliente = XanoServiceDeskCliente(
        BASE_URL, transport=httpx.MockTransport(responder)
    )
    ativos = executar(cliente.listar_ativos_monitoramento("token"))

    assert ativos[0].nome_ativo == "Totem 01"
    assert str(requisicoes[0].url) == f"{BASE_URL}/monitoramento/ativos"
    assert requisicoes[0].headers["Authorization"] == "Bearer token"


def test_gerente_e_redirecionado_sem_iniciar_consulta_de_monitoramento(monkeypatch):
    estado = novo_estado()
    object.__setattr__(estado, "sessao_confirmada", True)
    object.__setattr__(estado, "role", "gerente")

    async def revalidar(_estado):
        return None

    monkeypatch.setattr(MonitoramentoState, "_revalidar", revalidar)

    assert executar(estado._validar_acesso_monitoramento()) == "/inicio"


def test_xanoscript_dedicado_preserva_o_endpoint_generico_e_cobre_autorizacao():
    funcao = (
        ROOT / "xano/function/service_desk/listar_ativos_monitoramento.xs"
    ).read_text(encoding="utf-8")
    endpoint = (
        ROOT / "xano/api/mira_service_desk/monitoramento/ativos_GET.xs"
    ).read_text(encoding="utf-8")
    generico = (
        ROOT / "xano/api/apis_from_table_ativos_referencia/ativos_referencia_GET.xs"
    ).read_text(encoding="utf-8")

    assert 'function.run "autorizacao/exigir_perfil"' in funcao
    assert "tecnico: true" in funcao
    assert "diretoria: true" in funcao
    assert "administrador: true" in funcao
    assert 'test "gerente nao consulta monitoramento"' in funcao
    assert 'query "monitoramento/ativos" verb=GET' in endpoint
    assert 'auth = "usuarios"' in endpoint
    assert 'query ativos_referencia verb=GET' in generico
