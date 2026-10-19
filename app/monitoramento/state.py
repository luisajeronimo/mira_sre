"""Estado da página de monitoramento dos Totens."""

from __future__ import annotations

from typing import ClassVar

import reflex as rx

from app.services.service_desk import criar_cliente_service_desk
from app.services.xano import (
    XanoContratoInvalido,
    XanoIndisponivel,
    XanoNaoAutenticado,
    XanoNaoAutorizado,
)
from app.states.auth import (
    MENSAGEM_EXPIRADA,
    MENSAGEM_IDENTIDADE_INVALIDA,
    MENSAGEM_INDISPONIVEL,
    MENSAGEM_NAO_AUTORIZADO,
    AuthState,
)


class MonitoramentoState(AuthState):
    """Mantém os Totens exibidos na tela de monitoramento."""

    ativos: list[dict[str, str | int]] = []
    carregando: bool = False
    mensagem_erro: str = ""

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
                    "status_atual": item.status_atual,
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
