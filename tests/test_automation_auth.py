"""Regressões locais das credenciais técnicas de Fiscal e Simulator."""

import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
FISCAL_PATH = ROOT / "fiscal/fiscal.py"
SIMULATOR_PATH = ROOT / "simulator/simulator.py"
FISCAL_XS = ROOT / "xano/api/apis_from_table_telemetria_equipamentos/verificar_falhas_GET.xs"
SIMULATOR_XS = ROOT / "xano/api/apis_from_table_telemetria_equipamentos/telemetria_equipamentos_POST.xs"


def carregar_modulo(monkeypatch, caminho: Path, nome: str, ambiente: dict[str, str]):
    """Carrega um script com ambiente isolado para testar seus defaults."""

    for chave, valor in ambiente.items():
        monkeypatch.setenv(chave, valor)
    spec = importlib.util.spec_from_file_location(nome, caminho)
    modulo = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(modulo)
    return modulo


def ambiente_fiscal(**extra: str) -> dict[str, str]:
    return {
        "XANO_BASE_URL": "https://xano.example/api:operacional",
        "MIRA_FISCAL_AUTOMATION_KEY": "fiscal-segredo-de-teste",
        "FISCAL_INTERVAL_SECONDS": "300",
        "FISCAL_REQUEST_TIMEOUT_SECONDS": "30",
        **extra,
    }


def ambiente_simulator(**extra: str) -> dict[str, str]:
    return {
        "XANO_BASE_URL": "https://xano.example/api:operacional",
        "MIRA_SIMULATOR_AUTOMATION_KEY": "simulator-segredo-de-teste",
        "SIMULATOR_ATIVOS": "1,2",
        "SIMULATOR_INTERVAL_SECONDS": "300",
        "SIMULATOR_INTERVAL_BETWEEN_ASSETS": "3",
        **extra,
    }


class RespostaOk:
    ok = True
    status_code = 200
    text = "{}"

    def raise_for_status(self):
        return None

    def json(self):
        return {"success": True}


class RespostaErro:
    ok = False
    status_code = 401
    text = "fiscal-segredo-de-teste"

    def raise_for_status(self):
        raise RuntimeError("falha remota")


def test_fiscal_falha_sem_chave_antes_da_chamada(monkeypatch):
    fiscal = carregar_modulo(
        monkeypatch,
        FISCAL_PATH,
        "fiscal_sem_chave",
        ambiente_fiscal(MIRA_FISCAL_AUTOMATION_KEY=""),
    )
    chamadas = []
    monkeypatch.setattr(fiscal.requests, "get", lambda *args, **kwargs: chamadas.append(args))

    with pytest.raises(RuntimeError, match="MIRA_FISCAL_AUTOMATION_KEY"):
        fiscal.verificar_falhas()

    assert chamadas == []


def test_fiscal_envia_somente_header_dedicado_e_preserva_get(monkeypatch):
    fiscal = carregar_modulo(monkeypatch, FISCAL_PATH, "fiscal_valido", ambiente_fiscal())
    chamadas = []

    def get(url, **kwargs):
        chamadas.append((url, kwargs))
        return RespostaOk()

    monkeypatch.setattr(fiscal.requests, "get", get)

    assert fiscal.verificar_falhas() is True
    url, kwargs = chamadas[0]
    assert url == "https://xano.example/api:operacional/verificar-falhas"
    assert kwargs["headers"] == {"X-MIRA-Fiscal-Key": "fiscal-segredo-de-teste"}
    assert fiscal.INTERVALO_EXECUCAO_SEGUNDOS == 300


def test_fiscal_nao_registra_chave_em_resposta(monkeypatch, capsys):
    fiscal = carregar_modulo(monkeypatch, FISCAL_PATH, "fiscal_sem_vazamento", ambiente_fiscal())
    monkeypatch.setattr(fiscal.requests, "get", lambda *args, **kwargs: RespostaOk())

    fiscal.verificar_falhas()

    assert "fiscal-segredo-de-teste" not in capsys.readouterr().out


def test_fiscal_removeu_opcoes_de_diagnostico(monkeypatch):
    fiscal = carregar_modulo(monkeypatch, FISCAL_PATH, "fiscal_argumentos", ambiente_fiscal())
    monkeypatch.setattr(sys, "argv", ["fiscal.py", "--telemetria", "1"])

    with pytest.raises(SystemExit):
        fiscal.ler_argumentos()


def test_simulator_falha_sem_chave_antes_da_chamada(monkeypatch):
    simulator = carregar_modulo(
        monkeypatch,
        SIMULATOR_PATH,
        "simulator_sem_chave",
        ambiente_simulator(MIRA_SIMULATOR_AUTOMATION_KEY=""),
    )
    chamadas = []
    monkeypatch.setattr(simulator.requests, "post", lambda *args, **kwargs: chamadas.append(args))

    with pytest.raises(RuntimeError, match="MIRA_SIMULATOR_AUTOMATION_KEY"):
        simulator.enviar_telemetria({"ativos_referencia_id": 1})

    assert chamadas == []


