"""State da fila técnica e da assunção de chamados."""

from __future__ import annotations

import reflex as rx

from app.chamados.shared import (
    DetalheView,
    TecnicoOpcaoView,
    TecnicoView,
    TimelineView,
    _detalhe_para_dict,
    _status_permite_atribuicao,
    _tecnico_para_dict,
    evento_timeline_para_dict,
)
from app.services.service_desk import (
    ChamadoDetalhe,
    DetalheChamadoTecnico,
    criar_cliente_service_desk,
)
from app.services.xano import (
    XanoConflito,
    XanoContratoInvalido,
    XanoEntradaInvalida,
    XanoIndisponivel,
    XanoNaoAutenticado,
    XanoNaoAutorizado,
    XanoNaoEncontrado,
)
from app.states.auth import (
    MENSAGEM_EXPIRADA,
    MENSAGEM_IDENTIDADE_INVALIDA,
    MENSAGEM_INDISPONIVEL,
    MENSAGEM_NAO_AUTORIZADO,
    AuthState,
)


class ChamadosTecnicoState(AuthState):
    """Mantém a fila global e as operações de responsável do chamado."""

    visao: str = "todos"
    numero: str = ""
    chamados: list[TecnicoView] = []
    chamado: DetalheView = {}
    timeline: list[TimelineView] = []
    tecnicos: list[TecnicoOpcaoView] = []
    tecnico_alvo_id: str = ""
    carregando_fila: bool = False
    carregando_detalhe_tecnico: bool = False
    assumindo_id: int | None = None
    alterando_responsavel_id: int | None = None
    mensagem_fila: str = ""
    mensagem_detalhe_tecnico: str = ""
    mensagem_assuncao: str = ""
    mensagem_responsavel: str = ""
    mensagem_sucesso_responsavel: str = ""

    def visoes(self) -> list[str]:
        if self.role == "tecnico":
            return [
                "todos",
                "nao_atribuidos",
                "atribuidos_a_mim",
                "atribuidos_a_outros",
            ]
        if self.role in {"diretoria", "administrador"}:
            return ["todos", "nao_atribuidos", "atribuidos_a_outros"]
        return []

    def _limpar_mensagens_tecnico(self) -> None:
        self.mensagem_fila = ""
        self.mensagem_detalhe_tecnico = ""
        self.mensagem_assuncao = ""
        self.mensagem_responsavel = ""
        self.mensagem_sucesso_responsavel = ""

    def _atualizar_chamado(self, chamado: ChamadoDetalhe) -> None:
        self.chamado = _detalhe_para_dict(chamado)
        responsavel = chamado.tecnico
        self.chamado["pode_liberar"] = (
            _status_permite_atribuicao(chamado.status)
            and responsavel is not None
            and (
                self.role in {"diretoria", "administrador"}
                or (
                    self.role == "tecnico"
                    and responsavel.id == self.usuario_id
                )
            )
        )

    def _atualizar_detalhe(self, detalhe: DetalheChamadoTecnico) -> None:
        self._atualizar_chamado(detalhe.chamado)
        self.timeline = [
            evento_timeline_para_dict(evento) for evento in detalhe.timeline
        ]
        self.tecnicos = [
            {"id": tecnico.id, "nome": tecnico.nome}
            for tecnico in detalhe.tecnicos
        ]
        self.tecnico_alvo_id = ""

    async def _validar_tecnico(self) -> str | None:
        return await self._revalidar("tecnico")

    async def _validar_acesso_fila(self) -> str | None:
        destino = await self._revalidar()
        if destino is not None:
            return destino
        if self.role not in {"tecnico", "diretoria", "administrador"}:
            return self.destino_por_perfil(self.role) or "/login"
        return None

    def _registrar_erro_tecnico(self, erro: Exception, destino: str) -> str | None:
        if isinstance(erro, XanoNaoAutenticado):
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            return "/login"
        if isinstance(erro, XanoNaoAutorizado):
            setattr(self, destino, MENSAGEM_NAO_AUTORIZADO)
            return None
        if isinstance(erro, XanoNaoEncontrado):
            setattr(self, destino, "Chamado não encontrado.")
            return None
        if isinstance(erro, XanoEntradaInvalida):
            setattr(self, destino, "Os dados informados são inválidos.")
            return None
        if isinstance(erro, XanoConflito):
            setattr(self, destino, "A atribuição do chamado foi alterada por outra operação.")
            return None
        if isinstance(erro, XanoIndisponivel):
            setattr(self, destino, MENSAGEM_INDISPONIVEL)
            return None
        if isinstance(erro, XanoContratoInvalido):
            setattr(self, destino, MENSAGEM_IDENTIDADE_INVALIDA)
            return None
        setattr(self, destino, MENSAGEM_INDISPONIVEL)
        return None

    @rx.event
    async def selecionar_visao(self, visao: str):
        if visao not in self.visoes():
            self.mensagem_fila = "Visão inválida."
            return
        self.visao = visao
        async for evento in self.carregar_fila():
            yield evento

    @rx.event
    def atualizar_numero(self, valor: str):
        self.numero = valor

    @rx.event
    async def pesquisar_numero(self):
        async for evento in self.carregar_fila():
            yield evento

    @rx.event
    async def limpar_pesquisa(self):
        self.numero = ""
        async for evento in self.carregar_fila():
            yield evento

    @rx.event
    async def carregar_fila(self):
        if self.carregando_fila:
            return
        self.carregando_fila = True
        self._limpar_mensagens_tecnico()
        yield
        try:
            destino = await self._validar_acesso_fila()
            if destino is not None:
                yield rx.redirect(destino)
                return
            if not self.sessao_confirmada:
                return
            if self.visao not in self.visoes():
                self.visao = "todos"
            try:
                resultado = await criar_cliente_service_desk().listar_chamados_tecnico(
                    self._auth_token,
                    self.visao,
                    self.numero.strip() or None,
                )
                self.chamados = [_tecnico_para_dict(item) for item in resultado]
            except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
                destino = self._registrar_erro_tecnico(erro, "mensagem_fila")
                if destino is not None:
                    yield rx.redirect(destino)
                    return
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            self._registrar_erro_tecnico(erro, "mensagem_fila")
        finally:
            self.carregando_fila = False

    @rx.event
    async def carregar_detalhe_tecnico(self):
        if self.carregando_detalhe_tecnico:
            return
        self.carregando_detalhe_tecnico = True
        self.chamado = {}
        self.timeline = []
        self.tecnicos = []
        self.tecnico_alvo_id = ""
        self._limpar_mensagens_tecnico()
        yield
        destino = await self._validar_acesso_fila()
        if destino is not None:
            self.carregando_detalhe_tecnico = False
            yield rx.redirect(destino)
            return
        if not self.sessao_confirmada:
            self.carregando_detalhe_tecnico = False
            return
        try:
            chamado_id = int(str(self.chamado_id))
            if chamado_id <= 0:
                raise ValueError
        except (AttributeError, TypeError, ValueError):
            self.mensagem_detalhe_tecnico = "Chamado não encontrado."
            self.carregando_detalhe_tecnico = False
            return
        try:
            resultado = await criar_cliente_service_desk().obter_chamado_tecnico(
                self._auth_token,
                chamado_id,
            )
            self._atualizar_detalhe(resultado)
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro_tecnico(erro, "mensagem_detalhe_tecnico")
            if destino is not None:
                self.carregando_detalhe_tecnico = False
                yield rx.redirect(destino)
                return
        self.carregando_detalhe_tecnico = False

    @rx.event
    def selecionar_tecnico_alvo(self, tecnico_id: str) -> None:
        self.tecnico_alvo_id = tecnico_id

    async def _executar_acao_responsavel(self, acao: str, chamado_id: int):
        if acao not in {"assumir", "atribuir", "liberar"}:
            self.mensagem_responsavel = "Ação de responsável inválida."
            return
        if acao == "assumir":
            if self.assumindo_id is not None or self.alterando_responsavel_id is not None:
                return
            self.assumindo_id = chamado_id
            campo_erro = "mensagem_assuncao"
        else:
            if self.alterando_responsavel_id is not None or self.assumindo_id is not None:
                return
            self.alterando_responsavel_id = chamado_id
            campo_erro = "mensagem_responsavel"

        self.mensagem_assuncao = ""
        self.mensagem_responsavel = ""
        self.mensagem_sucesso_responsavel = ""
        try:
            yield
            destino = (
                await self._validar_tecnico()
                if acao == "assumir"
                else await self._validar_acesso_fila()
            )
            if destino is not None:
                yield rx.redirect(destino)
                return
            if not self.sessao_confirmada:
                return

            roles_autorizados = {"tecnico", "diretoria", "administrador"}
            detalhe_atual = self.chamado.get("id") == chamado_id
            pode_atribuir = detalhe_atual and self.chamado.get("pode_atribuir", False)
            pode_liberar = detalhe_atual and self.chamado.get("pode_liberar", False)
            if acao == "assumir":
                resumo = next(
                    (item for item in self.chamados if item.get("id") == chamado_id),
                    None,
                )
                pode_assumir = (
                    detalhe_atual and self.chamado.get("pode_assumir", False)
                ) if detalhe_atual else (
                    resumo is not None and resumo.get("pode_assumir", False)
                )
                if self.role != "tecnico" or not pode_assumir:
                    self.mensagem_assuncao = "Este chamado não está disponível para assumir."
                    return
            elif self.role not in roles_autorizados:
                setattr(self, campo_erro, MENSAGEM_NAO_AUTORIZADO)
                return
            elif not pode_atribuir:
                self.mensagem_responsavel = "Este chamado não permite alterar a atribuição."
                return

            tecnico_id = None
            if acao == "atribuir":
                try:
                    tecnico_id = int(self.tecnico_alvo_id)
                except (TypeError, ValueError):
                    tecnico_id = None
                if tecnico_id is None or tecnico_id not in {
                    tecnico["id"] for tecnico in self.tecnicos
                }:
                    self.mensagem_responsavel = "Selecione um Técnico válido."
                    return
            elif acao == "liberar":
                if not pode_liberar:
                    self.mensagem_responsavel = "A liberação não está disponível para este chamado."
                    return

            cliente = criar_cliente_service_desk()
            resultado = await cliente.alterar_responsavel_tecnico(
                self._auth_token,
                chamado_id,
                acao,
                tecnico_id,
            )
            self._atualizar_chamado(resultado)
            self.mensagem_sucesso_responsavel = {
                "assumir": "Chamado assumido.",
                "atribuir": "Responsável atualizado.",
                "liberar": "Atribuição liberada.",
            }[acao]
            try:
                detalhe = await cliente.obter_chamado_tecnico(
                    self._auth_token,
                    chamado_id,
                )
                self._atualizar_detalhe(detalhe)
            except Exception as erro:  # noqa: BLE001 - falha na atualização do detalhe
                destino = self._registrar_erro_tecnico(erro, campo_erro)
                if destino is not None:
                    yield rx.redirect(destino)
                    return
                self.mensagem_sucesso_responsavel = (
                    "Alteração salva, mas não foi possível atualizar o histórico. "
                    "Recarregue o detalhe."
                )

            mensagem_assuncao = self.mensagem_assuncao
            mensagem_responsavel = self.mensagem_responsavel
            mensagem_sucesso = self.mensagem_sucesso_responsavel
            async for evento in self.carregar_fila():
                yield evento
            self.mensagem_assuncao = mensagem_assuncao
            self.mensagem_responsavel = mensagem_responsavel
            self.mensagem_sucesso_responsavel = mensagem_sucesso
            yield
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro_tecnico(erro, campo_erro)
            if destino is not None:
                yield rx.redirect(destino)
                return
            if acao == "assumir":
                mensagem_assuncao = self.mensagem_assuncao
                async for evento in self.carregar_fila():
                    yield evento
                self.mensagem_assuncao = mensagem_assuncao
                yield
        finally:
            if acao == "assumir":
                self.assumindo_id = None
            else:
                self.alterando_responsavel_id = None

    @rx.event
    async def assumir(self, chamado_id: int):
        async for evento in self._executar_acao_responsavel("assumir", chamado_id):
            yield evento

    @rx.event
    async def atribuir_responsavel(self):
        try:
            chamado_id = int(self.chamado["id"])
        except (KeyError, TypeError, ValueError):
            self.mensagem_responsavel = "Chamado não encontrado."
            return
        async for evento in self._executar_acao_responsavel(
            "atribuir",
            chamado_id,
        ):
            yield evento

    @rx.event
    async def liberar_responsavel(self):
        try:
            chamado_id = int(self.chamado["id"])
        except (KeyError, TypeError, ValueError):
            self.mensagem_responsavel = "Chamado não encontrado."
            return
        async for evento in self._executar_acao_responsavel(
            "liberar",
            chamado_id,
        ):
            yield evento
