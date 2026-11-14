"""Estado de apresentação dos indicadores executivos da Diretoria."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import TypedDict
from zoneinfo import ZoneInfo

import reflex as rx

from app.indicadores.contrato import ResultadoConfiabilidade
from app.indicadores.contrato_causas import ResultadoCausas
from app.indicadores.contrato_operacao import ResultadoOperacao
from app.services.service_desk import criar_cliente_service_desk
from app.services.xano import (
    XanoContratoInvalido,
    XanoEntradaInvalida,
    XanoIndisponivel,
    XanoNaoAutenticado,
    XanoNaoAutorizado,
)
from app.states.auth import AuthState, MENSAGEM_EXPIRADA


FUSO = ZoneInfo("America/Sao_Paulo")


def _contagem(quantidade: int, singular: str, plural: str) -> str:
    return f"{quantidade} {singular if quantidade == 1 else plural}"


def _horas_texto(minutos: float | None) -> str:
    if minutos is None:
        return "—"
    horas = minutos / 60
    return "< 0,01 h" if 0 < horas < 0.01 else f"{horas:.2f} h"


class PontoConfiabilidadeView(TypedDict):
    dia: str
    dia_texto: str
    mttd_horas: float | None
    mttr_horas: float | None
    mttd_horas_texto: str
    mttr_horas_texto: str
    mttd_eventos: int
    mttd_inconsistentes: int
    mttd_eventos_texto: str
    mttd_inconsistencias_texto: str
    mttr_recuperacoes: int
    mttr_inconsistentes: int
    mttr_recuperacoes_texto: str
    mttr_inconsistencias_texto: str


class PontoDisponibilidadeHorariaView(TypedDict):
    hora: str
    percentual: float | None
    percentual_texto: str


class ContagemOperacaoView(TypedDict):
    rotulo: str
    quantidade: int


class FatiaStatusView(TypedDict):
    rotulo: str
    quantidade: int
    fill: str


CORES_STATUS_CHAMADO = (
    "#3B82F6", "#F97316", "#EAB308", "#8B5CF6",
    "#10B981", "#E11D48", "#0F766E", "#94A3B8",
)


class LojaCausasView(TypedDict):
    nome: str
    quantidade: int


class ParetoCausasView(TypedDict):
    nome: str
    quantidade: int
    percentual: float
    acumulado_percentual: float
    percentual_texto: str
    acumulado_texto: str
    destaque_80: bool


class RecorrenciaCausasView(TypedDict):
    nome: str
    elegiveis: int
    recorrentes: int
    percentual_texto: str


class IndicadoresDiretoriaState(AuthState):
    """Mantém filtros e resultados já calculados pelo Xano."""

    data_inicio: str = ""
    data_fim: str = ""
    aba_ativa: str = "disponibilidade"
    periodo_rapido: str = "30_dias"
    mostrar_periodo_personalizado: bool = False
    datas_personalizadas_pendentes: bool = False
    loja_id: str = "todas"
    totem_id: str = "todos"
    categoria_id: str = "todas"
    lojas_opcoes: list[dict[str, str]] = []
    totens_opcoes: list[dict[str, str]] = []
    categorias_opcoes: list[dict[str, str]] = []
    carregando_indicadores: bool = False
    mensagem_erro_indicadores: str = ""
    tem_resultado: bool = False
    periodo_texto: str = ""
    disponibilidade_texto: str = "—"
    disponibilidade_detalhe: str = ""
    disponibilidade_tempo: str = ""
    disponibilidade_aviso: str = ""
    totens_observados_texto: str = "—"
    totens_qualidade_texto: str = ""
    mttd_texto: str = "—"
    mttd_detalhe: str = ""
    mttr_texto: str = "—"
    mttr_detalhe: str = ""
    serie: list[PontoConfiabilidadeView] = []
    serie_tabela: list[PontoConfiabilidadeView] = []
    serie_horaria: list[PontoDisponibilidadeHorariaView] = []
    tem_operacao: bool = False
    mensagem_erro_operacao: str = ""
    operacao_periodo_texto: str = ""
    volume_total: int = 0
    volume_status: list[ContagemOperacaoView] = []
    volume_status_grafico: list[FatiaStatusView] = []
    volume_nao_classificados: int = 0
    conformidade_texto: str = "—"
    conformidade_progresso: str = "0%"
    conformidade_cumpriram: int = 0
    conformidade_elegiveis: int = 0
    conformidade_cancelados: int = 0
    conformidade_nao_calculaveis: int = 0
    risco_instante_texto: str = ""
    risco_faixas: list[ContagemOperacaoView] = []
    risco_nao_calculaveis: int = 0
    risco_status_nao_canonicos: int = 0
    risco_sem_dados: bool = True
    consulta_geracao: int = 0
    causas_catalogo_carregado: bool = False
    tem_causas: bool = False
    mensagem_erro_causas: str = ""
    causas_periodo_texto: str = ""
    causas_recorte_texto: str = ""
    causas_elegiveis: int = 0
    causas_recorrentes: int = 0
    causas_recorrencia_texto: str = "—"
    causas_categorias_80: int = 0
    causas_exclusoes_texto: str = ""
    causas_sem_loja: int = 0
    causas_top_lojas: list[LojaCausasView] = []
    causas_pareto: list[ParetoCausasView] = []
    causas_por_loja: list[RecorrenciaCausasView] = []
    causas_por_totem: list[RecorrenciaCausasView] = []

    @rx.event
    def selecionar_aba(self, valor: str):
        if valor in ("disponibilidade", "operacao", "causas"):
            self.aba_ativa = valor
            self.mostrar_periodo_personalizado = False
            if valor == "causas" and not self.tem_causas:
                return IndicadoresDiretoriaState.carregar_causas

    @rx.event
    def alterar_data_inicio(self, valor: str) -> None:
        self.data_inicio = valor
        self.datas_personalizadas_pendentes = True

    @rx.event
    def alterar_data_fim(self, valor: str) -> None:
        self.data_fim = valor
        self.datas_personalizadas_pendentes = True

    @rx.event
    def alterar_periodo_personalizado(self, inicio: str, fim: str) -> None:
        self.data_inicio = inicio
        self.data_fim = fim
        self.datas_personalizadas_pendentes = True

    @rx.event
    def alternar_periodo_personalizado(self) -> None:
        self.mostrar_periodo_personalizado = not self.mostrar_periodo_personalizado

    @rx.event
    def alterar_loja(self, valor: str) -> None:
        self.loja_id = valor

    @rx.event
    def alterar_totem(self, valor: str) -> None:
        self.totem_id = valor

    @rx.event
    def alterar_categoria(self, valor: str) -> None:
        self.categoria_id = valor

    def _limpar_resultado(self) -> None:
        self._limpar_causas()
        self.tem_resultado = False
        self.periodo_texto = ""
        self.disponibilidade_texto = "—"
        self.disponibilidade_detalhe = ""
        self.disponibilidade_tempo = ""
        self.disponibilidade_aviso = ""
        self.totens_observados_texto = "—"
        self.totens_qualidade_texto = ""
        self.mttd_texto = "—"
        self.mttd_detalhe = ""
        self.mttr_texto = "—"
        self.mttr_detalhe = ""
        self.serie = []
        self.serie_tabela = []
        self.serie_horaria = []
        self.tem_operacao = False
        self.mensagem_erro_operacao = ""
        self.operacao_periodo_texto = ""
        self.volume_total = 0
        self.volume_status = []
        self.volume_status_grafico = []
        self.volume_nao_classificados = 0
        self.conformidade_texto = "—"
        self.conformidade_progresso = "0%"
        self.conformidade_cumpriram = 0
        self.conformidade_elegiveis = 0
        self.conformidade_cancelados = 0
        self.conformidade_nao_calculaveis = 0
        self.risco_instante_texto = ""
        self.risco_faixas = []
        self.risco_nao_calculaveis = 0
        self.risco_status_nao_canonicos = 0
        self.risco_sem_dados = True

    def _limpar_causas(self) -> None:
        self.tem_causas = False
        self.mensagem_erro_causas = ""
        self.causas_periodo_texto = ""
        self.causas_recorte_texto = ""
        self.causas_elegiveis = 0
        self.causas_recorrentes = 0
        self.causas_recorrencia_texto = "—"
        self.causas_categorias_80 = 0
        self.causas_exclusoes_texto = ""
        self.causas_sem_loja = 0
        self.causas_top_lojas = []
        self.causas_pareto = []
        self.causas_por_loja = []
        self.causas_por_totem = []

    def _apresentar_causas(self, resultado: ResultadoCausas) -> None:
        inicio = datetime.fromtimestamp(resultado.t0 / 1000, FUSO)
        fim = datetime.fromtimestamp(resultado.observado_ate / 1000, FUSO)
        self.causas_periodo_texto = f"Aberturas de {inicio:%d/%m/%Y %H:%M} até {fim:%d/%m/%Y %H:%M} · horário de Brasília"
        nomes = []
        for identificador, opcoes, geral in (
            (resultado.lojas_id, self.lojas_opcoes, "Todas as Lojas"),
            (resultado.ativos_referencia_id, self.totens_opcoes, "Todos os Totens"),
            (resultado.categorias_servico_id, self.categorias_opcoes, "Todas as Categorias"),
        ):
            nomes.append(geral if identificador is None else next(
                (opcao["label"] for opcao in opcoes if opcao["value"] == str(identificador)),
                f"ID {identificador}",
            ))
        self.causas_recorte_texto = " · ".join(nomes)
        self.causas_elegiveis = resultado.base["elegiveis"]
        self.causas_recorrentes = resultado.recorrentes
        self.causas_recorrencia_texto = "—" if resultado.percentual is None else f"{resultado.percentual:.2f}%"
        self.causas_categorias_80 = resultado.categorias_80
        self.causas_sem_loja = resultado.base["sem_loja"]
        self.causas_exclusoes_texto = (
            f"Fora da base no período: {resultado.base['cancelados']} Cancelados · "
            f"{resultado.base['requisicoes']} Requisições · {resultado.base['inconsistentes']} com dados inconsistentes. "
            f"Sem data e sem atribuição ao período: {resultado.base['sem_data']}."
        )
        self.causas_top_lojas = [{"nome": x["nome"], "quantidade": x["quantidade"]} for x in resultado.top_lojas]
        self.causas_pareto = [
            {"nome": x["nome"], "quantidade": x["quantidade"], "percentual": x["percentual"],
             "acumulado_percentual": x["acumulado_percentual"], "destaque_80": x["destaque_80"],
             "percentual_texto": f"{x['percentual']:.2f}%", "acumulado_texto": f"{x['acumulado_percentual']:.2f}%"}
            for x in resultado.pareto
        ]
        self.causas_por_loja = self._segmentos_causas(resultado.por_loja)
        self.causas_por_totem = self._segmentos_causas(resultado.por_totem)
        self.tem_causas = True

    @staticmethod
    def _segmentos_causas(linhas: list[dict]) -> list[RecorrenciaCausasView]:
        return [{"nome": x["nome"], "elegiveis": x["elegiveis"], "recorrentes": x["recorrentes"],
                 "percentual_texto": f"{x['percentual']:.2f}%"} for x in linhas]

    def _inicializar_periodo(self) -> None:
        if self.data_inicio and self.data_fim:
            return
        self._definir_datas_rapidas("30_dias", datetime.now(FUSO))

    def _definir_datas_rapidas(self, periodo: str, agora: datetime) -> None:
        hoje = agora.date()
        self.data_inicio = (hoje - timedelta(days=29 if periodo == "30_dias" else 0)).isoformat()
        self.data_fim = hoje.isoformat()
        self.periodo_rapido = periodo
        self.datas_personalizadas_pendentes = False

    def _limites(self, *, agora: datetime | None = None, incluir_totem: bool = True) -> tuple[int, int, int | None, int | None]:
        try:
            inicio = date.fromisoformat(self.data_inicio)
            fim = date.fromisoformat(self.data_fim)
            agora = agora or datetime.now(FUSO)
            if inicio > fim or fim > agora.date():
                raise ValueError
            t0 = int(datetime.combine(inicio, time.min, FUSO).timestamp() * 1000)
            fim_exclusivo = datetime.combine(fim + timedelta(days=1), time.min, FUSO)
            t1 = int((fim_exclusivo if self.periodo_rapido == "hoje" else min(fim_exclusivo, agora)).timestamp() * 1000)
            loja = None if self.loja_id == "todas" else int(self.loja_id)
            totem = None if not incluir_totem or self.totem_id == "todos" else int(self.totem_id)
            if t0 >= t1 or (loja is not None and loja <= 0) or (totem is not None and totem <= 0):
                raise ValueError
            return t0, t1, loja, totem
        except (ValueError, TypeError, OverflowError) as exc:
            raise ValueError("Informe um período e filtros válidos.") from exc

    def _apresentar(self, resultado: ResultadoConfiabilidade) -> None:
        inicio_texto = f"{datetime.fromtimestamp(resultado.t0 / 1000, FUSO):%d/%m/%Y %H:%M}"
        if resultado.disponibilidade_horaria is None:
            self.periodo_texto = f"{inicio_texto} até {datetime.fromtimestamp(resultado.t1 / 1000, FUSO):%d/%m/%Y %H:%M}"
        else:
            fim_texto = f"{datetime.fromtimestamp((resultado.t1 - 60_000) / 1000, FUSO):%d/%m/%Y %H:%M}"
            observado_texto = f"{datetime.fromtimestamp(resultado.disponibilidade_horaria.observado_ate / 1000, FUSO):%H:%M}"
            self.periodo_texto = f"{inicio_texto} até {fim_texto} · observado até {observado_texto}"
        disp = resultado.disponibilidade
        self.disponibilidade_texto = "—" if disp.percentual is None else f"{disp.percentual:.2f}%"
        self.disponibilidade_aviso = (
            "Histórico necessário inconsistente; o percentual pode estar indisponível."
            if disp.totens_invalidos else
            "Sem tempo observável no recorte." if not disp.observado_ms else ""
        )
        self.disponibilidade_detalhe = (
            f"{_contagem(disp.totens_incluidos, 'Totem observado', 'Totens observados')} · "
            f"{disp.totens_sem_observacao} sem observação · "
            f"{disp.totens_invalidos} com histórico inválido"
        )
        self.totens_observados_texto = str(disp.totens_incluidos)
        self.totens_qualidade_texto = (
            f"{disp.totens_sem_observacao} sem observação · "
            f"{_contagem(disp.totens_invalidos, 'histórico inválido', 'históricos inválidos')}"
        )
        self.disponibilidade_tempo = (
            f"{_horas_texto(disp.observado_ms / 60_000)} observadas · "
            f"{_horas_texto(disp.indisponivel_ms / 60_000)} indisponíveis"
            f"{' (histórico incompleto)' if disp.totens_invalidos else ''}"
        )
        self.mttd_texto = _horas_texto(resultado.mttd.minutos)
        self.mttd_detalhe = (
            f"{_contagem(resultado.mttd.eventos, 'detecção elegível', 'detecções elegíveis')} · "
            f"{_contagem(resultado.mttd.inconsistentes, 'inconsistência', 'inconsistências')}"
        )
        self.mttr_texto = _horas_texto(resultado.mttr.minutos)
        self.mttr_detalhe = (
            f"{_contagem(resultado.mttr.eventos, 'recuperação elegível', 'recuperações elegíveis')} · "
            f"{_contagem(resultado.mttr.abertas, 'indisponibilidade aberta', 'indisponibilidades abertas')} · "
            f"{_contagem(resultado.mttr.inconsistentes, 'inconsistência', 'inconsistências')}"
        )
        self.serie = [
            {
                "dia": ponto.dia,
                "dia_texto": date.fromisoformat(ponto.dia).strftime("%d/%m/%Y"),
                "mttd_horas": None if ponto.mttd_minutos is None else round(ponto.mttd_minutos / 60, 4),
                "mttr_horas": None if ponto.mttr_minutos is None else round(ponto.mttr_minutos / 60, 4),
                "mttd_horas_texto": _horas_texto(ponto.mttd_minutos),
                "mttr_horas_texto": _horas_texto(ponto.mttr_minutos),
                "mttd_eventos": ponto.mttd_eventos,
                "mttd_inconsistentes": ponto.mttd_inconsistentes,
                "mttd_eventos_texto": _contagem(ponto.mttd_eventos, "detecção", "detecções"),
                "mttd_inconsistencias_texto": _contagem(ponto.mttd_inconsistentes, "inconsistência", "inconsistências"),
                "mttr_recuperacoes": ponto.mttr_recuperacoes,
                "mttr_inconsistentes": ponto.mttr_inconsistentes,
                "mttr_recuperacoes_texto": _contagem(ponto.mttr_recuperacoes, "recuperação", "recuperações"),
                "mttr_inconsistencias_texto": _contagem(ponto.mttr_inconsistentes, "inconsistência", "inconsistências"),
            }
            for ponto in resultado.serie
        ]
        self.serie_tabela = list(reversed(self.serie))
        self.serie_horaria = [
            {
                "hora": f"{datetime.fromtimestamp(ponto.inicio / 1000, FUSO):%H}h",
                "percentual": ponto.percentual,
                "percentual_texto": "Sem dados" if ponto.percentual is None else f"{ponto.percentual:.2f}%",
            }
            for ponto in resultado.disponibilidade_horaria.pontos
        ] if resultado.disponibilidade_horaria is not None else []
        self.tem_resultado = True

    def _apresentar_operacao(self, resultado: ResultadoOperacao) -> None:
        inicio = f"{datetime.fromtimestamp(resultado.t0 / 1000, FUSO):%d/%m/%Y %H:%M}"
        fim_ms = resultado.t1 - 60_000 if resultado.t1 > resultado.observado_ate else resultado.t1
        fim = f"{datetime.fromtimestamp(fim_ms / 1000, FUSO):%d/%m/%Y %H:%M}"
        self.operacao_periodo_texto = f"Período: {inicio} até {fim}"
        self.volume_total = resultado.volumetria.total
        self.volume_status = [
            {"rotulo": item.status, "quantidade": item.quantidade}
            for item in resultado.volumetria.por_status
        ]
        self.volume_nao_classificados = resultado.volumetria.nao_classificados
        self.volume_status_grafico = [
            {"rotulo": item.status, "quantidade": item.quantidade, "fill": cor}
            for item, cor in zip(resultado.volumetria.por_status, CORES_STATUS_CHAMADO)
            if item.quantidade > 0
        ]
        if resultado.volumetria.nao_classificados:
            self.volume_status_grafico.append({
                "rotulo": "Não classificados",
                "quantidade": resultado.volumetria.nao_classificados,
                "fill": "#64748B",
            })
        conformidade = resultado.conformidade
        self.conformidade_texto = "—" if conformidade.percentual is None else f"{conformidade.percentual:.2f}%"
        self.conformidade_progresso = "0%" if conformidade.percentual is None else f"{conformidade.percentual:g}%"
        self.conformidade_cumpriram = conformidade.cumpriram
        self.conformidade_elegiveis = conformidade.elegiveis
        self.conformidade_cancelados = conformidade.cancelados
        self.conformidade_nao_calculaveis = conformidade.nao_calculaveis
        self.risco_instante_texto = f"{datetime.fromtimestamp(resultado.risco.calculado_em / 1000, FUSO):%d/%m/%Y %H:%M}"
        self.risco_faixas = [
            {"rotulo": rotulo, "quantidade": getattr(resultado.risco, campo)}
            for rotulo, campo in (("Normal · < 70%", "normal"), ("Risco · 70–90%", "risco"), ("Crítico · > 90–100%", "critico"), ("Violado · > 100%", "violado"))
        ]
        self.risco_nao_calculaveis = resultado.risco.nao_calculaveis
        self.risco_status_nao_canonicos = resultado.risco.status_nao_canonicos
        self.risco_sem_dados = not any((
            resultado.risco.normal, resultado.risco.risco, resultado.risco.critico,
            resultado.risco.violado, resultado.risco.nao_calculaveis,
        ))
        self.tem_operacao = True

    async def _validar_acesso(self) -> str | None:
        destino = await self._revalidar()
        if destino is not None:
            return destino
        if not self.sessao_confirmada or not self.perfil_operacional or self.deve_trocar_senha:
            return "/inicio"
        return None

    async def _consultar(self, *, carregar_catalogo: bool, geracao: int, agora: datetime | None = None) -> str | None:
        try:
            t0, t1, loja, totem = self._limites(agora=agora)
            cliente = criar_cliente_service_desk()
            if carregar_catalogo:
                catalogo = await cliente.catalogo_indicadores_disponibilidade(self._auth_token)
                if geracao != self.consulta_geracao:
                    return None
                self.lojas_opcoes = [{"value": "todas", "label": "Todas as Lojas"}] + [
                    {"value": str(item.id), "label": item.nome} for item in catalogo.lojas
                ]
                self.totens_opcoes = [{"value": "todos", "label": "Todos os Totens"}] + [
                    {"value": str(item.id), "label": f"{item.id} — {item.nome}"} for item in catalogo.totens
                ]
            resultado = await cliente.consultar_indicadores_disponibilidade(
                self._auth_token, t0=t0, t1=t1, lojas_id=loja, ativos_referencia_id=totem,
                visao="hoje" if self.periodo_rapido == "hoje" else None,
            )
            if geracao != self.consulta_geracao:
                return None
            if (resultado.t0, resultado.t1, resultado.lojas_id, resultado.ativos_referencia_id) != (t0, t1, loja, totem):
                raise XanoContratoInvalido("O serviço retornou filtros diferentes dos solicitados.")
            self._apresentar(resultado)
        except ValueError as exc:
            if geracao != self.consulta_geracao:
                return None
            self.mensagem_erro_indicadores = str(exc)
        except XanoNaoAutenticado:
            if geracao != self.consulta_geracao:
                return None
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            return "/login"
        except XanoNaoAutorizado:
            if geracao != self.consulta_geracao:
                return None
            return "/inicio"
        except XanoEntradaInvalida:
            if geracao != self.consulta_geracao:
                return None
            self.mensagem_erro_indicadores = "O serviço rejeitou o período ou os filtros informados."
        except XanoContratoInvalido:
            if geracao != self.consulta_geracao:
                return None
            self.mensagem_erro_indicadores = "A resposta dos indicadores é incompatível."
        except XanoIndisponivel:
            if geracao != self.consulta_geracao:
                return None
            self.mensagem_erro_indicadores = "Os indicadores estão indisponíveis. Tente novamente."
        except Exception:
            if geracao != self.consulta_geracao:
                return None
            self.mensagem_erro_indicadores = "Os indicadores estão indisponíveis. Tente novamente."
        return None

    async def _consultar_operacao(self, *, carregar_catalogo: bool, geracao: int, agora: datetime) -> str | None:
        try:
            t0, t1, loja, _ = self._limites(agora=agora, incluir_totem=False)
            categoria = None if self.categoria_id == "todas" else int(self.categoria_id)
            if categoria is not None and categoria <= 0:
                raise ValueError("Informe uma Categoria válida.")
            cliente = criar_cliente_service_desk()
            if carregar_catalogo:
                catalogo = await cliente.catalogo_indicadores_operacao(self._auth_token)
                if geracao != self.consulta_geracao:
                    return None
                if not self.lojas_opcoes:
                    self.lojas_opcoes = [{"value": "todas", "label": "Todas as Lojas"}] + [
                        {"value": str(item.id), "label": item.nome} for item in catalogo.lojas
                    ]
                self.categorias_opcoes = [{"value": "todas", "label": "Todas as Categorias"}] + [
                    {"value": str(item.id), "label": item.nome} for item in catalogo.categorias
                ]
            resultado = await cliente.consultar_indicadores_operacao(
                self._auth_token, t0=t0, t1=t1, lojas_id=loja,
                categorias_servico_id=categoria, visao="hoje" if self.periodo_rapido == "hoje" else None,
            )
            if geracao != self.consulta_geracao:
                return None
            if (resultado.t0, resultado.t1, resultado.lojas_id, resultado.categorias_servico_id) != (t0, t1, loja, categoria):
                raise XanoContratoInvalido("O serviço retornou filtros diferentes dos solicitados.")
            self._apresentar_operacao(resultado)
        except ValueError as exc:
            if geracao == self.consulta_geracao:
                self.mensagem_erro_operacao = str(exc)
        except XanoNaoAutenticado:
            if geracao != self.consulta_geracao:
                return None
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            return "/login"
        except XanoNaoAutorizado:
            if geracao == self.consulta_geracao:
                return "/inicio"
        except XanoEntradaInvalida:
            if geracao == self.consulta_geracao:
                self.mensagem_erro_operacao = "O serviço rejeitou o período ou os filtros de chamados."
        except XanoContratoInvalido:
            if geracao == self.consulta_geracao:
                self.mensagem_erro_operacao = "A resposta dos indicadores de chamados é incompatível."
        except XanoIndisponivel:
            if geracao == self.consulta_geracao:
                self.mensagem_erro_operacao = "Os indicadores de chamados estão indisponíveis. Tente novamente."
        except Exception:
            if geracao == self.consulta_geracao:
                self.mensagem_erro_operacao = "Os indicadores de chamados estão indisponíveis. Tente novamente."
        return None

    async def _consultar_causas(self, *, carregar_catalogo: bool, geracao: int, agora: datetime) -> str | None:
        try:
            t0, t1, loja, totem = self._limites(agora=agora)
            categoria = None if self.categoria_id == "todas" else int(self.categoria_id)
            if categoria is not None and categoria <= 0:
                raise ValueError("Informe uma Categoria válida.")
            cliente = criar_cliente_service_desk()
            if carregar_catalogo:
                catalogo = await cliente.catalogo_indicadores_causas(self._auth_token)
                if geracao != self.consulta_geracao:
                    return None
                for campo, itens, geral in (("lojas_opcoes", catalogo.lojas, "Todas as Lojas"),
                                             ("totens_opcoes", catalogo.totens, "Todos os Totens"),
                                             ("categorias_opcoes", catalogo.categorias, "Todas as Categorias")):
                    setattr(self, campo, [{"value": "todos" if campo == "totens_opcoes" else "todas", "label": geral}]
                            + [{"value": str(x.id), "label": f"{x.id} — {x.nome}" if campo == "totens_opcoes" else x.nome} for x in itens])
                self.causas_catalogo_carregado = True
            resultado = await cliente.consultar_indicadores_causas(
                self._auth_token, t0=t0, t1=t1, lojas_id=loja, ativos_referencia_id=totem,
                categorias_servico_id=categoria, visao="hoje" if self.periodo_rapido == "hoje" else None,
            )
            if geracao != self.consulta_geracao:
                return None
            if (resultado.t0, resultado.t1, resultado.lojas_id, resultado.ativos_referencia_id, resultado.categorias_servico_id) != (t0, t1, loja, totem, categoria):
                raise XanoContratoInvalido("O serviço retornou filtros diferentes dos solicitados.")
            self._apresentar_causas(resultado)
        except XanoNaoAutenticado:
            if geracao == self.consulta_geracao:
                self._limpar_sessao(MENSAGEM_EXPIRADA)
                return "/login"
        except XanoNaoAutorizado:
            if geracao == self.consulta_geracao:
                return "/inicio"
        except ValueError as exc:
            if geracao == self.consulta_geracao:
                self.mensagem_erro_causas = str(exc)
        except XanoEntradaInvalida:
            if geracao == self.consulta_geracao:
                self.mensagem_erro_causas = "O serviço rejeitou o período ou os filtros de causas."
        except XanoContratoInvalido:
            if geracao == self.consulta_geracao:
                self.mensagem_erro_causas = "A resposta de causas e recorrência é incompatível."
        except Exception:
            if geracao == self.consulta_geracao:
                self.mensagem_erro_causas = "Causas e recorrência estão indisponíveis. Tente novamente."
        return None

    @rx.event
    async def carregar_causas(self):
        self._inicializar_periodo()
        self.consulta_geracao += 1
        geracao = self.consulta_geracao
        self._limpar_causas()
        self.carregando_indicadores = True
        yield
        destino = await self._validar_acesso()
        if destino is None:
            destino = await self._consultar_causas(carregar_catalogo=not self.causas_catalogo_carregado, geracao=geracao, agora=datetime.now(FUSO))
        if geracao == self.consulta_geracao:
            self.carregando_indicadores = False
        if destino is not None:
            yield rx.redirect(destino)

    @rx.event
    async def carregar(self):
        self._inicializar_periodo()
        agora = datetime.now(FUSO)
        self.consulta_geracao += 1
        geracao = self.consulta_geracao
        self._limpar_resultado()
        self.mensagem_erro_indicadores = ""
        self.carregando_indicadores = True
        yield
        destino = await self._validar_acesso()
        if destino is None:
            destino = await self._consultar(carregar_catalogo=True, geracao=geracao, agora=agora)
        if destino is None:
            destino = await self._consultar_operacao(carregar_catalogo=True, geracao=geracao, agora=agora)
        if destino is None and self.aba_ativa == "causas":
            destino = await self._consultar_causas(carregar_catalogo=not self.causas_catalogo_carregado, geracao=geracao, agora=agora)
        if geracao == self.consulta_geracao:
            self.carregando_indicadores = False
        if destino is not None:
            yield rx.redirect(destino)

    @rx.event
    async def aplicar_filtros(self):
        self.mostrar_periodo_personalizado = False
        if self.datas_personalizadas_pendentes:
            self.periodo_rapido = "personalizado"
            self.datas_personalizadas_pendentes = False
        agora = datetime.now(FUSO)
        if self.periodo_rapido in ("30_dias", "hoje"):
            self._definir_datas_rapidas(self.periodo_rapido, agora)
        self.consulta_geracao += 1
        geracao = self.consulta_geracao
        self._limpar_resultado()
        self.mensagem_erro_indicadores = ""
        self.carregando_indicadores = True
        yield
        destino = await self._validar_acesso()
        if destino is None:
            destino = await self._consultar(carregar_catalogo=False, geracao=geracao, agora=agora)
        if destino is None:
            destino = await self._consultar_operacao(carregar_catalogo=False, geracao=geracao, agora=agora)
        if destino is None and self.aba_ativa == "causas":
            destino = await self._consultar_causas(carregar_catalogo=not self.causas_catalogo_carregado, geracao=geracao, agora=agora)
        if geracao == self.consulta_geracao:
            self.carregando_indicadores = False
        if destino is not None:
            yield rx.redirect(destino)

    @rx.event
    async def selecionar_periodo_rapido(self, periodo: str):
        if periodo not in ("30_dias", "hoje"):
            return
        self.mostrar_periodo_personalizado = False
        agora = datetime.now(FUSO)
        self._definir_datas_rapidas(periodo, agora)
        self.consulta_geracao += 1
        geracao = self.consulta_geracao
        self._limpar_resultado()
        self.mensagem_erro_indicadores = ""
        self.carregando_indicadores = True
        yield
        destino = await self._validar_acesso()
        if destino is None:
            destino = await self._consultar(carregar_catalogo=False, geracao=geracao, agora=agora)
        if destino is None:
            destino = await self._consultar_operacao(carregar_catalogo=False, geracao=geracao, agora=agora)
        if destino is None and self.aba_ativa == "causas":
            destino = await self._consultar_causas(carregar_catalogo=not self.causas_catalogo_carregado, geracao=geracao, agora=agora)
        if geracao == self.consulta_geracao:
            self.carregando_indicadores = False
        if destino is not None:
            yield rx.redirect(destino)
