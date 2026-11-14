"""Contrato de leitura dos agregados de causas e recorrência calculados no Xano."""

from dataclasses import dataclass
from typing import Any

from app.indicadores.contrato import OpcaoIndicador, _inteiro, _numero, _objeto, _opcoes
from app.services.xano import XanoContratoInvalido


@dataclass(frozen=True, slots=True)
class CatalogoCausas:
    lojas: list[OpcaoIndicador]
    totens: list[OpcaoIndicador]
    categorias: list[OpcaoIndicador]


@dataclass(frozen=True, slots=True)
class ResultadoCausas:
    t0: int
    t1: int
    observado_ate: int
    lojas_id: int | None
    ativos_referencia_id: int | None
    categorias_servico_id: int | None
    base: dict[str, int]
    top_lojas: list[dict[str, Any]]
    pareto: list[dict[str, Any]]
    categorias_80: int
    recorrentes: int
    percentual: float | None
    por_loja: list[dict[str, Any]]
    por_totem: list[dict[str, Any]]


def ler_catalogo_causas(dados: Any) -> CatalogoCausas:
    d = _objeto(dados, "catálogo de causas", {"lojas", "totens", "categorias"})
    return CatalogoCausas(*(_opcoes(d[campo], campo) for campo in ("lojas", "totens", "categorias")))


def _linhas(dados: Any, nome: str, campos: set[str]) -> list[dict[str, Any]]:
    if not isinstance(dados, list):
        raise XanoContratoInvalido(f"Resposta inválida: {nome}.")
    vistos = set()
    for linha in dados:
        _objeto(linha, nome, campos | {"id", "nome"})
        identificador = _inteiro(linha["id"], nome + ".id", positivo=True)
        if identificador in vistos or not isinstance(linha["nome"], str) or not linha["nome"].strip():
            raise XanoContratoInvalido(f"Resposta inválida: {nome}.")
        vistos.add(identificador)
    return dados


def ler_resultado_causas(dados: Any) -> ResultadoCausas:
    d = _objeto(dados, "causas", {"periodo", "filtros", "base", "top_lojas", "pareto", "recorrencia"})
    p = _objeto(d["periodo"], "periodo", {"t0", "t1", "observado_ate", "fuso"})
    t0, t1, observado = (_inteiro(p[c], c, positivo=True) for c in ("t0", "t1", "observado_ate"))
    if not t0 < observado <= t1 or p["fuso"] != "America/Sao_Paulo":
        raise XanoContratoInvalido("Resposta inválida: periodo.")
    f = _objeto(d["filtros"], "filtros", {"lojas_id", "ativos_referencia_id", "categorias_servico_id"})
    filtros = [None if f[c] is None else _inteiro(f[c], c, positivo=True) for c in ("lojas_id", "ativos_referencia_id", "categorias_servico_id")]
    base = _objeto(d["base"], "base", {"elegiveis", "cancelados", "requisicoes", "inconsistentes", "sem_data", "sem_loja"})
    for campo, valor in base.items():
        _inteiro(valor, "base." + campo)
    if base["sem_loja"] > base["elegiveis"]:
        raise XanoContratoInvalido("Resposta inválida: base.sem_loja.")
    top = _linhas(d["top_lojas"], "top_lojas", {"quantidade"})
    if len(top) > 5:
        raise XanoContratoInvalido("Resposta inválida: top_lojas.")
    for linha in top:
        _inteiro(linha["quantidade"], "top.quantidade", positivo=True)
    if top != sorted(top, key=lambda x: (-x["quantidade"], x["id"])):
        raise XanoContratoInvalido("Resposta inválida: ordem do Top 5.")
    pareto = _objeto(d["pareto"], "pareto", {"categorias", "categorias_80"})
    causas = _linhas(pareto["categorias"], "pareto", {"quantidade", "percentual", "acumulado_percentual", "destaque_80"})
    categorias_80 = _inteiro(pareto["categorias_80"], "categorias_80")
    for linha in causas:
        _inteiro(linha["quantidade"], "pareto.quantidade", positivo=True)
        for campo in ("percentual", "acumulado_percentual"):
            if _numero(linha[campo], campo, maximo=100) is None:
                raise XanoContratoInvalido("Resposta inválida: percentual de Pareto.")
        if not isinstance(linha["destaque_80"], bool):
            raise XanoContratoInvalido("Resposta inválida: destaque_80.")
    if (sum(x["quantidade"] for x in causas) != base["elegiveis"]
            or causas != sorted(causas, key=lambda x: (-x["quantidade"], x["id"]))
            or categorias_80 != sum(x["destaque_80"] for x in causas)):
        raise XanoContratoInvalido("Resposta inválida: base do Pareto.")
    r = _objeto(d["recorrencia"], "recorrencia", {"janela_dias", "elegiveis", "recorrentes", "percentual", "por_loja", "por_totem"})
    elegiveis = _inteiro(r["elegiveis"], "recorrencia.elegiveis")
    recorrentes = _inteiro(r["recorrentes"], "recorrencia.recorrentes")
    percentual = _numero(r["percentual"], "recorrencia.percentual", maximo=100)
    if r["janela_dias"] != 30 or elegiveis != base["elegiveis"] or recorrentes > elegiveis or (percentual is None) != (elegiveis == 0):
        raise XanoContratoInvalido("Resposta inválida: recorrencia.")
    segmentos = []
    for campo in ("por_loja", "por_totem"):
        linhas = _linhas(r[campo], campo, {"elegiveis", "recorrentes", "percentual"})
        for linha in linhas:
            n = _inteiro(linha["elegiveis"], campo, positivo=True)
            if _inteiro(linha["recorrentes"], campo) > n or _numero(linha["percentual"], campo, maximo=100) is None:
                raise XanoContratoInvalido(f"Resposta inválida: {campo}.")
        segmentos.append(linhas)
    if (sum(x["elegiveis"] for x in segmentos[0]) + base["sem_loja"] != elegiveis
            or sum(x["elegiveis"] for x in segmentos[1]) != elegiveis
            or sum(x["recorrentes"] for x in segmentos[1]) != recorrentes):
        raise XanoContratoInvalido("Resposta inválida: bases dos detalhamentos.")
    return ResultadoCausas(t0, t1, observado, *filtros, dict(base), top, causas, categorias_80, recorrentes, percentual, *segmentos)
