"""Contrato tipado da volumetria e dos indicadores executivos de SLA."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.indicadores.contrato import OpcaoIndicador, _inteiro, _numero, _objeto, _opcoes
from app.services.xano import XanoContratoInvalido


STATUS_CHAMADO = (
    "Novo", "Em Atendimento", "Aguardando Solicitante", "Aguardando Mudança",
    "Resolvido", "Solução Rejeitada", "Encerrado", "Cancelado",
)


@dataclass(frozen=True, slots=True)
class CatalogoOperacao:
    lojas: list[OpcaoIndicador]
    categorias: list[OpcaoIndicador]


@dataclass(frozen=True, slots=True)
class StatusVolume:
    status: str
    quantidade: int


@dataclass(frozen=True, slots=True)
class Volumetria:
    total: int
    por_status: list[StatusVolume]
    nao_classificados: int


@dataclass(frozen=True, slots=True)
class Conformidade:
    percentual: float | None
    cumpriram: int
    elegiveis: int
    cancelados: int
    nao_calculaveis: int


@dataclass(frozen=True, slots=True)
class RiscoAtual:
    calculado_em: int
    normal: int
    risco: int
    critico: int
    violado: int
    nao_calculaveis: int
    status_nao_canonicos: int


@dataclass(frozen=True, slots=True)
class ResultadoOperacao:
    t0: int
    t1: int
    observado_ate: int
    lojas_id: int | None
    categorias_servico_id: int | None
    volumetria: Volumetria
    conformidade: Conformidade
    risco: RiscoAtual
    chamados_filtrados: int


def ler_catalogo_operacao(dados: Any) -> CatalogoOperacao:
    objeto = _objeto(dados, "catálogo de operação", {"lojas", "categorias"})
    return CatalogoOperacao(_opcoes(objeto["lojas"], "lojas"), _opcoes(objeto["categorias"], "categorias"))


def ler_resultado_operacao(dados: Any) -> ResultadoOperacao:
    objeto = _objeto(dados, "operação", {"periodo", "filtros", "volumetria", "conformidade", "risco", "chamados_filtrados"})
    periodo = _objeto(objeto["periodo"], "periodo", {"t0", "t1", "observado_ate", "fuso"})
    t0 = _inteiro(periodo["t0"], "periodo.t0", positivo=True)
    t1 = _inteiro(periodo["t1"], "periodo.t1", positivo=True)
    observado_ate = _inteiro(periodo["observado_ate"], "periodo.observado_ate", positivo=True)
    if periodo["fuso"] != "America/Sao_Paulo" or not t0 < observado_ate <= t1:
        raise XanoContratoInvalido("Resposta inválida: periodo.")

    filtros = _objeto(objeto["filtros"], "filtros", {"lojas_id", "categorias_servico_id"})
    loja = None if filtros["lojas_id"] is None else _inteiro(filtros["lojas_id"], "filtros.lojas_id", positivo=True)
    categoria = None if filtros["categorias_servico_id"] is None else _inteiro(filtros["categorias_servico_id"], "filtros.categorias_servico_id", positivo=True)

    volume_dados = _objeto(objeto["volumetria"], "volumetria", {"total", "por_status", "nao_classificados"})
    total = _inteiro(volume_dados["total"], "volumetria.total")
    nao_classificados = _inteiro(volume_dados["nao_classificados"], "volumetria.nao_classificados")
    itens = volume_dados["por_status"]
    if not isinstance(itens, list) or len(itens) != len(STATUS_CHAMADO):
        raise XanoContratoInvalido("Resposta inválida: volumetria.por_status.")
    por_status: list[StatusVolume] = []
    for esperado, item in zip(STATUS_CHAMADO, itens):
        ponto = _objeto(item, "volumetria.status", {"status", "quantidade"})
        if ponto["status"] != esperado:
            raise XanoContratoInvalido("Resposta inválida: volumetria.status.")
        por_status.append(StatusVolume(esperado, _inteiro(ponto["quantidade"], "volumetria.quantidade")))
    if total != nao_classificados + sum(item.quantidade for item in por_status):
        raise XanoContratoInvalido("Resposta inválida: volumetria.total.")
    volumetria = Volumetria(total, por_status, nao_classificados)

    conf = _objeto(objeto["conformidade"], "conformidade", {"percentual", "cumpriram", "elegiveis", "cancelados", "nao_calculaveis"})
    conformidade = Conformidade(
        _numero(conf["percentual"], "conformidade.percentual", maximo=100),
        _inteiro(conf["cumpriram"], "conformidade.cumpriram"),
        _inteiro(conf["elegiveis"], "conformidade.elegiveis"),
        _inteiro(conf["cancelados"], "conformidade.cancelados"),
        _inteiro(conf["nao_calculaveis"], "conformidade.nao_calculaveis"),
    )
    if conformidade.cumpriram > conformidade.elegiveis or (conformidade.percentual is None) != (conformidade.elegiveis == 0):
        raise XanoContratoInvalido("Resposta inválida: conformidade.")

    risco_dados = _objeto(objeto["risco"], "risco", {"calculado_em", "normal", "risco", "critico", "violado", "nao_calculaveis", "status_nao_canonicos"})
    risco = RiscoAtual(
        _inteiro(risco_dados["calculado_em"], "risco.calculado_em", positivo=True),
        _inteiro(risco_dados["normal"], "risco.normal"),
        _inteiro(risco_dados["risco"], "risco.risco"),
        _inteiro(risco_dados["critico"], "risco.critico"),
        _inteiro(risco_dados["violado"], "risco.violado"),
        _inteiro(risco_dados["nao_calculaveis"], "risco.nao_calculaveis"),
        _inteiro(risco_dados["status_nao_canonicos"], "risco.status_nao_canonicos"),
    )
    if risco.calculado_em < observado_ate:
        raise XanoContratoInvalido("Resposta inválida: risco.calculado_em.")

    return ResultadoOperacao(t0, t1, observado_ate, loja, categoria, volumetria, conformidade, risco, _inteiro(objeto["chamados_filtrados"], "chamados_filtrados"))
