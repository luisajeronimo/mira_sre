"""Contrato HTTP e estado do dashboard de disponibilidade da Diretoria."""

import asyncio
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import httpx
import pytest

import app.indicadores.state as modulo_estado
from app.indicadores.contrato import ler_resultado
from app.indicadores.state import IndicadoresDiretoriaState
from app.services.service_desk import XanoServiceDeskCliente
from app.services.xano import XanoContratoInvalido, XanoIndisponivel
from app.states.auth import AuthState


BASE_URL = "https://xano.example/api:mira-service-desk"


def executar(corrotina):
    return asyncio.run(corrotina)


def executar_evento(handler, estado, *args):
    async def coletar():
        return [evento async for evento in handler.fn(estado, *args)]

    return executar(coletar())


def resposta(t0=1792000000000, t1=1792003600000, loja=None, totem=None):
    return {
        "periodo": {"t0": t0, "t1": t1, "fuso": "America/Sao_Paulo"},
        "filtros": {"lojas_id": loja, "ativos_referencia_id": totem},
        "disponibilidade": {
            "percentual": 94.10, "observado_ms": 93600000, "indisponivel_ms": 5520000,
            "totens_incluidos": 2, "totens_sem_observacao": 1, "totens_invalidos": 0,
        },
        "mttd": {"minutos": 19, "eventos": 2, "inconsistentes": 0},
        "mttr": {"minutos": 51, "recuperacoes": 2, "inconsistentes": 0, "abertas": 1},
        "serie": [{"dia": "2026-10-14", "mttd_minutos": 19, "mttr_minutos": 51,
                   "mttd_eventos": 2, "mttd_inconsistentes": 0,
                   "mttr_recuperacoes": 2, "mttr_inconsistentes": 0}],
    }


def resposta_horaria(t0, t1, loja=None, totem=None, observado_ate=None):
    dados = resposta(t0=t0, t1=t1, loja=loja, totem=totem)
    observado_ate = observado_ate or t0 + 12 * 3_600_000
    dados["disponibilidade_horaria"] = {
        "observado_ate": observado_ate,
        "pontos": [
            {"inicio": t0 + indice * 3_600_000, "fim": t0 + (indice + 1) * 3_600_000,
             "percentual": None, "observado_ms": 0, "indisponivel_ms": 0, "totens_invalidos": 0}
            for indice in range(24)
        ],
    }
    return dados


def test_visao_hoje_exige_24_horas_e_rejeita_dados_futuros():
    t0 = 1791946800000
    dados = resposta_horaria(t0, t0 + 86_400_000, observado_ate=t0 + 12 * 3_600_000)
    dados["disponibilidade_horaria"]["pontos"][0].update(percentual=100, observado_ms=3_600_000)
    resultado = ler_resultado(dados, visao="hoje")
    assert len(resultado.disponibilidade_horaria.pontos) == 24
    assert resultado.disponibilidade_horaria.pontos[0].percentual == 100
    with pytest.raises(XanoContratoInvalido):
        ler_resultado(resposta(t0=t0, t1=t0 + 86_400_000), visao="hoje")
    with pytest.raises(XanoContratoInvalido):
        ler_resultado(dados)
    dados["disponibilidade_horaria"]["pontos"][13].update(percentual=100, observado_ms=3_600_000)
    with pytest.raises(XanoContratoInvalido):
        ler_resultado(dados, visao="hoje")


def test_cliente_envia_filtros_e_le_resposta_tipificada():
    requisicoes = []

    def responder(requisicao):
        requisicoes.append(requisicao)
        if requisicao.url.path.endswith("/filtros"):
            return httpx.Response(200, json={"lojas": [{"id": 1, "nome": "Loja A"}],
                                             "totens": [{"id": 17, "nome": "Totem 17"}]})
        return httpx.Response(200, json=resposta(loja=1, totem=17))

    cliente = XanoServiceDeskCliente(BASE_URL, transport=httpx.MockTransport(responder))
    catalogo = executar(cliente.catalogo_indicadores_disponibilidade("token"))
    resultado = executar(cliente.consultar_indicadores_disponibilidade(
        "token", t0=1792000000000, t1=1792003600000, lojas_id=1, ativos_referencia_id=17
    ))

    assert catalogo.totens[0].id == 17
    assert resultado.disponibilidade.percentual == 94.1
    assert resultado.mttd.minutos == 19
    assert resultado.mttr.abertas == 1
    assert str(requisicoes[0].url) == f"{BASE_URL}/indicadores/disponibilidade-confiabilidade/filtros"
    assert dict(requisicoes[1].url.params) == {"t0": "1792000000000", "t1": "1792003600000", "lojas_id": "1", "ativos_referencia_id": "17"}


