"""Estado da página de monitoramento dos Totens."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import ClassVar, TypedDict

import reflex as rx

from app.services.service_desk import criar_cliente_service_desk
from app.services.xano import (
    XanoContratoInvalido,
    XanoIndisponivel,
    XanoNaoAutenticado,
    XanoNaoAutorizado,
    XanoNaoEncontrado,
)


class ResumoTotemView(TypedDict):
    id: int
    nome_ativo: str
    tipo: str
    loja_nome: str
    status_atual: str
    ultima_telemetria_em_texto: str
    ultima_transicao_disponibilidade_em_texto: str


class TelemetriaTotemView(TypedDict, total=False):
    id: int
    evento_timestamp_texto: str
    uso_cpu: str
    uso_memoria: str
    temperatura: str
    status_rede: str


class TransicaoTotemView(TypedDict):
    id: int
    status: str
    detectado_em_texto: str
    heartbeat_limite_minutos: str


class IncidenteTotemView(TypedDict):
    id: int
    titulo: str
    status: str
    prioridade: str
    criado_em_texto: str
    ultima_atualizacao_em_texto: str
    categoria_nome: str


class DetalheTotemView(TypedDict, total=False):
    id: int
    nome_ativo: str
    tipo: str
    loja_nome: str
    status_atual: str
    tem_ultima_telemetria: bool
    ultima_telemetria: TelemetriaTotemView
    telemetrias: list[TelemetriaTotemView]
    transicoes: list[TransicaoTotemView]
    incidentes: list[IncidenteTotemView]
from app.states.auth import (
    MENSAGEM_EXPIRADA,
    MENSAGEM_IDENTIDADE_INVALIDA,
    MENSAGEM_INDISPONIVEL,
    MENSAGEM_NAO_AUTORIZADO,
    AuthState,
)


class MonitoramentoState(AuthState):
    """Mantém os Totens exibidos na tela de monitoramento."""

    ativos: list[ResumoTotemView] = []
    detalhe_totem: DetalheTotemView = {}
    totem_selecionado_id: int | None = None
    carregando: bool = False
    carregando_detalhe: bool = False
    mensagem_erro: str = ""
    mensagem_erro_detalhe: str = ""

    PERFIS_AUTORIZADOS: ClassVar[frozenset[str]] = frozenset(
        {"tecnico", "diretoria", "administrador"}
    )

    @rx.var
    def total_totens(self) -> int:
        return len(self.ativos)

    @rx.var
    def totens_online(self) -> int:
        return sum(
            1 for ativo in self.ativos
            if ativo["status_atual"] == "online"
        )

    @rx.var
    def totens_offline(self) -> int:
        return sum(
            1 for ativo in self.ativos
            if ativo["status_atual"] == "offline"
        )

    @rx.var
    def detalhe_carregado(self) -> bool:
        return bool(self.detalhe_totem)

    @staticmethod
    def _timestamp_para_texto(valor: int | None) -> str:
        if valor is None:
            return "Sem registro"
        try:
            return datetime.fromtimestamp(
                valor / 1000,
                tz=timezone.utc,
            ).astimezone().strftime("%d/%m/%Y %H:%M")
        except (OverflowError, OSError, TypeError, ValueError):
            return "Sem registro"

    @staticmethod
    def _telemetria_para_dict(telemetria) -> TelemetriaTotemView:
        return {
            "id": telemetria.id,
            "evento_timestamp_texto": MonitoramentoState._timestamp_para_texto(
                telemetria.evento_timestamp
            ),
            "uso_cpu": f"{telemetria.uso_cpu}%",
            "uso_memoria": f"{telemetria.uso_memoria}%",
            "temperatura": f"{telemetria.temperatura}°C",
            "status_rede": telemetria.status_rede,
        }

    def _atualizar_detalhe(self, resultado) -> None:
        ultima = resultado.ultima_telemetria
        self.detalhe_totem = {
            "id": resultado.totem.id,
            "nome_ativo": resultado.totem.nome_ativo,
            "tipo": resultado.totem.tipo,
            "loja_nome": (
                resultado.totem.loja.nome
                if resultado.totem.loja is not None
                else "Loja não informada"
            ),
            "status_atual": resultado.totem.status_atual,
            "tem_ultima_telemetria": ultima is not None,
            "ultima_telemetria": (
                self._telemetria_para_dict(ultima) if ultima is not None else {}
            ),
            "telemetrias": [
                self._telemetria_para_dict(telemetria)
                for telemetria in resultado.telemetrias
            ],
            "transicoes": [
                {
                    "id": transicao.id,
                    "status": transicao.status,
                    "detectado_em_texto": self._timestamp_para_texto(
                        transicao.detectado_em
                    ),
                    "heartbeat_limite_minutos": (
                        f"{transicao.heartbeat_limite_minutos} minutos"
                    ),
                }
                for transicao in resultado.transicoes_disponibilidade
            ],
            "incidentes": [
                {
                    "id": incidente.id,
                    "titulo": incidente.titulo,
                    "status": incidente.status,
                    "prioridade": incidente.prioridade,
                    "criado_em_texto": self._timestamp_para_texto(
                        incidente.criado_em
                    ),
                    "ultima_atualizacao_em_texto": self._timestamp_para_texto(
                        incidente.ultima_atualizacao_em
                    ),
                    "categoria_nome": incidente.categoria.nome,
                }
                for incidente in resultado.incidentes_automaticos
            ],
        }
        self.totem_selecionado_id = resultado.totem.id

    async def _carregar(self):
        try:
            cliente = criar_cliente_service_desk()
            resultado = await cliente.listar_ativos_monitoramento(
                self._auth_token
            )
            self.ativos = [
                {
                    "id": item.id,
                    "nome_ativo": item.nome_ativo,
                    "tipo": item.tipo,
                    "loja_nome": (
                        item.loja.nome if item.loja is not None else "Loja não informada"
                    ),
                    "status_atual": item.status_atual,
                    "ultima_telemetria_em_texto": self._timestamp_para_texto(
                        item.ultima_telemetria_em
                    ),
                    "ultima_transicao_disponibilidade_em_texto": self._timestamp_para_texto(
                        item.ultima_transicao_disponibilidade_em
                    ),
                }
                for item in resultado
            ]
        except XanoNaoAutenticado:
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            return "/login"
        except XanoNaoAutorizado:
            self.mensagem_erro = MENSAGEM_NAO_AUTORIZADO
        except XanoIndisponivel:
            self.mensagem_erro = MENSAGEM_INDISPONIVEL
        except XanoContratoInvalido:
            self.mensagem_erro = MENSAGEM_IDENTIDADE_INVALIDA
        except Exception:
            self.mensagem_erro = MENSAGEM_INDISPONIVEL
        return None

    def _registrar_erro_detalhe(self, erro: Exception) -> str | None:
        if isinstance(erro, XanoNaoAutenticado):
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            return "/login"
        if isinstance(erro, XanoNaoAutorizado):
            self.mensagem_erro_detalhe = MENSAGEM_NAO_AUTORIZADO
        elif isinstance(erro, XanoNaoEncontrado):
            self.mensagem_erro_detalhe = "Totem não encontrado."
        elif isinstance(erro, XanoIndisponivel):
            self.mensagem_erro_detalhe = MENSAGEM_INDISPONIVEL
        elif isinstance(erro, XanoContratoInvalido):
            self.mensagem_erro_detalhe = (
                "Não foi possível carregar o detalhe porque a resposta do serviço é incompatível."
            )
        else:
            self.mensagem_erro_detalhe = MENSAGEM_INDISPONIVEL
        return None

    async def _validar_acesso_monitoramento(self) -> str | None:
        """Revalida a sessão antes de permitir qualquer consulta global."""
        destino = await self._revalidar()
        if destino is not None:
            return destino
        if not self.sessao_confirmada or self.role not in self.PERFIS_AUTORIZADOS:
            return "/inicio"
        return None

    @rx.event
    async def carregar(self):
        if self.carregando:
            return

        self.carregando = True
        self.mensagem_erro = ""
        yield

        destino = await self._validar_acesso_monitoramento()

        if destino is not None:
            self.carregando = False
            yield rx.redirect(destino)
            return

        destino = await self._carregar()

        self.carregando = False

        if destino is not None:
            yield rx.redirect(destino)

    @rx.event
    async def selecionar_totem(self, ativos_referencia_id: int):
        if self.carregando_detalhe:
            return
        self.carregando_detalhe = True
        self.mensagem_erro_detalhe = ""
        yield
        try:
            cliente = criar_cliente_service_desk()
            resultado = await cliente.obter_detalhe_ativo_monitoramento(
                self._auth_token,
                ativos_referencia_id,
            )
            self._atualizar_detalhe(resultado)
        except Exception as erro:  # noqa: BLE001 - convertido em mensagem sanitizada
            destino = self._registrar_erro_detalhe(erro)
            if destino is not None:
                self.carregando_detalhe = False
                yield rx.redirect(destino)
                return
        self.carregando_detalhe = False
