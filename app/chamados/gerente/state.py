"""State da jornada de chamados do Gerente."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, TypedDict
from zoneinfo import ZoneInfo

import reflex as rx

from app.chamados.shared import (
    ChamadoView,
    ComentarioView,
    DetalheView,
    HistoricoStatusView,
    _detalhe_para_dict,
    _resumo_para_dict,
    comentario_publico_para_dict,
    consumo_sla_para_dict,
    historico_status_para_dict,
)
from app.services.service_desk import PRIORIDADES_CHAMADO, criar_cliente_service_desk
from app.services.xano import (
    XanoContratoInvalido,
    XanoConflito,
    XanoEntradaInvalida,
    XanoIndisponivel,
    XanoNaoAutenticado,
    XanoNaoAutorizado,
    XanoNaoEncontrado,
)
from app.states.auth import (
    DESTINO_PRIMEIRO_ACESSO,
    MENSAGEM_EXPIRADA,
    MENSAGEM_INDISPONIVEL,
    MENSAGEM_NAO_AUTORIZADO,
    AuthState,
)


class ChamadosGerenteState(AuthState):
    """Mantém catálogos e dados de chamados separados da autenticação."""

    chamados: list[ChamadoView] = []
    ativos: list[str] = []
    ativos_formulario: list[dict[str, Any]] = []
    categorias: list[str] = []
    categorias_formulario: list[dict[str, Any]] = []
    chamado: DetalheView = {}
    comentarios: list[ComentarioView] = []
    rascunho_comentario: str = ""
    historico_status: list[HistoricoStatusView] = []
    consumo_sla: dict[str, str] = {}
    justificativa_rejeicao: str = ""
    enviando_rejeicao: bool = False
    carregando_historico: bool = False
    carregando_sla: bool = False
    mensagem_historico: str = ""
    mensagem_sla: str = ""
    mensagem_rejeicao: str = ""
    mensagem_sucesso_rejeicao: str = ""

    filtro_numero: str = ""
    filtro_status: list[str] = []
    filtro_ativo: list[str] = []
    filtro_data_inicio: str = ""
    filtro_data_fim: str = ""
    filtro_ultima_atualizacao_inicio: str = ""
    filtro_ultima_atualizacao_fim: str = ""
    filtro_numero_confirmado: str = ""
    filtro_status_confirmado: list[str] = []
    filtro_ativo_confirmado: list[str] = []
    filtro_data_inicio_confirmada: str = ""
    filtro_data_fim_confirmada: str = ""
    filtro_ultima_atualizacao_inicio_confirmada: str = ""
    filtro_ultima_atualizacao_fim_confirmada: str = ""
    numero_aplicado: int | None = None
    status_aplicado: list[str] = []
    ativo_id_aplicado: list[int] = []
    data_inicio_aplicada: int | None = None
    data_fim_aplicada: int | None = None
    ultima_atualizacao_inicio_aplicada: int | None = None
    ultima_atualizacao_fim_aplicada: int | None = None
    filtros_aplicados: list[str] = []
    ordenar_por: str = "criado_em"
    direcao: str = "DESC"
    total_chamados: int = 0
    preferencia_filtros_carregada: bool = False
    drawer_totem_aberto: bool = False

    ativo_formulario: str = ""
    categoria_formulario: str = ""
    prioridade_formulario: str = ""
    titulo_formulario: str = ""
    descricao_formulario: str = ""

    carregando_chamados: bool = False
    consulta_chamados_pendente: bool = False
    carregando_formulario: bool = False
    carregando_detalhe: bool = False
    carregando_comentarios: bool = False
    detalhe_carregado: bool = False
    enviando: bool = False
    enviando_comentario: bool = False
    mensagem_chamados: str = ""
    mensagem_formulario: str = ""
    mensagem_detalhe: str = ""
    mensagem_comentarios: str = ""
    mensagem_sucesso: str = ""

    usuario_id_contexto_gerente: int | None = None
    _token_contexto_gerente: str = ""
    _versao_contexto_gerente: int = -1

    def _contexto_sessao_gerente(self) -> tuple[int | None, int, str]:
        return self.usuario_id, self._versao_sessao, self._auth_token

    def _contexto_gerente_atual(self, contexto: tuple[int | None, int, str]) -> bool:
        return (
            self.sessao_confirmada
            and self.role == "gerente"
            and self._contexto_sessao_gerente() == contexto
        )

    def _limpar_contexto_gerente(self) -> None:
        """Descarta dados locais protegidos e preferências da sessão anterior."""
        self.chamados = []
        self.ativos = []
        self.ativos_formulario = []
        self.categorias = []
        self.categorias_formulario = []
        self.chamado = {}
        self.comentarios = []
        self.rascunho_comentario = ""
        self.historico_status = []
        self.consumo_sla = {}
        self.justificativa_rejeicao = ""
        self.enviando_rejeicao = False
        self.carregando_historico = False
        self.carregando_sla = False
        self._limpar_filtros()
        self.filtro_numero_confirmado = ""
        self.filtro_status_confirmado = []
        self.filtro_ativo_confirmado = []
        self.filtro_data_inicio_confirmada = ""
        self.filtro_data_fim_confirmada = ""
        self.filtro_ultima_atualizacao_inicio_confirmada = ""
        self.filtro_ultima_atualizacao_fim_confirmada = ""
        self.ordenar_por = "criado_em"
        self.direcao = "DESC"
        self.total_chamados = 0
        self.preferencia_filtros_carregada = False
        self.drawer_totem_aberto = False
        self._limpar_formulario_local()
        self.carregando_chamados = False
        self.consulta_chamados_pendente = False
        self.carregando_formulario = False
        self.carregando_detalhe = False
        self.carregando_comentarios = False
        self.detalhe_carregado = False
        self.enviando = False
        self.enviando_comentario = False
        self._limpar_mensagens_funcionais()

    def _sincronizar_contexto_gerente(self) -> None:
        """Isola dados ao trocar de identidade ou iniciar outra sessão."""
        if not self.sessao_confirmada or self.role != "gerente" or self.usuario_id is None:
            self._limpar_contexto_gerente()
            self.usuario_id_contexto_gerente = None
            self._token_contexto_gerente = ""
            self._versao_contexto_gerente = -1
            return
        if self.usuario_id_contexto_gerente is not None and (
            self.usuario_id_contexto_gerente != self.usuario_id
            or self._token_contexto_gerente != self._auth_token
            or self._versao_contexto_gerente != self._versao_sessao
        ):
            self._limpar_contexto_gerente()
        self.usuario_id_contexto_gerente = self.usuario_id
        self._token_contexto_gerente = self._auth_token
        self._versao_contexto_gerente = self._versao_sessao

    def _limpar_sessao(self, mensagem: str = "") -> None:
        self._limpar_contexto_gerente()
        self.usuario_id_contexto_gerente = None
        self._token_contexto_gerente = ""
        self._versao_contexto_gerente = -1
        super()._limpar_sessao(mensagem)

    @rx.event
    def sair_gerente(self):
        self._limpar_sessao()
        return rx.redirect("/login")

    @staticmethod
    def prioridades() -> list[str]:
        return list(PRIORIDADES_CHAMADO)

    @staticmethod
    def status_filtros() -> list[str]:
        return [
            "Novo",
            "Em Atendimento",
            "Aguardando Solicitante",
            "Aguardando Mudança",
            "Resolvido",
            "Solução Rejeitada",
            "Encerrado",
            "Cancelado",
        ]

    @staticmethod
    def colunas_ordenaveis() -> list[str]:
        return [
            "numero",
            "titulo",
            "status",
            "prioridade",
            "totem",
            "categoria",
            "criado_em",
            "ultima_atualizacao_em",
        ]

    def _limpar_mensagens_funcionais(self) -> None:
        self.mensagem_chamados = ""
        self.mensagem_formulario = ""
        self.mensagem_detalhe = ""
        self.mensagem_comentarios = ""
        self.mensagem_sucesso = ""
        self.mensagem_historico = ""
        self.mensagem_sla = ""
        self.mensagem_rejeicao = ""
        self.mensagem_sucesso_rejeicao = ""

    def _registrar_erro(self, erro: Exception, destino: str) -> str | None:
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
        if isinstance(erro, XanoIndisponivel):
            setattr(self, destino, MENSAGEM_INDISPONIVEL)
            return None
        if isinstance(erro, XanoContratoInvalido):
            # Erro de contrato em uma consulta de domínio não é prova de que
            # a identidade autenticada deixou de ser válida.
            setattr(self, destino, MENSAGEM_INDISPONIVEL)
            return None
        setattr(self, destino, MENSAGEM_INDISPONIVEL)
        return None

    async def _validar_gerente(self) -> str | None:
        return await self._revalidar("gerente")

    async def _garantir_gerente(self) -> str | None:
        """Evita revalidar /me em cada interação já autenticada da jornada."""
        self._sincronizar_contexto_gerente()
        if self.deve_trocar_senha:
            return DESTINO_PRIMEIRO_ACESSO
        if self.sessao_confirmada and self.role == "gerente" and self._auth_token:
            return None
        destino = await self._validar_gerente()
        self._sincronizar_contexto_gerente()
        return destino

    @rx.event
    async def redirecionar_alias_lista(self):
        revalidar = not (
            self.sessao_confirmada
            and self.role == "gerente"
            and self._auth_token
        )
        if revalidar:
            self._iniciar_carregamento()
            yield
        destino = await self._garantir_gerente()
        if revalidar:
            self._finalizar_carregamento()
        yield rx.redirect(destino or "/inicio")

    @rx.event
    async def redirecionar_alias_novo(self):
        revalidar = not (
            self.sessao_confirmada
            and self.role == "gerente"
            and self._auth_token
        )
        if revalidar:
            self._iniciar_carregamento()
            yield
        destino = await self._garantir_gerente()
        if revalidar:
            self._finalizar_carregamento()
        yield rx.redirect(destino or "/chamados/novo")

    @rx.event
    async def redirecionar_alias_detalhe(self):
        revalidar = not (
            self.sessao_confirmada
            and self.role == "gerente"
            and self._auth_token
        )
        if revalidar:
            self._iniciar_carregamento()
            yield
        destino = await self._garantir_gerente()
        if revalidar:
            self._finalizar_carregamento()
        if destino is not None:
            yield rx.redirect(destino)
            return
        chamado_id = self.router.page.params.get("chamado_id", "")
        yield rx.redirect(f"/chamados/{chamado_id}")

    @staticmethod
    def _id_da_opcao(valor: str) -> int | None:
        if not valor:
            return None
        try:
            resultado = int(valor.split(" — ", 1)[0])
        except (TypeError, ValueError):
            return None
        return resultado if resultado > 0 else None

    @staticmethod
    def _inicio_do_dia(data: str) -> int:
        instante = datetime.strptime(data, "%Y-%m-%d").replace(
            tzinfo=ZoneInfo("America/Sao_Paulo")
        )
        return int(instante.timestamp() * 1000)

    def _preparar_filtros_aplicados(self) -> bool:
        self.mensagem_chamados = ""
        numero_texto = self.filtro_numero.strip()
        if numero_texto:
            try:
                numero = int(numero_texto)
            except ValueError:
                numero = 0
            if numero <= 0:
                self.mensagem_chamados = "Informe um número de chamado válido."
                return False
        else:
            numero = None

        if any(status not in self.status_filtros() for status in self.filtro_status):
            self.mensagem_chamados = "Informe um status válido."
            return False

        ativo_id = [self._id_da_opcao(opcao) for opcao in self.filtro_ativo]
        if any(item is None for item in ativo_id):
            self.mensagem_chamados = "Selecione um Totem válido."
            return False

        try:
            inicio = (
                self._inicio_do_dia(self.filtro_data_inicio)
                if self.filtro_data_inicio
                else None
            )
            fim = (
                self._inicio_do_dia(self.filtro_data_fim) + 86_400_000
                if self.filtro_data_fim
                else None
            )
        except ValueError:
            self.mensagem_chamados = "Informe um período de abertura válido."
            return False

        if inicio is not None and fim is not None and inicio >= fim:
            self.mensagem_chamados = "A data inicial deve ser anterior à data final."
            return False

        try:
            ultima_inicio = self._inicio_do_dia(self.filtro_ultima_atualizacao_inicio) if self.filtro_ultima_atualizacao_inicio else None
            ultima_fim = self._inicio_do_dia(self.filtro_ultima_atualizacao_fim) + 86_400_000 if self.filtro_ultima_atualizacao_fim else None
        except ValueError:
            self.mensagem_chamados = "Informe um período de última atualização válido."
            return False
        if ultima_inicio is not None and ultima_fim is not None and ultima_inicio >= ultima_fim:
            self.mensagem_chamados = "A data inicial deve ser anterior à data final."
            return False

        self.numero_aplicado = numero
        self.status_aplicado = list(self.filtro_status)
        self.ativo_id_aplicado = ativo_id
        self.data_inicio_aplicada = inicio
        self.data_fim_aplicada = fim
        self.ultima_atualizacao_inicio_aplicada = ultima_inicio
        self.ultima_atualizacao_fim_aplicada = ultima_fim

        filtros: list[str] = []
        if numero is not None:
            filtros.append(f"Número: {numero}")
        if self.filtro_status:
            filtros.append(f"Status: {', '.join(self.filtro_status)}")
        if self.filtro_ativo:
            filtros.append(f"Totem: {', '.join(item.split(' — ', 1)[-1] for item in self.filtro_ativo)}")
        if self.filtro_data_inicio:
            filtros.append(f"Abertura a partir de: {self.filtro_data_inicio}")
        if self.filtro_data_fim:
            filtros.append(f"Abertura até: {self.filtro_data_fim}")
        if self.filtro_ultima_atualizacao_inicio:
            filtros.append(f"Atualização a partir de: {self.filtro_ultima_atualizacao_inicio}")
        if self.filtro_ultima_atualizacao_fim:
            filtros.append(f"Atualização até: {self.filtro_ultima_atualizacao_fim}")
        self.filtros_aplicados = filtros
        return True

    def _limpar_filtros(self) -> None:
        self.filtro_numero = ""
        self.filtro_status = []
        self.filtro_ativo = []
        self.filtro_data_inicio = ""
        self.filtro_data_fim = ""
        self.filtro_ultima_atualizacao_inicio = ""
        self.filtro_ultima_atualizacao_fim = ""
        self.numero_aplicado = None
        self.status_aplicado = []
        self.ativo_id_aplicado = []
        self.data_inicio_aplicada = None
        self.data_fim_aplicada = None
        self.ultima_atualizacao_inicio_aplicada = None
        self.ultima_atualizacao_fim_aplicada = None
        self.filtros_aplicados = []

    def _limpar_formulario_local(self) -> None:
        self.ativo_formulario = ""
        self.categoria_formulario = ""
        self.prioridade_formulario = ""
        self.titulo_formulario = ""
        self.descricao_formulario = ""

    @rx.event
    def alterar_filtro_numero(self, valor: str):
        self.filtro_numero = valor

    @rx.event
    def alterar_filtro_status(self, valor: str):
        self.filtro_status = [item for item in self.filtro_status if item != valor] if valor in self.filtro_status else [*self.filtro_status, valor]

    @rx.event
    def alterar_filtro_ativo(self, valor: str):
        self.filtro_ativo = [item for item in self.filtro_ativo if item != valor] if valor in self.filtro_ativo else [*self.filtro_ativo, valor]

    @rx.event
    def alterar_filtro_data_inicio(self, valor: str):
        self.filtro_data_inicio = valor

    @rx.event
    def alterar_filtro_data_fim(self, valor: str):
        self.filtro_data_fim = valor

    @rx.event
    def alterar_periodo_abertura(self, inicio: str, fim: str):
        self.filtro_data_inicio = inicio
        self.filtro_data_fim = fim

    @rx.event
    def alterar_filtro_ultima_atualizacao_inicio(self, valor: str):
        self.filtro_ultima_atualizacao_inicio = valor

    @rx.event
    def alterar_filtro_ultima_atualizacao_fim(self, valor: str):
        self.filtro_ultima_atualizacao_fim = valor

    @rx.event
    def alterar_periodo_atualizacao(self, inicio: str, fim: str):
        self.filtro_ultima_atualizacao_inicio = inicio
        self.filtro_ultima_atualizacao_fim = fim

    def _aplicar_preferencia(self, preferencia) -> None:
        self.numero_aplicado = preferencia.numero
        self.status_aplicado = list(preferencia.status)
        self.ativo_id_aplicado = list(preferencia.ativo_ids)
        self.data_inicio_aplicada = preferencia.data_inicio
        self.data_fim_aplicada = preferencia.data_fim
        self.ultima_atualizacao_inicio_aplicada = preferencia.ultima_atualizacao_inicio
        self.ultima_atualizacao_fim_aplicada = preferencia.ultima_atualizacao_fim
        self.filtro_numero = str(preferencia.numero) if preferencia.numero else ""
        self.filtro_status = list(self.status_aplicado)
        self.filtro_data_inicio = self._data_do_timestamp(preferencia.data_inicio)
        self.filtro_data_fim = self._data_do_timestamp(preferencia.data_fim - 86_400_000) if preferencia.data_fim else ""
        self.filtro_ultima_atualizacao_inicio = self._data_do_timestamp(preferencia.ultima_atualizacao_inicio)
        self.filtro_ultima_atualizacao_fim = self._data_do_timestamp(preferencia.ultima_atualizacao_fim - 86_400_000) if preferencia.ultima_atualizacao_fim else ""
        self._sincronizar_totem_e_etiquetas()
        self._confirmar_filtros()

    def _sincronizar_totem_e_etiquetas(self) -> None:
        self.filtro_ativo = [item for item in self.ativos if self._id_da_opcao(item) in self.ativo_id_aplicado]
        filtros: list[str] = []
        if self.numero_aplicado is not None:
            filtros.append(f"Número: {self.numero_aplicado}")
        if self.status_aplicado:
            filtros.append(f"Status: {', '.join(self.status_aplicado)}")
        if self.filtro_ativo:
            filtros.append(f"Totem: {', '.join(item.split(' — ', 1)[-1] for item in self.filtro_ativo)}")
        if self.filtro_data_inicio:
            filtros.append(f"Abertura a partir de: {self.filtro_data_inicio}")
        if self.filtro_data_fim:
            filtros.append(f"Abertura até: {self.filtro_data_fim}")
        if self.filtro_ultima_atualizacao_inicio:
            filtros.append(f"Atualização a partir de: {self.filtro_ultima_atualizacao_inicio}")
        if self.filtro_ultima_atualizacao_fim:
            filtros.append(f"Atualização até: {self.filtro_ultima_atualizacao_fim}")
        self.filtros_aplicados = filtros

    def _confirmar_filtros(self) -> None:
        self.filtro_numero_confirmado = self.filtro_numero
        self.filtro_status_confirmado = list(self.filtro_status)
        self.filtro_ativo_confirmado = list(self.filtro_ativo)
        self.filtro_data_inicio_confirmada = self.filtro_data_inicio
        self.filtro_data_fim_confirmada = self.filtro_data_fim
        self.filtro_ultima_atualizacao_inicio_confirmada = (
            self.filtro_ultima_atualizacao_inicio
        )
        self.filtro_ultima_atualizacao_fim_confirmada = (
            self.filtro_ultima_atualizacao_fim
        )

    def _snapshot_filtros_confirmados(self):
        return (
            self.filtro_numero_confirmado, self.filtro_status_confirmado,
            self.filtro_ativo_confirmado, self.filtro_data_inicio_confirmada,
            self.filtro_data_fim_confirmada,
            self.filtro_ultima_atualizacao_inicio_confirmada,
            self.filtro_ultima_atualizacao_fim_confirmada, self.numero_aplicado,
            self.status_aplicado, self.ativo_id_aplicado,
            self.data_inicio_aplicada, self.data_fim_aplicada,
            self.ultima_atualizacao_inicio_aplicada,
            self.ultima_atualizacao_fim_aplicada, list(self.filtros_aplicados),
        )

    def _restaurar_filtros_confirmados(self, snapshot) -> None:
        (
            self.filtro_numero_confirmado, self.filtro_status_confirmado,
            self.filtro_ativo_confirmado, self.filtro_data_inicio_confirmada,
            self.filtro_data_fim_confirmada,
            self.filtro_ultima_atualizacao_inicio_confirmada,
            self.filtro_ultima_atualizacao_fim_confirmada, self.numero_aplicado,
            self.status_aplicado, self.ativo_id_aplicado,
            self.data_inicio_aplicada, self.data_fim_aplicada,
            self.ultima_atualizacao_inicio_aplicada,
            self.ultima_atualizacao_fim_aplicada, self.filtros_aplicados,
        ) = snapshot
        self.filtro_numero = self.filtro_numero_confirmado
        self.filtro_status = list(self.filtro_status_confirmado)
        self.filtro_ativo = list(self.filtro_ativo_confirmado)
        self.filtro_data_inicio = self.filtro_data_inicio_confirmada
        self.filtro_data_fim = self.filtro_data_fim_confirmada
        self.filtro_ultima_atualizacao_inicio = self.filtro_ultima_atualizacao_inicio_confirmada
        self.filtro_ultima_atualizacao_fim = self.filtro_ultima_atualizacao_fim_confirmada

    @staticmethod
    def _data_do_timestamp(instante: int | None) -> str:
        if instante is None:
            return ""
        return datetime.fromtimestamp(instante / 1000, tz=ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d")

    async def _salvar_preferencia(
        self, contexto: tuple[int | None, int, str]
    ) -> None:
        cliente = criar_cliente_service_desk()
        if not hasattr(cliente, "salvar_preferencia_filtros_gerente"):
            return
        await cliente.salvar_preferencia_filtros_gerente(
            self._auth_token, numero=self.numero_aplicado, status=self.status_aplicado,
            ativo_ids=self.ativo_id_aplicado, data_inicio=self.data_inicio_aplicada,
            data_fim=self.data_fim_aplicada,
            ultima_atualizacao_inicio=self.ultima_atualizacao_inicio_aplicada,
            ultima_atualizacao_fim=self.ultima_atualizacao_fim_aplicada,
        )
        if self._contexto_gerente_atual(contexto):
            self._confirmar_filtros()

    @rx.event
    def alterar_ativo_formulario(self, valor: str):
        self.ativo_formulario = valor

    @rx.event
    def alterar_categoria_formulario(self, valor: str):
        self.categoria_formulario = valor

    @rx.event
    def alterar_prioridade_formulario(self, valor: str):
        self.prioridade_formulario = valor

    @rx.event
    def alterar_titulo_formulario(self, valor: str):
        self.titulo_formulario = valor

    @rx.event
    def alterar_descricao_formulario(self, valor: str):
        self.descricao_formulario = valor

    @rx.event
    async def carregar_lista(self):
        self._sincronizar_contexto_gerente()
        if self.carregando_chamados:
            # Eventos rápidos de ordenação/filtro não abrem uma segunda
            # consulta concorrente. A última intenção será atendida pela
            # carga que já está em andamento, sem criar um request storm.
            self.consulta_chamados_pendente = True
            return
        self.carregando_chamados = True
        self._limpar_mensagens_funcionais()
        yield
        contexto = None
        try:
            while True:
                self.consulta_chamados_pendente = False
                destino = await self._garantir_gerente()
                if destino is not None:
                    yield rx.redirect(destino)
                    return
                if not self.sessao_confirmada:
                    return
                contexto = self._contexto_sessao_gerente()

                cliente = criar_cliente_service_desk()
                if not self.preferencia_filtros_carregada and hasattr(cliente, "obter_preferencia_filtros_gerente"):
                    preferencia = await cliente.obter_preferencia_filtros_gerente(self._auth_token)
                    if not self._contexto_gerente_atual(contexto):
                        return
                    self._aplicar_preferencia(preferencia)
                    self.preferencia_filtros_carregada = True
                filtros_consulta = {
                    "numero": self.numero_aplicado,
                    "status": self.status_aplicado,
                    "ativo_ids": self.ativo_id_aplicado,
                    "data_inicio": self.data_inicio_aplicada,
                    "data_fim": self.data_fim_aplicada,
                    "ordenar_por": self.ordenar_por,
                    "direcao": self.direcao,
                }
                if self.ultima_atualizacao_inicio_aplicada is not None:
                    filtros_consulta["ultima_atualizacao_inicio"] = self.ultima_atualizacao_inicio_aplicada
                if self.ultima_atualizacao_fim_aplicada is not None:
                    filtros_consulta["ultima_atualizacao_fim"] = self.ultima_atualizacao_fim_aplicada
                chamada = cliente.listar_chamados(self._auth_token, **filtros_consulta)
                if self.ativos:
                    resultado = await chamada
                    ativos = None
                else:
                    resultado, ativos = await asyncio.gather(
                        chamada,
                        cliente.listar_ativos_historicos_gerente(self._auth_token),
                        return_exceptions=True,
                    )
                    if not self._contexto_gerente_atual(contexto):
                        return
                    if isinstance(resultado, Exception):
                        raise resultado
                    if isinstance(ativos, Exception):
                        destino_ativos = self._registrar_erro(
                            ativos,
                            "mensagem_chamados",
                        )
                        if destino_ativos is not None:
                            yield rx.redirect(destino_ativos)
                            return
                        ativos = None

                if not self._contexto_gerente_atual(contexto):
                    return

                self.chamados = [
                    _resumo_para_dict(item) for item in resultado.items
                ]
                self.total_chamados = resultado.total
                if ativos is not None:
                    self.ativos = [
                        f"{item.id} — {item.nome_ativo}" for item in ativos
                    ]
                    self._sincronizar_totem_e_etiquetas()
                    if self.ativo_id_aplicado and not self.filtro_ativo_confirmado:
                        self._confirmar_filtros()

                # Só repete automaticamente quando a consulta anterior
                # terminou com sucesso e houve uma nova intenção concorrente.
                # Em falha transitória, a próxima ação explícita faz a nova
                # tentativa, evitando retry agressivo e novo 429.
                if not self.consulta_chamados_pendente:
                    break
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            if contexto is not None and not self._contexto_gerente_atual(contexto):
                return
            destino = self._registrar_erro(erro, "mensagem_chamados")
            if destino is not None:
                yield rx.redirect(destino)
                return
        finally:
            if contexto is None or self._contexto_sessao_gerente() == contexto:
                self.carregando_chamados = False

    @rx.event
    async def aplicar_filtros(self):
        self._sincronizar_contexto_gerente()
        contexto = self._contexto_sessao_gerente()
        filtros_confirmados = self._snapshot_filtros_confirmados()
        chamados_confirmados, total_confirmado = list(self.chamados), self.total_chamados
        if not self._preparar_filtros_aplicados():
            return
        async for evento in self.carregar_lista():
            yield evento
        if not self._contexto_gerente_atual(contexto):
            return
        if not self.mensagem_chamados:
            try:
                await self._salvar_preferencia(contexto)
            except Exception as erro:  # noqa: BLE001
                if not self._contexto_gerente_atual(contexto):
                    return
                self._registrar_erro(erro, "mensagem_chamados")
                self._restaurar_filtros_confirmados(filtros_confirmados)
                self.chamados, self.total_chamados = chamados_confirmados, total_confirmado
        else:
            self._restaurar_filtros_confirmados(filtros_confirmados)
            self.chamados, self.total_chamados = chamados_confirmados, total_confirmado

    @rx.event
    async def limpar_filtros_lista(self):
        self._sincronizar_contexto_gerente()
        contexto = self._contexto_sessao_gerente()
        filtros_confirmados = self._snapshot_filtros_confirmados()
        chamados_confirmados, total_confirmado = list(self.chamados), self.total_chamados
        self._limpar_filtros()
        async for evento in self.carregar_lista():
            yield evento
        if not self._contexto_gerente_atual(contexto):
            return
        if not self.mensagem_chamados:
            try:
                await self._salvar_preferencia(contexto)
            except Exception as erro:  # noqa: BLE001
                if not self._contexto_gerente_atual(contexto):
                    return
                self._registrar_erro(erro, "mensagem_chamados")
                self._restaurar_filtros_confirmados(filtros_confirmados)
                self.chamados, self.total_chamados = chamados_confirmados, total_confirmado
        else:
            self._restaurar_filtros_confirmados(filtros_confirmados)
            self.chamados, self.total_chamados = chamados_confirmados, total_confirmado

    @rx.event
    def abrir_drawer_totem(self):
        self.drawer_totem_aberto = bool(self.chamado.get("resumo_totem"))

    @rx.event
    def fechar_drawer_totem(self):
        self.drawer_totem_aberto = False

    @rx.event
    def definir_drawer_totem_aberto(self, aberto: bool):
        self.drawer_totem_aberto = aberto

    @rx.event
    async def alternar_ordenacao(self, coluna: str):
        self._sincronizar_contexto_gerente()
        if coluna not in self.colunas_ordenaveis():
            self.mensagem_chamados = "Ordenação inválida."
            return
        if coluna == self.ordenar_por:
            self.direcao = "ASC" if self.direcao == "DESC" else "DESC"
        else:
            self.ordenar_por = coluna
            self.direcao = "ASC"
        async for evento in self.carregar_lista():
            yield evento

    @rx.event
    async def carregar_formulario(self):
        self._sincronizar_contexto_gerente()
        if self.carregando_formulario:
            return
        self.carregando_formulario = True
        self._limpar_mensagens_funcionais()
        yield
        destino = await self._garantir_gerente()
        if destino is not None:
            self.carregando_formulario = False
            yield rx.redirect(destino)
            return
        if not self.sessao_confirmada:
            self.carregando_formulario = False
            return
        contexto = self._contexto_sessao_gerente()
        try:
            cliente = criar_cliente_service_desk()
            ativos, categorias = await asyncio.gather(
                cliente.listar_ativos(self._auth_token),
                cliente.listar_categorias(self._auth_token),
            )
            if not self._contexto_gerente_atual(contexto):
                return
            self.ativos = [f"{item.id} — {item.nome_ativo}" for item in ativos]
            self.ativos_formulario = [
                {"id": item.id, "nome": item.nome_ativo} for item in ativos
            ]
            self.categorias = [f"{item.id} — {item.nome}" for item in categorias]
            self.categorias_formulario = [
                {"id": item.id, "nome": item.nome} for item in categorias
            ]
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            if not self._contexto_gerente_atual(contexto):
                return
            destino = self._registrar_erro(erro, "mensagem_formulario")
            if destino is not None:
                self.carregando_formulario = False
                yield rx.redirect(destino)
                return
        if self._contexto_sessao_gerente() == contexto:
            self.carregando_formulario = False

    @rx.event
    async def carregar_detalhe(self):
        self._sincronizar_contexto_gerente()
        if self.carregando_detalhe:
            return
        self.carregando_detalhe = True
        self.detalhe_carregado = False
        self.chamado = {}
        self.comentarios = []
        self.rascunho_comentario = ""
        self.historico_status = []
        self.consumo_sla = {}
        self.justificativa_rejeicao = ""
        self._limpar_mensagens_funcionais()
        yield
        destino = await self._garantir_gerente()
        if destino is not None:
            self.carregando_detalhe = False
            yield rx.redirect(destino)
            return
        if not self.sessao_confirmada:
            self.carregando_detalhe = False
            return
        contexto = self._contexto_sessao_gerente()
        try:
            chamado_id = int(str(self.chamado_id))
            if chamado_id <= 0:
                raise ValueError
        except (AttributeError, TypeError, ValueError):
            self.mensagem_detalhe = "Chamado não encontrado."
            self.carregando_detalhe = False
            return
        try:
            cliente = criar_cliente_service_desk()
            resultado = await cliente.obter_chamado(self._auth_token, chamado_id)
            if not self._contexto_gerente_atual(contexto):
                return
            self.chamado = _detalhe_para_dict(resultado)
            self.detalhe_carregado = True
            self.carregando_comentarios = True
            try:
                comentarios = await cliente.listar_comentarios_publicos(
                    self._auth_token,
                    chamado_id,
                )
                if not self._contexto_gerente_atual(contexto):
                    return
                self.comentarios = [
                    comentario_publico_para_dict(comentario)
                    for comentario in comentarios
                ]
            except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
                if not self._contexto_gerente_atual(contexto):
                    return
                destino = self._registrar_erro(erro, "mensagem_comentarios")
                if destino is not None:
                    self.carregando_detalhe = False
                    yield rx.redirect(destino)
                    return
            finally:
                if self._contexto_sessao_gerente() == contexto:
                    self.carregando_comentarios = False
            self.carregando_sla = True
            try:
                consumo = await cliente.obter_consumo_sla_gerente(self._auth_token, chamado_id)
                if not self._contexto_gerente_atual(contexto):
                    return
                self.consumo_sla = consumo_sla_para_dict(consumo)
            except Exception as erro:  # noqa: BLE001
                if not self._contexto_gerente_atual(contexto):
                    return
                destino = self._registrar_erro(erro, "mensagem_sla")
                if destino is not None:
                    yield rx.redirect(destino)
                    return
            finally:
                self.carregando_sla = False
            self.carregando_historico = True
            try:
                itens = await cliente.listar_historico_status_gerente(self._auth_token, chamado_id)
                if not self._contexto_gerente_atual(contexto):
                    return
                self.historico_status = [historico_status_para_dict(item) for item in itens]
            except Exception as erro:  # noqa: BLE001
                if not self._contexto_gerente_atual(contexto):
                    return
                destino = self._registrar_erro(erro, "mensagem_historico")
                if destino is not None:
                    yield rx.redirect(destino)
                    return
            finally:
                self.carregando_historico = False
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            if not self._contexto_gerente_atual(contexto):
                return
            destino = self._registrar_erro(erro, "mensagem_detalhe")
            if destino is not None:
                self.carregando_detalhe = False
                yield rx.redirect(destino)
            return
        if self._contexto_sessao_gerente() == contexto:
            self.carregando_detalhe = False

    @rx.event
    async def publicar_comentario(self):
        self._sincronizar_contexto_gerente()
        if self.enviando_comentario:
            return
        self.enviando_comentario = True
        self.mensagem_comentarios = ""
        yield
        destino = await self._garantir_gerente()
        if destino is not None:
            self.enviando_comentario = False
            yield rx.redirect(destino)
            return
        if not self.sessao_confirmada:
            self.enviando_comentario = False
            return
        contexto = self._contexto_sessao_gerente()
        try:
            chamado_id = int(str(self.chamado_id))
            if chamado_id <= 0:
                raise ValueError
        except (AttributeError, TypeError, ValueError):
            self.mensagem_comentarios = "Chamado não encontrado."
            self.enviando_comentario = False
            return
        try:
            cliente = criar_cliente_service_desk()
            comentario = await cliente.criar_comentario_publico(
                self._auth_token,
                chamado_id,
                conteudo=self.rascunho_comentario,
            )
            if not self._contexto_gerente_atual(contexto):
                return
            self.comentarios = [comentario_publico_para_dict(comentario)] + self.comentarios
            self.rascunho_comentario = ""
            self.mensagem_sucesso = "Comentário publicado."
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            if not self._contexto_gerente_atual(contexto):
                return
            destino = self._registrar_erro(erro, "mensagem_comentarios")
            if destino is not None:
                self.enviando_comentario = False
                yield rx.redirect(destino)
            self.enviando_comentario = False
            return
        try:
            resultado = await cliente.obter_chamado(self._auth_token, chamado_id)
            if not self._contexto_gerente_atual(contexto):
                return
            self.chamado = _detalhe_para_dict(resultado)
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            if not self._contexto_gerente_atual(contexto):
                return
            destino = self._registrar_erro(erro, "mensagem_detalhe")
            if destino is not None:
                self.enviando_comentario = False
                yield rx.redirect(destino)
                return
        if self._contexto_sessao_gerente() == contexto:
            self.enviando_comentario = False

    @rx.event
    def alterar_justificativa_rejeicao(self, valor: str):
        self.justificativa_rejeicao = valor

    @rx.event
    async def rejeitar_solucao(self):
        if self.enviando_rejeicao:
            return
        self.mensagem_rejeicao = ""
        self.mensagem_sucesso_rejeicao = ""
        justificativa = self.justificativa_rejeicao.strip()
        if not justificativa:
            self.mensagem_rejeicao = "Informe a justificativa da rejeição."
            return
        if not self.detalhe_carregado or self.chamado.get("status") != "Resolvido":
            self.mensagem_rejeicao = "O chamado não está Resolvido."
            return
        self.enviando_rejeicao = True
        yield
        destino = await self._garantir_gerente()
        if destino is not None:
            self.enviando_rejeicao = False
            yield rx.redirect(destino)
            return
        contexto = self._contexto_sessao_gerente()
        chamado_id = self.chamado["id"]
        try:
            cliente = criar_cliente_service_desk()
            confirmado = await cliente.rejeitar_solucao(
                self._auth_token, chamado_id, justificativa=justificativa,
                ultima_atualizacao_em=self.chamado["ultima_atualizacao_em"],
            )
            if not self._contexto_gerente_atual(contexto):
                return
            self.chamado = _detalhe_para_dict(confirmado)
            self.justificativa_rejeicao = ""
            self.mensagem_sucesso_rejeicao = "Solução rejeitada."
            self.consumo_sla = {}
            self.historico_status = []
            try:
                comentarios = await cliente.listar_comentarios_publicos(self._auth_token, chamado_id)
                if self._contexto_gerente_atual(contexto):
                    self.comentarios = [comentario_publico_para_dict(item) for item in comentarios]
            except Exception as erro:  # noqa: BLE001
                destino = self._registrar_erro(erro, "mensagem_comentarios")
                if destino is not None:
                    yield rx.redirect(destino)
                    return
            if not self._contexto_gerente_atual(contexto):
                return
            try:
                consumo = await cliente.obter_consumo_sla_gerente(self._auth_token, chamado_id)
                if self._contexto_gerente_atual(contexto):
                    self.consumo_sla = consumo_sla_para_dict(consumo)
            except Exception as erro:  # noqa: BLE001
                destino = self._registrar_erro(erro, "mensagem_sla")
                if destino is not None:
                    yield rx.redirect(destino)
                    return
            if not self._contexto_gerente_atual(contexto):
                return
            try:
                itens = await cliente.listar_historico_status_gerente(self._auth_token, chamado_id)
                if self._contexto_gerente_atual(contexto):
                    self.historico_status = [historico_status_para_dict(item) for item in itens]
            except Exception as erro:  # noqa: BLE001
                destino = self._registrar_erro(erro, "mensagem_historico")
                if destino is not None:
                    yield rx.redirect(destino)
                    return
        except XanoConflito:
            if self._contexto_gerente_atual(contexto):
                self.mensagem_rejeicao = "O chamado mudou. Confira o detalhe atualizado antes de tentar novamente."
                try:
                    atualizado = await cliente.obter_chamado(self._auth_token, chamado_id)
                    if self._contexto_gerente_atual(contexto):
                        self.chamado = _detalhe_para_dict(atualizado)
                        self.consumo_sla = {}
                        self.historico_status = []
                        try:
                            consumo = await cliente.obter_consumo_sla_gerente(self._auth_token, chamado_id)
                            if self._contexto_gerente_atual(contexto):
                                self.consumo_sla = consumo_sla_para_dict(consumo)
                        except Exception as erro:  # noqa: BLE001
                            destino = self._registrar_erro(erro, "mensagem_sla")
                            if destino is not None:
                                yield rx.redirect(destino)
                                return
                except Exception as erro:  # noqa: BLE001
                    self._registrar_erro(erro, "mensagem_detalhe")
        except Exception as erro:  # noqa: BLE001
            if self._contexto_gerente_atual(contexto):
                destino = self._registrar_erro(erro, "mensagem_rejeicao")
                if destino is not None:
                    yield rx.redirect(destino)
        finally:
            if self._contexto_sessao_gerente() == contexto:
                self.enviando_rejeicao = False

    @rx.event
    def descartar_rascunho_comentario(self):
        """Descarta somente o rascunho local, sem chamada ao backend."""
        self.rascunho_comentario = ""

    @rx.event
    def alterar_rascunho_comentario(self, conteudo: str):
        """Mantém o rascunho exclusivamente no State local."""
        self.rascunho_comentario = conteudo

    @rx.event
    async def abrir_chamado(self, form_data: dict[str, Any] | None = None):
        self._sincronizar_contexto_gerente()
        if self.enviando:
            return
        self.enviando = True
        self.mensagem_formulario = ""
        self.mensagem_sucesso = ""
        yield
        destino = await self._garantir_gerente()
        if destino is not None:
            self.enviando = False
            yield rx.redirect(destino)
            return
        if not self.sessao_confirmada:
            self.enviando = False
            return
        contexto = self._contexto_sessao_gerente()
        if isinstance(form_data, dict) and any(
            k in form_data
            for k in ("ativos_referencia_id", "categorias_servico_id", "titulo")
        ):
            dados = form_data
        else:
            dados = {
                "ativos_referencia_id": self.ativo_formulario,
                "categorias_servico_id": self.categoria_formulario,
                "prioridade": self.prioridade_formulario,
                "titulo": self.titulo_formulario,
                "descricao": self.descricao_formulario,
            }
        ativo_id = self._id_da_opcao(str(dados.get("ativos_referencia_id", "")))
        categoria_id = self._id_da_opcao(
            str(dados.get("categorias_servico_id", ""))
        )
        if ativo_id is None or categoria_id is None:
            self.mensagem_formulario = "Selecione um ativo e uma categoria."
            self.enviando = False
            return
        try:
            resultado = await criar_cliente_service_desk().abrir_chamado(
                self._auth_token,
                ativos_referencia_id=ativo_id,
                categorias_servico_id=categoria_id,
                prioridade=str(dados.get("prioridade", "")),
                titulo=str(dados.get("titulo", "")),
                descricao=str(dados.get("descricao", "")),
            )
            if not self._contexto_gerente_atual(contexto):
                return
            self.chamado = _detalhe_para_dict(resultado)
            self._limpar_formulario_local()
            self.enviando = False
            yield rx.toast.success("Chamado aberto com sucesso.")
            yield rx.redirect(f"/chamados/{resultado.id}")
            return
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            if not self._contexto_gerente_atual(contexto):
                return
            destino = self._registrar_erro(erro, "mensagem_formulario")
            self.enviando = False
            if destino is not None:
                yield rx.redirect(destino)
                return

    @rx.event
    def limpar_formulario(self):
        """Limpa apenas o rascunho local da abertura manual."""
        self._limpar_formulario_local()
        self.mensagem_formulario = ""

    @rx.event
    def descartar_formulario(self):
        """Abandona o rascunho sem executar mutação no backend."""
        self._limpar_formulario_local()
        self.mensagem_formulario = ""
        return rx.redirect("/inicio")

    @rx.event
    def voltar_para_lista(self):
        """Navega sem alterar nem descartar explicitamente o rascunho."""
        return rx.redirect("/inicio")