def test_cliente_envia_visao_hoje_e_exige_serie_horaria():
    t0 = 1791946800000
    t1 = t0 + 86_400_000
    requisicoes = []

    def responder(requisicao):
        requisicoes.append(requisicao)
        return httpx.Response(200, json=resposta_horaria(t0, t1))

    cliente = XanoServiceDeskCliente(BASE_URL, transport=httpx.MockTransport(responder))
    resultado = executar(cliente.consultar_indicadores_disponibilidade("token", t0=t0, t1=t1, visao="hoje"))
    assert resultado.disponibilidade_horaria is not None
    assert dict(requisicoes[0].url.params) == {"t0": str(t0), "t1": str(t1), "visao": "hoje"}


@pytest.mark.parametrize("alteracao", [
    lambda dados: dados["disponibilidade"].update(percentual=101),
    lambda dados: dados["mttd"].update(minutos=0),
    lambda dados: dados["serie"][0].update(mttd_eventos=0),
    lambda dados: dados["periodo"].update(fuso="UTC"),
])
def test_contrato_rejeita_resultado_incompatível(alteracao):
    dados = resposta()
    alteracao(dados)
    if dados["mttd"]["minutos"] == 0:
        dados["mttd"]["eventos"] = 0
    with pytest.raises(XanoContratoInvalido):
        ler_resultado(dados)


def novo_estado():
    return IndicadoresDiretoriaState(_reflex_internal_init=True)


def test_abas_alternam_visao_sem_apagar_filtros():
    estado = novo_estado()
    estado.loja_id = "2"
    estado.periodo_rapido = "hoje"
    estado.mostrar_periodo_personalizado = True
    IndicadoresDiretoriaState.selecionar_aba.fn(estado, "operacao")
    assert estado.aba_ativa == "operacao"
    assert estado.loja_id == "2"
    assert estado.periodo_rapido == "hoje"
    assert estado.mostrar_periodo_personalizado is False
    IndicadoresDiretoriaState.selecionar_aba.fn(estado, "invalida")
    assert estado.aba_ativa == "operacao"


def test_apresentacao_em_horas_e_tabela_do_mais_recente_para_o_mais_antigo():
    dados = resposta()
    dados["serie"].append({**dados["serie"][0], "dia": "2026-10-15", "mttd_minutos": 30})
    estado = novo_estado()

    estado._apresentar(ler_resultado(dados))

    assert estado.mttd_texto == "0.32 h"
    assert estado.mttr_texto == "0.85 h"
    assert estado.disponibilidade_tempo == "26.00 h observadas · 1.53 h indisponíveis"
    assert [ponto["dia"] for ponto in estado.serie] == ["2026-10-14", "2026-10-15"]
    assert [ponto["dia"] for ponto in estado.serie_tabela] == ["2026-10-15", "2026-10-14"]
    assert estado.serie[0]["mttd_horas"] == pytest.approx(19 / 60, abs=0.0001)


def test_apresentacao_de_hoje_preserva_horas_futuras_sem_valor():
    t0 = 1791946800000
    dados = resposta_horaria(t0, t0 + 86_400_000, observado_ate=t0 + 12 * 3_600_000)
    dados["disponibilidade_horaria"]["pontos"][0].update(percentual=100, observado_ms=3_600_000)
    estado = novo_estado()

    estado._apresentar(ler_resultado(dados, visao="hoje"))

    assert estado.periodo_texto == "14/10/2026 00:00 até 14/10/2026 23:59 · observado até 12:00"
    assert estado.serie_horaria[0] == {"hora": "00h", "percentual": 100.0, "percentual_texto": "100.00%"}
    assert estado.serie_horaria[23] == {"hora": "23h", "percentual": None, "percentual_texto": "Sem dados"}
    assert len(estado.serie) == 1


