"""State da fila técnica e da assunção de chamados."""

from __future__ import annotations

import reflex as rx
from datetime import datetime
from zoneinfo import ZoneInfo

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
    MENSAGEM_INDISPONIVEL,
    MENSAGEM_NAO_AUTORIZADO,
    AuthState,
)


class ChamadosTecnicoState(AuthState):
    """Mantém a fila global e as operações de responsável do chamado."""

    filtro_numero: str = ""
    filtro_status: str = ""
    filtro_ativo: str = ""
    filtro_data_inicio: str = ""
    filtro_data_fim: str = ""
    filtro_numero_confirmado: str = ""
    filtro_status_confirmado: str = ""
    filtro_ativo_confirmado: str = ""
    filtro_data_inicio_confirmada: str = ""
    filtro_data_fim_confirmada: str = ""
    numero_aplicado: int | None = None
    status_aplicado: str = ""
    ativo_id_aplicado: int | None = None
    data_inicio_aplicada: int | None = None
    data_fim_aplicada: int | None = None
    filtros_aplicados: list[str] = []
    escopo_rapido: str = "todos"
    ativos: list[str] = []
    total_chamados: int = 0
    chamados: list[TecnicoView] = []
    chamado: DetalheView = {}
    timeline: list[TimelineView] = []
    tecnicos: list[TecnicoOpcaoView] = []
    categorias_tratativa: list[TecnicoOpcaoView] = []
    tecnico_alvo_id: str = ""
    responsavel_confirmado_id: int | None = None
    status_confirmado: str = ""
    prioridade_confirmada: str = ""
    categoria_confirmada_id: int | None = None
    ultima_atualizacao_confirmada: int | None = None
    responsavel_pendente_id: str = "0"
    status_pendente: str = ""
    prioridade_pendente: str = ""
    categoria_pendente_id: str = ""
    comentario_status_pendente: str = ""
    visibilidade_comentario_status_pendente: str = "publica"
    carregando_fila: bool = False
    carregando_detalhe_tecnico: bool = False
    salvando_tratativa: bool = False
    detalhe_tecnico_carregado: bool = False
    assumindo_id: int | None = None
    alterando_responsavel_id: int | None = None
    mensagem_fila: str = ""
    mensagem_detalhe_tecnico: str = ""
    mensagem_assuncao: str = ""
    mensagem_responsavel: str = ""
    mensagem_sucesso_responsavel: str = ""
    mensagem_tratativa: str = ""
    mensagem_sucesso_tratativa: str = ""

    @staticmethod
    def status_filtros() -> list[str]:
        return ["Novo", "Em Atendimento", "Aguardando Solicitante", "Aguardando Mudança", "Resolvido", "Solução Rejeitada", "Encerrado", "Cancelado"]

    @staticmethod
    def prioridades_tratativa() -> list[str]:
        return ["Baixa", "Média", "Alta", "Urgente"]

    @staticmethod
    def _status_exige_comentario_publico(status: str) -> bool:
        return status in {
            "Resolvido",
            "Aguardando Solicitante",
            "Cancelado",
        }

    @rx.var
    def edicao_funcional_bloqueada(self) -> bool:
        return self.status_confirmado in {"Encerrado", "Cancelado"}

    @rx.var
    def status_pendente_alterado(self) -> bool:
        return self.status_pendente != self.status_confirmado

    @rx.var
    def status_pendente_exige_comentario_publico(self) -> bool:
        return self._status_exige_comentario_publico(self.status_pendente)

    @rx.var
    def ha_mudanca_funcional_pendente(self) -> bool:
        return (
            self.responsavel_pendente_id
            != self._valor_responsavel_confirmado()
            or self.status_pendente != self.status_confirmado
            or self.prioridade_pendente != self.prioridade_confirmada
            or self.categoria_pendente_id
            != self._valor_categoria_confirmada()
        )

    @rx.var
    def pode_salvar_tratativa(self) -> bool:
        if self.edicao_funcional_bloqueada or not self.ha_mudanca_funcional_pendente:
            return False
        if not self.status_pendente_alterado:
            return True
        if not self.comentario_status_pendente.strip():
            return False
        if self.status_pendente_exige_comentario_publico:
            return self.visibilidade_comentario_status_pendente == "publica"
        return self.visibilidade_comentario_status_pendente in {"publica", "interna"}

    @rx.var
    def categoria_confirmada_inativa(self) -> bool:
        return (
            self.categoria_confirmada_id is not None
            and all(
                categoria["id"] != self.categoria_confirmada_id
                for categoria in self.categorias_tratativa
            )
        )

    def _limpar_mensagens_tecnico(self) -> None:
        self.mensagem_fila = ""
        self.mensagem_detalhe_tecnico = ""
        self.mensagem_assuncao = ""
        self.mensagem_responsavel = ""
        self.mensagem_sucesso_responsavel = ""
        self.mensagem_tratativa = ""
        self.mensagem_sucesso_tratativa = ""

    def _valor_responsavel_confirmado(self) -> str:
        return str(self.responsavel_confirmado_id or 0)

    def _valor_categoria_confirmada(self) -> str:
        return str(self.categoria_confirmada_id or "")

    def _copiar_confirmado_para_pendente(self) -> None:
        self.responsavel_pendente_id = self._valor_responsavel_confirmado()
        self.status_pendente = self.status_confirmado
        self.prioridade_pendente = self.prioridade_confirmada
        self.categoria_pendente_id = self._valor_categoria_confirmada()
        self.comentario_status_pendente = ""
        self.visibilidade_comentario_status_pendente = "publica"

    @staticmethod
    def _id_pendente(valor: str, *, permitir_nao_atribuido: bool = False) -> int | None:
        if permitir_nao_atribuido and valor == "0":
            return None
        try:
            resultado = int(valor)
        except (TypeError, ValueError):
            return None
        return resultado if resultado > 0 else None

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

    def _atualizar_detalhe(
        self,
        detalhe: DetalheChamadoTecnico,
        categorias: list[TecnicoOpcaoView] | None = None,
    ) -> None:
        self._atualizar_chamado(detalhe.chamado)
        self.timeline = [
            evento_timeline_para_dict(evento) for evento in detalhe.timeline
        ]
        self.tecnicos = [
            {"id": tecnico.id, "nome": tecnico.nome}
            for tecnico in detalhe.tecnicos
        ]
        if categorias is not None:
            self.categorias_tratativa = categorias
        self.responsavel_confirmado_id = (
            detalhe.chamado.tecnico.id
            if detalhe.chamado.tecnico is not None
            else None
        )
        self.status_confirmado = detalhe.chamado.status or ""
        self.prioridade_confirmada = detalhe.chamado.prioridade
        self.categoria_confirmada_id = detalhe.chamado.categoria.id
        self.ultima_atualizacao_confirmada = (
            detalhe.chamado.ultima_atualizacao_em
        )
        self._copiar_confirmado_para_pendente()
        self.tecnico_alvo_id = ""
        self.detalhe_tecnico_carregado = True

    async def _validar_tecnico(self) -> str | None:
        return await self._revalidar("tecnico")

    async def _validar_acesso_fila(self) -> str | None:
        if (
            self.sessao_confirmada
            and self._auth_token
            and self.role in {"tecnico", "diretoria", "administrador"}
        ):
            return None
        destino = await self._revalidar()
        if destino is not None:
            return destino
        if self.role not in {"tecnico", "diretoria", "administrador"}:
            return self.destino_por_perfil(self.role) or "/login"
        return None

    def _registrar_erro_fila(self, erro: Exception) -> str | None:
        if isinstance(erro, XanoNaoAutenticado):
            self._limpar_sessao(MENSAGEM_EXPIRADA)
            return "/login"
        if isinstance(erro, XanoNaoAutorizado):
            self.mensagem_fila = MENSAGEM_NAO_AUTORIZADO
            return None
        if isinstance(erro, XanoEntradaInvalida):
            self.mensagem_fila = "Os filtros informados são inválidos."
            return None
        if isinstance(erro, XanoIndisponivel):
            self.mensagem_fila = MENSAGEM_INDISPONIVEL
            return None
        if isinstance(erro, XanoContratoInvalido):
            self.mensagem_fila = (
                "Não foi possível carregar a fila porque a resposta do serviço é incompatível."
            )
            return None
        self.mensagem_fila = MENSAGEM_INDISPONIVEL
        return None

    def _registrar_erro_tecnico(self, erro: Exception, destino: str) -> str | None:
        """Mantém o tratamento específico de detalhe e ações de responsável."""
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
            mensagem = (
                "Não foi possível carregar os dados porque a resposta do serviço é incompatível."
                if destino == "mensagem_detalhe_tecnico"
                else "Não foi possível concluir a operação porque a resposta do serviço é incompatível."
            )
            setattr(self, destino, mensagem)
            return None
        setattr(self, destino, MENSAGEM_INDISPONIVEL)
        return None

    @rx.event
    def alterar_filtro_numero(self, valor: str) -> None: self.filtro_numero = valor
    @rx.event
    def alterar_filtro_status(self, valor: str) -> None: self.filtro_status = valor
    @rx.event
    def alterar_filtro_ativo(self, valor: str) -> None: self.filtro_ativo = valor
    @rx.event
    def alterar_filtro_data_inicio(self, valor: str) -> None: self.filtro_data_inicio = valor
    @rx.event
    def alterar_filtro_data_fim(self, valor: str) -> None: self.filtro_data_fim = valor

    @rx.event
    def alterar_responsavel_pendente(self, valor: str) -> None:
        if self.edicao_funcional_bloqueada:
            return
        tecnico_id = self._id_pendente(valor, permitir_nao_atribuido=True)
        if valor == "0" or tecnico_id in {item["id"] for item in self.tecnicos}:
            self.responsavel_pendente_id = valor

    @rx.event
    def alterar_status_pendente(self, valor: str) -> None:
        if self.edicao_funcional_bloqueada or valor not in self.status_filtros():
            return
        self.status_pendente = valor
        if self._status_exige_comentario_publico(valor):
            self.visibilidade_comentario_status_pendente = "publica"

    @rx.event
    def alterar_prioridade_pendente(self, valor: str) -> None:
        if (
            not self.edicao_funcional_bloqueada
            and valor in self.prioridades_tratativa()
        ):
            self.prioridade_pendente = valor

    @rx.event
    def alterar_categoria_pendente(self, valor: str) -> None:
        if self.edicao_funcional_bloqueada:
            return
        categoria_id = self._id_pendente(valor)
        categorias_ativas = {item["id"] for item in self.categorias_tratativa}
        if categoria_id in categorias_ativas or categoria_id == self.categoria_confirmada_id:
            self.categoria_pendente_id = valor

    @rx.event
    def alterar_comentario_status_pendente(self, valor: str) -> None:
        if not self.edicao_funcional_bloqueada:
            self.comentario_status_pendente = valor

    @rx.event
    def alterar_visibilidade_comentario_status_pendente(self, valor: str) -> None:
        if self.edicao_funcional_bloqueada:
            return
        if self.status_pendente_exige_comentario_publico:
            self.visibilidade_comentario_status_pendente = "publica"
        elif valor in {"publica", "interna"}:
            self.visibilidade_comentario_status_pendente = valor

    @rx.event
    def descartar_mudancas_tratativa(self) -> None:
        self._copiar_confirmado_para_pendente()
        self.mensagem_tratativa = ""
        self.mensagem_sucesso_tratativa = ""

    @staticmethod
    def _id_da_opcao(valor: str) -> int | None:
        try: resultado = int(valor.split(" — ", 1)[0]) if valor else None
        except (TypeError, ValueError): return None
        return resultado if resultado and resultado > 0 else None

    @staticmethod
    def _inicio_do_dia(data: str) -> int:
        return int(datetime.strptime(data, "%Y-%m-%d").replace(tzinfo=ZoneInfo("America/Sao_Paulo")).timestamp() * 1000)

    def _filtros_solicitados(self) -> tuple[int | None, str, int | None, int | None, int | None, list[str]] | None:
        numero = self.filtro_numero.strip()
        if numero and (not numero.isdigit() or int(numero) <= 0):
            self.mensagem_fila = "Informe um número de chamado válido."; return None
        if self.filtro_status and self.filtro_status not in self.status_filtros():
            self.mensagem_fila = "Informe um status válido."; return None
        ativo_id = self._id_da_opcao(self.filtro_ativo)
        if self.filtro_ativo and ativo_id is None:
            self.mensagem_fila = "Selecione um Totem válido."; return None
        try:
            inicio = self._inicio_do_dia(self.filtro_data_inicio) if self.filtro_data_inicio else None
            fim = self._inicio_do_dia(self.filtro_data_fim) + 86_400_000 if self.filtro_data_fim else None
        except ValueError:
            self.mensagem_fila = "Informe um período de abertura válido."; return None
        if inicio is not None and fim is not None and inicio >= fim:
            self.mensagem_fila = "A data inicial deve ser anterior à data final."; return None
        etiquetas = ([f"Número: {numero}"] if numero else []) + ([f"Status: {self.filtro_status}"] if self.filtro_status else []) + ([f"Totem: {self.filtro_ativo.split(' — ', 1)[-1]}"] if self.filtro_ativo else []) + ([f"Abertura a partir de: {self.filtro_data_inicio}"] if self.filtro_data_inicio else []) + ([f"Abertura até: {self.filtro_data_fim}"] if self.filtro_data_fim else [])
        return (int(numero) if numero else None, self.filtro_status, ativo_id, inicio, fim, etiquetas)

    def _restaurar_filtros_confirmados(self) -> None:
        self.filtro_numero = self.filtro_numero_confirmado
        self.filtro_status = self.filtro_status_confirmado
        self.filtro_ativo = self.filtro_ativo_confirmado
        self.filtro_data_inicio = self.filtro_data_inicio_confirmada
        self.filtro_data_fim = self.filtro_data_fim_confirmada

    @rx.event
    async def aplicar_filtros(self):
        filtros = self._filtros_solicitados()
        if filtros is None: return
        async for evento in self._carregar_fila(
            filtros=filtros,
            confirmar_filtros=True,
            escopo_rapido=self.escopo_rapido,
        ):
            yield evento

    @rx.event
    async def limpar_filtros(self):
        filtros = (None, "", None, None, None, [])
        async for evento in self._carregar_fila(
            filtros=filtros,
            confirmar_filtros=True,
            escopo_rapido=self.escopo_rapido,
        ):
            yield evento

    @rx.event
    async def selecionar_escopo_rapido(self, escopo: str):
        if self.role != "tecnico" or escopo not in {"todos", "atribuidos_a_mim"}:
            return
        async for evento in self._carregar_fila(
            filtros=(self.numero_aplicado, self.status_aplicado, self.ativo_id_aplicado, self.data_inicio_aplicada, self.data_fim_aplicada, self.filtros_aplicados),
            confirmar_filtros=False,
            escopo_rapido=escopo,
        ):
            yield evento

    @rx.event
    async def carregar_fila(self):
        async for evento in self._carregar_fila(
            filtros=(self.numero_aplicado, self.status_aplicado, self.ativo_id_aplicado, self.data_inicio_aplicada, self.data_fim_aplicada, self.filtros_aplicados),
            confirmar_filtros=False,
            escopo_rapido=self.escopo_rapido,
        ):
            yield evento

    async def _carregar_fila(
        self,
        *,
        filtros: tuple[int | None, str, int | None, int | None, int | None, list[str]],
        confirmar_filtros: bool,
        escopo_rapido: str,
    ):
        if self.carregando_fila:
            return
        self.carregando_fila = True
        self.mensagem_fila = ""
        self.mensagem_assuncao = ""
        self.mensagem_responsavel = ""
        self.mensagem_sucesso_responsavel = ""
        yield
        try:
            destino = await self._validar_acesso_fila()
            if destino is not None:
                yield rx.redirect(destino)
                return
            if not self.sessao_confirmada:
                return
            try:
                numero, status, ativo_id, inicio, fim, etiquetas = filtros
                cliente = criar_cliente_service_desk()
                resultado = await cliente.listar_chamados_tecnico(self._auth_token, numero=numero, status=status or None, ativo_id=ativo_id, data_inicio=inicio, data_fim=fim, somente_atribuidos_a_mim=(escopo_rapido == "atribuidos_a_mim"))
                ativos_carregados: list[str] | None = None
                if not self.ativos:
                    ativos = await cliente.listar_ativos_tecnico(self._auth_token)
                    ativos_carregados = [f"{item.id} — {item.nome_ativo}" for item in ativos]
                # A consulta só substitui o resultado confirmado depois que os
                # dados auxiliares necessários à mesma tela também chegaram.
                self.chamados = [_tecnico_para_dict(item) for item in resultado.items]
                self.total_chamados = resultado.total
                self.escopo_rapido = escopo_rapido
                if ativos_carregados is not None:
                    self.ativos = ativos_carregados
                if confirmar_filtros:
                    self.numero_aplicado, self.status_aplicado, self.ativo_id_aplicado, self.data_inicio_aplicada, self.data_fim_aplicada, self.filtros_aplicados = filtros
                    self.filtro_numero = str(numero) if numero is not None else ""
                    self.filtro_status = status
                    self.filtro_ativo = next((item for item in self.ativos if item.startswith(f"{ativo_id} —")), "") if ativo_id else ""
                    self.filtro_data_inicio = self.filtro_data_inicio if inicio is not None else ""
                    self.filtro_data_fim = self.filtro_data_fim if fim is not None else ""
                    self.filtro_numero_confirmado = self.filtro_numero
                    self.filtro_status_confirmado = self.filtro_status
                    self.filtro_ativo_confirmado = self.filtro_ativo
                    self.filtro_data_inicio_confirmada = self.filtro_data_inicio
                    self.filtro_data_fim_confirmada = self.filtro_data_fim
            except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
                destino = self._registrar_erro_fila(erro)
                if confirmar_filtros:
                    self._restaurar_filtros_confirmados()
                if destino is not None:
                    yield rx.redirect(destino)
                    return
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            self._registrar_erro_fila(erro)
            if confirmar_filtros:
                self._restaurar_filtros_confirmados()
        finally:
            self.carregando_fila = False

    @rx.event
    async def carregar_detalhe_tecnico(self):
        if self.carregando_detalhe_tecnico:
            return
        self.carregando_detalhe_tecnico = True
        self.detalhe_tecnico_carregado = False
        self.chamado = {}
        self.timeline = []
        self.tecnicos = []
        self.categorias_tratativa = []
        self.responsavel_confirmado_id = None
        self.status_confirmado = ""
        self.prioridade_confirmada = ""
        self.categoria_confirmada_id = None
        self.ultima_atualizacao_confirmada = None
        self._copiar_confirmado_para_pendente()
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
            cliente = criar_cliente_service_desk()
            resultado = await cliente.obter_chamado_tecnico(
                self._auth_token,
                chamado_id,
            )
            categorias = await cliente.listar_categorias_tratativa(
                self._auth_token
            )
            self._atualizar_detalhe(
                resultado,
                categorias=[
                    {"id": categoria.id, "nome": categoria.nome}
                    for categoria in categorias
                ],
            )
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro_tecnico(erro, "mensagem_detalhe_tecnico")
            if destino is not None:
                self.carregando_detalhe_tecnico = False
                yield rx.redirect(destino)
                return
        self.carregando_detalhe_tecnico = False

    @rx.event
    async def salvar_tratativa(self):
        if self.salvando_tratativa:
            return
        self.mensagem_tratativa = ""
        self.mensagem_sucesso_tratativa = ""
        if self.edicao_funcional_bloqueada:
            self.mensagem_tratativa = "Chamado terminal não permite edição funcional."
            return
        if not self.ha_mudanca_funcional_pendente:
            self.mensagem_tratativa = "Nenhuma alteração pendente para salvar."
            return
        if self.status_pendente_alterado and not self.comentario_status_pendente.strip():
            self.mensagem_tratativa = "Mudança de Status exige comentário."
            return
        if (
            self.status_pendente_exige_comentario_publico
            and self.visibilidade_comentario_status_pendente != "publica"
        ):
            self.mensagem_tratativa = "Este Status exige comentário Público."
            return
        chamado_id = self.chamado.get("id")
        tecnico_id = self._id_pendente(
            self.responsavel_pendente_id,
            permitir_nao_atribuido=True,
        )
        categoria_id = self._id_pendente(self.categoria_pendente_id)
        if (
            not isinstance(chamado_id, int)
            or chamado_id <= 0
            or categoria_id is None
            or self.ultima_atualizacao_confirmada is None
        ):
            self.mensagem_tratativa = "Detalhe do chamado incompatível. Recarregue a página."
            return
        self.salvando_tratativa = True
        yield
        try:
            destino = await self._validar_acesso_fila()
            if destino is not None:
                yield rx.redirect(destino)
                return
            if not self.sessao_confirmada:
                return
            cliente = criar_cliente_service_desk()
            try:
                resultado = await cliente.salvar_tratativa_chamado(
                    self._auth_token,
                    chamado_id,
                    tecnico_id=tecnico_id,
                    status=self.status_pendente,
                    prioridade=self.prioridade_pendente,
                    categorias_servico_id=categoria_id,
                    ultima_atualizacao_em=self.ultima_atualizacao_confirmada,
                    comentario_status=(
                        self.comentario_status_pendente
                        if self.status_pendente_alterado
                        else None
                    ),
                    visibilidade_comentario_status=(
                        self.visibilidade_comentario_status_pendente
                        if self.status_pendente_alterado
                        else None
                    ),
                )
            except XanoConflito:
                self.mensagem_tratativa = (
                    "O chamado foi atualizado por outra operação. O detalhe foi recarregado."
                )
                try:
                    atual = await cliente.obter_chamado_tecnico(
                        self._auth_token,
                        chamado_id,
                    )
                    self._atualizar_detalhe(atual)
                except Exception as erro:  # noqa: BLE001 - erro sanitizado existente
                    destino = self._registrar_erro_tecnico(
                        erro,
                        "mensagem_tratativa",
                    )
                    if destino is not None:
                        yield rx.redirect(destino)
                return
            self._atualizar_detalhe(resultado)
            self.mensagem_sucesso_tratativa = "Alterações salvas."
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro_tecnico(erro, "mensagem_tratativa")
            if destino is not None:
                yield rx.redirect(destino)
                return
        finally:
            self.salvando_tratativa = False

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
