"""Validação dos resultados executivos calculados pelo Xano."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import Any

from app.services.xano import XanoContratoInvalido


@dataclass(frozen=True, slots=True)
class OpcaoIndicador:
    id: int
    nome: str


@dataclass(frozen=True, slots=True)
class CatalogoIndicadores:
    lojas: list[OpcaoIndicador]
    totens: list[OpcaoIndicador]


@dataclass(frozen=True, slots=True)
class DisponibilidadeIndicador:
    percentual: float | None
    observado_ms: int
    indisponivel_ms: int
    totens_incluidos: int
    totens_sem_observacao: int
    totens_invalidos: int


@dataclass(frozen=True, slots=True)
class MediaIndicador:
    minutos: float | None
    eventos: int
    inconsistentes: int
    abertas: int = 0


@dataclass(frozen=True, slots=True)
class PontoConfiabilidade:
    dia: str
    mttd_minutos: float | None
    mttr_minutos: float | None
    mttd_eventos: int
    mttd_inconsistentes: int
    mttr_recuperacoes: int
    mttr_inconsistentes: int


@dataclass(frozen=True, slots=True)
class PontoDisponibilidadeHoraria:
    inicio: int
    fim: int
    percentual: float | None
    observado_ms: int
    indisponivel_ms: int
    totens_invalidos: int


@dataclass(frozen=True, slots=True)
class DisponibilidadeHoraria:
    observado_ate: int
    pontos: list[PontoDisponibilidadeHoraria]


@dataclass(frozen=True, slots=True)
class ResultadoConfiabilidade:
    t0: int
    t1: int
    lojas_id: int | None
    ativos_referencia_id: int | None
    disponibilidade: DisponibilidadeIndicador
    mttd: MediaIndicador
    mttr: MediaIndicador
    serie: list[PontoConfiabilidade]
    disponibilidade_horaria: DisponibilidadeHoraria | None = None


def _objeto(valor: Any, nome: str, campos: set[str]) -> dict[str, Any]:
    if not isinstance(valor, dict) or set(valor) != campos:
        raise XanoContratoInvalido(f"Resposta inválida: {nome}.")
    return valor


def _inteiro(valor: Any, nome: str, *, positivo: bool = False) -> int:
    if not isinstance(valor, int) or isinstance(valor, bool) or valor < (1 if positivo else 0):
        raise XanoContratoInvalido(f"Resposta inválida: {nome}.")
    return valor


def _numero(valor: Any, nome: str, *, maximo: float | None = None) -> float | None:
    if valor is None:
        return None
    if not isinstance(valor, (int, float)) or isinstance(valor, bool) or valor < 0:
        raise XanoContratoInvalido(f"Resposta inválida: {nome}.")
    convertido = float(valor)
    if not isfinite(convertido) or (maximo is not None and convertido > maximo):
        raise XanoContratoInvalido(f"Resposta inválida: {nome}.")
    return convertido


def _opcoes(valor: Any, nome: str) -> list[OpcaoIndicador]:
    if not isinstance(valor, list):
        raise XanoContratoInvalido(f"Resposta inválida: {nome}.")
    resultado: list[OpcaoIndicador] = []
    for item in valor:
        dados = _objeto(item, nome, {"id", "nome"})
        nome_item = dados["nome"]
        if not isinstance(nome_item, str) or not nome_item.strip():
            raise XanoContratoInvalido(f"Resposta inválida: {nome}.nome.")
        resultado.append(OpcaoIndicador(_inteiro(dados["id"], f"{nome}.id", positivo=True), nome_item))
    return resultado


def ler_catalogo(dados: Any) -> CatalogoIndicadores:
    objeto = _objeto(dados, "catálogo", {"lojas", "totens"})
    return CatalogoIndicadores(_opcoes(objeto["lojas"], "lojas"), _opcoes(objeto["totens"], "totens"))


def ler_resultado(dados: Any, *, visao: str | None = None) -> ResultadoConfiabilidade:
    if visao not in (None, "hoje"):
        raise XanoContratoInvalido("Visão inválida.")
    campos = {"periodo", "filtros", "disponibilidade", "mttd", "mttr", "serie"}
    if visao == "hoje":
        campos.add("disponibilidade_horaria")
    objeto = _objeto(dados, "indicadores", campos)
    periodo = _objeto(objeto["periodo"], "periodo", {"t0", "t1", "fuso"})
    t0 = _inteiro(periodo["t0"], "periodo.t0", positivo=True)
    t1 = _inteiro(periodo["t1"], "periodo.t1", positivo=True)
    if t0 >= t1 or periodo["fuso"] != "America/Sao_Paulo":
        raise XanoContratoInvalido("Resposta inválida: periodo.")
    filtros = _objeto(objeto["filtros"], "filtros", {"lojas_id", "ativos_referencia_id"})
    lojas_id = None if filtros["lojas_id"] is None else _inteiro(filtros["lojas_id"], "filtros.lojas_id", positivo=True)
    ativos_id = None if filtros["ativos_referencia_id"] is None else _inteiro(filtros["ativos_referencia_id"], "filtros.ativos_referencia_id", positivo=True)

    disp = _objeto(objeto["disponibilidade"], "disponibilidade", {
        "percentual", "observado_ms", "indisponivel_ms", "totens_incluidos", "totens_sem_observacao", "totens_invalidos"
    })
    disponibilidade = DisponibilidadeIndicador(
        _numero(disp["percentual"], "disponibilidade.percentual", maximo=100),
        _inteiro(disp["observado_ms"], "disponibilidade.observado_ms"),
        _inteiro(disp["indisponivel_ms"], "disponibilidade.indisponivel_ms"),
        _inteiro(disp["totens_incluidos"], "disponibilidade.totens_incluidos"),
        _inteiro(disp["totens_sem_observacao"], "disponibilidade.totens_sem_observacao"),
        _inteiro(disp["totens_invalidos"], "disponibilidade.totens_invalidos"),
    )
    if bool(disponibilidade.totens_invalidos or not disponibilidade.observado_ms) != (disponibilidade.percentual is None):
        raise XanoContratoInvalido("Resposta inválida: disponibilidade.percentual.")
    if disponibilidade.indisponivel_ms > disponibilidade.observado_ms:
        raise XanoContratoInvalido("Resposta inválida: disponibilidade.indisponivel_ms.")

    mttd_dados = _objeto(objeto["mttd"], "mttd", {"minutos", "eventos", "inconsistentes"})
    mttr_dados = _objeto(objeto["mttr"], "mttr", {"minutos", "recuperacoes", "inconsistentes", "abertas"})
    mttd = MediaIndicador(_numero(mttd_dados["minutos"], "mttd.minutos"), _inteiro(mttd_dados["eventos"], "mttd.eventos"), _inteiro(mttd_dados["inconsistentes"], "mttd.inconsistentes"))
    mttr = MediaIndicador(_numero(mttr_dados["minutos"], "mttr.minutos"), _inteiro(mttr_dados["recuperacoes"], "mttr.recuperacoes"), _inteiro(mttr_dados["inconsistentes"], "mttr.inconsistentes"), _inteiro(mttr_dados["abertas"], "mttr.abertas"))
    if (mttd.eventos == 0) != (mttd.minutos is None) or (mttr.eventos == 0) != (mttr.minutos is None):
        raise XanoContratoInvalido("Resposta inválida: médias.")

    serie_bruta = objeto["serie"]
    if not isinstance(serie_bruta, list):
        raise XanoContratoInvalido("Resposta inválida: serie.")
    serie: list[PontoConfiabilidade] = []
    for item in serie_bruta:
        ponto = _objeto(item, "serie.ponto", {"dia", "mttd_minutos", "mttr_minutos", "mttd_eventos", "mttd_inconsistentes", "mttr_recuperacoes", "mttr_inconsistentes"})
        dia = ponto["dia"]
        if not isinstance(dia, str):
            raise XanoContratoInvalido("Resposta inválida: serie.dia.")
        try:
            date.fromisoformat(dia)
        except ValueError as exc:
            raise XanoContratoInvalido("Resposta inválida: serie.dia.") from exc
        mttd_q = _inteiro(ponto["mttd_eventos"], "serie.mttd_eventos")
        mttr_q = _inteiro(ponto["mttr_recuperacoes"], "serie.mttr_recuperacoes")
        mttd_v = _numero(ponto["mttd_minutos"], "serie.mttd_minutos")
        mttr_v = _numero(ponto["mttr_minutos"], "serie.mttr_minutos")
        if (mttd_q == 0) != (mttd_v is None) or (mttr_q == 0) != (mttr_v is None):
            raise XanoContratoInvalido("Resposta inválida: serie.ponto.")
        serie.append(PontoConfiabilidade(
            dia, mttd_v, mttr_v, mttd_q,
            _inteiro(ponto["mttd_inconsistentes"], "serie.mttd_inconsistentes"),
            mttr_q, _inteiro(ponto["mttr_inconsistentes"], "serie.mttr_inconsistentes"),
        ))
    if any(a.dia >= b.dia for a, b in zip(serie, serie[1:])):
        raise XanoContratoInvalido("Resposta inválida: serie.ordem.")

    horaria = None
    if visao == "hoje":
        bruto = _objeto(objeto["disponibilidade_horaria"], "disponibilidade_horaria", {"observado_ate", "pontos"})
        observado_ate = _inteiro(bruto["observado_ate"], "disponibilidade_horaria.observado_ate", positivo=True)
        if not t0 < observado_ate < t1 or not isinstance(bruto["pontos"], list) or len(bruto["pontos"]) != 24:
            raise XanoContratoInvalido("Resposta inválida: disponibilidade_horaria.")
        pontos: list[PontoDisponibilidadeHoraria] = []
        for indice, item in enumerate(bruto["pontos"]):
            ponto = _objeto(item, "disponibilidade_horaria.ponto", {"inicio", "fim", "percentual", "observado_ms", "indisponivel_ms", "totens_invalidos"})
            inicio_hora = _inteiro(ponto["inicio"], "disponibilidade_horaria.inicio", positivo=True)
            fim_hora = _inteiro(ponto["fim"], "disponibilidade_horaria.fim", positivo=True)
            observado_ms = _inteiro(ponto["observado_ms"], "disponibilidade_horaria.observado_ms")
            indisponivel_ms = _inteiro(ponto["indisponivel_ms"], "disponibilidade_horaria.indisponivel_ms")
            invalidos = _inteiro(ponto["totens_invalidos"], "disponibilidade_horaria.totens_invalidos")
            percentual = _numero(ponto["percentual"], "disponibilidade_horaria.percentual", maximo=100)
            if (inicio_hora, fim_hora) != (t0 + indice * 3_600_000, t0 + (indice + 1) * 3_600_000):
                raise XanoContratoInvalido("Resposta inválida: disponibilidade_horaria.intervalo.")
            if indisponivel_ms > observado_ms or bool(invalidos or not observado_ms) != (percentual is None):
                raise XanoContratoInvalido("Resposta inválida: disponibilidade_horaria.percentual.")
            if inicio_hora >= observado_ate and (observado_ms or indisponivel_ms or invalidos or percentual is not None):
                raise XanoContratoInvalido("Resposta inválida: disponibilidade_horaria.futuro.")
            pontos.append(PontoDisponibilidadeHoraria(inicio_hora, fim_hora, percentual, observado_ms, indisponivel_ms, invalidos))
        horaria = DisponibilidadeHoraria(observado_ate, pontos)

    return ResultadoConfiabilidade(t0, t1, lojas_id, ativos_id, disponibilidade, mttd, mttr, serie, horaria)