def test_periodo_inicial_tem_30_dias_civis():
    estado = novo_estado()
    estado._inicializar_periodo()
    assert (date.fromisoformat(estado.data_fim) - date.fromisoformat(estado.data_inicio)).days == 29
    t0, t1, loja, totem = estado._limites()
    assert loja is None and totem is None
    assert datetime.fromtimestamp(t0 / 1000, ZoneInfo("America/Sao_Paulo")).hour == 0
    assert t1 <= int(datetime.now().timestamp() * 1000)


def test_atalhos_de_periodo_consultam_ao_clique_e_preservam_recortes(monkeypatch):
    estado = novo_estado()
    estado._inicializar_periodo()
    estado.loja_id = "1"
    estado.totem_id = "17"
    object.__setattr__(estado, "_auth_token", "token")
    consultas = []

    async def acesso_autorizado(_estado):
        return None

    class ClienteConhecido:
        async def consultar_indicadores_disponibilidade(self, token, **filtros):
            consultas.append(filtros)
            dados = (resposta_horaria if filtros["visao"] == "hoje" else resposta)(
                t0=filtros["t0"], t1=filtros["t1"],
                loja=filtros["lojas_id"], totem=filtros["ativos_referencia_id"],
            )
            return ler_resultado(dados, visao=filtros["visao"])

    monkeypatch.setattr(IndicadoresDiretoriaState, "_validar_acesso", acesso_autorizado)
    monkeypatch.setattr(modulo_estado, "criar_cliente_service_desk", ClienteConhecido)

    antes = datetime.now(ZoneInfo("America/Sao_Paulo"))
    executar_evento(IndicadoresDiretoriaState.selecionar_periodo_rapido, estado, "hoje")
    assert estado.periodo_rapido == "hoje"
    assert len(consultas) == 1
    assert consultas[0]["lojas_id"] == 1
    assert consultas[0]["ativos_referencia_id"] == 17
    inicio_hoje = datetime.fromtimestamp(consultas[0]["t0"] / 1000, ZoneInfo("America/Sao_Paulo"))
    assert (inicio_hoje.date(), inicio_hoje.hour) == (antes.date(), 0)
    assert consultas[0]["t1"] == int((inicio_hoje + timedelta(days=1)).timestamp() * 1000)
    assert consultas[0]["visao"] == "hoje"
    assert len(estado.serie_horaria) == 24

    executar_evento(IndicadoresDiretoriaState.selecionar_periodo_rapido, estado, "30_dias")
    assert estado.periodo_rapido == "30_dias"
    assert len(consultas) == 2
    inicio_30_dias = datetime.fromtimestamp(consultas[1]["t0"] / 1000, ZoneInfo("America/Sao_Paulo"))
    assert (antes.date() - inicio_30_dias.date()).days == 29
    assert consultas[1]["lojas_id"] == 1
    assert consultas[1]["ativos_referencia_id"] == 17
    assert consultas[1]["visao"] is None

    IndicadoresDiretoriaState.alterar_data_inicio.fn(estado, "2026-10-01")
    assert estado.periodo_rapido == "30_dias"
    assert estado.datas_personalizadas_pendentes is True
    executar_evento(IndicadoresDiretoriaState.aplicar_filtros, estado)
    assert estado.periodo_rapido == "personalizado"
    assert len(consultas) == 3
    inicio_personalizado = datetime.fromtimestamp(consultas[2]["t0"] / 1000, ZoneInfo("America/Sao_Paulo"))
    assert inicio_personalizado.date().isoformat() == "2026-10-01"


def test_periodo_futuro_e_invertido_sao_rejeitados():
    estado = novo_estado()
    estado.data_inicio = "2026-11-12"
    estado.data_fim = "2026-11-11"
    with pytest.raises(ValueError):
        estado._limites()
    estado.data_inicio = "2026-11-11"
    estado.data_fim = (date.today() + timedelta(days=2)).isoformat()
    with pytest.raises(ValueError):
        estado._limites()