def test_simulator_envia_somente_header_dedicado_e_preserva_post_payload(monkeypatch):
    simulator = carregar_modulo(
        monkeypatch, SIMULATOR_PATH, "simulator_valido", ambiente_simulator()
    )
    chamadas = []
    payload = {
        "ativos_referencia_id": 1,
        "uso_cpu": 42,
        "uso_memoria": 58,
        "temperatura": 31,
        "status_rede": "ONLINE",
        "evento_timestamp": 1_780_000_000_000,
    }

    def post(url, **kwargs):
        chamadas.append((url, kwargs))
        return RespostaOk()

    monkeypatch.setattr(simulator.requests, "post", post)

    assert simulator.enviar_telemetria(payload) == {"success": True}
    url, kwargs = chamadas[0]
    assert url == "https://xano.example/api:operacional/telemetria_equipamentos"
    assert kwargs["json"] == payload
    assert kwargs["headers"] == {
        "X-MIRA-Simulator-Key": "simulator-segredo-de-teste"
    }
    assert simulator.INTERVALO_CICLO_SEGUNDOS == 300
    assert simulator.INTERVALO_ENTRE_ATIVOS_SEGUNDOS == 3


def test_simulator_nao_registra_corpo_de_erro_com_chave(monkeypatch, capsys):
    simulator = carregar_modulo(
        monkeypatch, SIMULATOR_PATH, "simulator_sem_vazamento", ambiente_simulator()
    )
    monkeypatch.setattr(simulator.requests, "post", lambda *args, **kwargs: RespostaErro())

    with pytest.raises(RuntimeError, match="falha remota"):
        simulator.enviar_telemetria({"ativos_referencia_id": 1})

    saida = capsys.readouterr().out
    assert "simulator-segredo-de-teste" not in saida
    assert "fiscal-segredo-de-teste" not in saida


def test_simulator_separa_posts_por_intervalo_configuravel(monkeypatch):
    simulator = carregar_modulo(
        monkeypatch,
        SIMULATOR_PATH,
        "simulator_ciclo",
        ambiente_simulator(SIMULATOR_INTERVAL_BETWEEN_ASSETS="4"),
    )
    enviados = []
    esperas = []
    monkeypatch.setattr(
        simulator,
        "gerar_telemetria",
        lambda ativo_id: ({"ativos_referencia_id": ativo_id}, ["NORMAL"]),
    )
    monkeypatch.setattr(simulator, "enviar_telemetria", lambda payload: enviados.append(payload))
    monkeypatch.setattr(simulator.time, "sleep", esperas.append)

    simulator.executar_ciclo()

    assert enviados == [{"ativos_referencia_id": 1}, {"ativos_referencia_id": 2}]
    assert esperas == [4]


@pytest.mark.parametrize(
    ("fonte", "header", "segredo", "primeiro_db"),
    [
        (FISCAL_XS, "X-Mira-Fiscal-Key", "MIRA_FISCAL_AUTOMATION_KEY", "db.get categorias_servico"),
        (SIMULATOR_XS, "X-Mira-Simulator-Key", "MIRA_SIMULATOR_AUTOMATION_KEY", "db.get ativos_referencia"),
    ],
)
def test_guardas_xano_rejeitam_com_401_e_corpo_exato_antes_da_logica(
    fonte, header, segredo, primeiro_db
):
    conteudo = fonte.read_text(encoding="utf-8")

    assert f'$env.$http_headers|get:"{header}"' in conteudo
    assert f"$env.{segredo}" in conteudo
    assert 'value = "HTTP/1.1 401 Unauthorized\\nContent-Type: application/json"' in conteudo
    assert 'value = {error: "Não autenticado."}' in conteudo
    assert conteudo.index("util.set_header") < conteudo.index("return {")
    assert conteudo.index("return {") < conteudo.index(primeiro_db)
    assert '!= ""' in conteudo


def test_simulator_adia_presenca_do_payload_para_depois_do_guard():
    conteudo = SIMULATOR_XS.read_text(encoding="utf-8")

    for declaracao in (
        "int ativos_referencia_id?",
        "decimal uso_cpu?",
        "decimal uso_memoria?",
        "decimal temperatura?",
        "text status_rede?",
        "timestamp evento_timestamp?",
    ):
        assert declaracao in conteudo

    validacao = "precondition ($input.ativos_referencia_id != null"
    assert validacao in conteudo
    assert conteudo.index('value = {error: "Não autenticado."}') < conteudo.index(validacao)
    assert conteudo.index(validacao) < conteudo.index("db.get ativos_referencia")
    assert conteudo.index(validacao) < conteudo.index("db.add telemetria_equipamentos")

    for campo in (
        "ativos_referencia_id",
        "uso_cpu",
        "uso_memoria",
        "temperatura",
        "status_rede",
        "evento_timestamp",
    ):
        assert f"$input.{campo} != null" in conteudo


def test_credenciais_tecnicas_nao_sao_reutilizadas_em_endpoints_humanos():
    auth_sources = (ROOT / "xano/api/mira_auth").glob("*.xs")
    conteudo = "\n".join(arquivo.read_text(encoding="utf-8") for arquivo in auth_sources)

    assert "X-MIRA-Fiscal-Key" not in conteudo
    assert "X-MIRA-Simulator-Key" not in conteudo