def test_falha_ao_aplicar_limpa_resultado_anterior(monkeypatch):
    estado = novo_estado()
    estado._inicializar_periodo()
    estado.tem_resultado = True
    estado.disponibilidade_texto = "94,10%"
    object.__setattr__(estado, "_auth_token", "token")

    async def acesso_autorizado(_estado):
        return None

    class ClienteIndisponivel:
        async def consultar_indicadores_disponibilidade(self, *args, **kwargs):
            raise XanoIndisponivel("falha")

    monkeypatch.setattr(IndicadoresDiretoriaState, "_validar_acesso", acesso_autorizado)
    monkeypatch.setattr(modulo_estado, "criar_cliente_service_desk", ClienteIndisponivel)
    executar_evento(IndicadoresDiretoriaState.aplicar_filtros, estado)

    assert estado.tem_resultado is False
    assert estado.disponibilidade_texto == "—"
    assert estado.mensagem_erro_indicadores


def test_state_apresenta_apenas_agregados_retornados_pelo_xano(monkeypatch):
    estado = novo_estado()
    estado._inicializar_periodo()
    object.__setattr__(estado, "_auth_token", "token")
    class ClienteConhecido:
        async def consultar_indicadores_disponibilidade(self, token, **filtros):
            assert token == "token"
            assert filtros["lojas_id"] is None and filtros["ativos_referencia_id"] is None
            return ler_resultado(resposta(t0=filtros["t0"], t1=filtros["t1"]))

    async def acesso_autorizado(_estado):
        return None

    monkeypatch.setattr(IndicadoresDiretoriaState, "_validar_acesso", acesso_autorizado)
    monkeypatch.setattr(modulo_estado, "criar_cliente_service_desk", ClienteConhecido)
    executar_evento(IndicadoresDiretoriaState.aplicar_filtros, estado)

    assert estado.tem_resultado is True
    assert estado.disponibilidade_texto == "94.10%"
    assert estado.totens_observados_texto == "2"
    assert estado.totens_qualidade_texto == "1 sem observação · 0 históricos inválidos"
    assert estado.mttd_texto == "0.32 h"
    assert estado.mttr_texto == "0.85 h"
    assert estado.serie[0]["mttd_horas"] == pytest.approx(19 / 60, abs=0.0001)
    assert estado.carregando_indicadores is False


def test_resposta_de_filtro_diferente_nao_aparece(monkeypatch):
    estado = novo_estado()
    estado._inicializar_periodo()
    object.__setattr__(estado, "_auth_token", "token")

    class ClienteIncoerente:
        async def consultar_indicadores_disponibilidade(self, token, **filtros):
            return ler_resultado(resposta(t0=filtros["t0"], t1=filtros["t1"], loja=2))

    async def acesso_autorizado(_estado):
        return None

    monkeypatch.setattr(IndicadoresDiretoriaState, "_validar_acesso", acesso_autorizado)
    monkeypatch.setattr(modulo_estado, "criar_cliente_service_desk", ClienteIncoerente)
    executar_evento(IndicadoresDiretoriaState.aplicar_filtros, estado)

    assert estado.tem_resultado is False
    assert estado.mensagem_erro_indicadores == "A resposta dos indicadores é incompatível."


@pytest.mark.parametrize("perfil, autorizado", [
    ("diretoria", True),
    ("gerente", False),
    ("tecnico", False),
    ("administrador", False),
])
def test_acesso_direto_da_rota_respeita_perfil(monkeypatch, perfil, autorizado):
    estado = IndicadoresDiretoriaState(
        parent_state=AuthState(_reflex_internal_init=True),
        _reflex_internal_init=True,
    )
    estado.role = perfil
    estado.sessao_confirmada = True

    async def revalidacao(_estado):
        return None

    monkeypatch.setattr(IndicadoresDiretoriaState, "_revalidar", revalidacao)
    assert executar(estado._validar_acesso()) == (None if autorizado else "/inicio")
