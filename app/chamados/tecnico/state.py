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
    DESTINO_PRIMEIRO_ACESSO,
    MENSAGEM_EXPIRADA,
    MENSAGEM_INDISPONIVEL,
    MENSAGEM_NAO_AUTORIZADO,
    AuthState,
)


class ChamadosTecnicoState(AuthState):
    """Mantém a fila global e a tratativa técnica do chamado."""

    filtro_numero: str = ""
    filtro_status: str = ""
    filtro_ativo: str = ""
    filtro_prioridade: str = ""
    filtro_responsavel: str = ""
    filtro_data_inicio: str = ""
    filtro_data_fim: str = ""
    filtro_numero_confirmado: str = ""
    filtro_status_confirmado: str = ""
    filtro_ativo_confirmado: str = ""
    filtro_prioridade_confirmada: str = ""
    filtro_responsavel_confirmado: str = ""
    filtro_data_inicio_confirmada: str = ""
    filtro_data_fim_confirmada: str = ""
    numero_aplicado: int | None = None
    status_aplicado: str = ""
    ativo_id_aplicado: int | None = None
    prioridade_aplicada: str = ""
    responsavel_id_aplicado: int | None = None
    somente_nao_atribuido_aplicado: bool = False
    responsavel_filtro_transitorio_id: int | None = None
    data_inicio_aplicada: int | None = None
    data_fim_aplicada: int | None = None
    filtros_aplicados: list[str] = []
    escopo_rapido: str = "todos"
    ordenar_por: str = "numero"
    direcao_ordenacao: str = "DESC"
    escopo_preferencia_carregada: str = ""
    usuario_id_contexto_fila: int | None = None
    _token_contexto_fila: str = ""
    versao_sessao_contexto_fila: int = -1
    ativos: list[str] = []
    total_chamados: int = 0
    chamados: list[TecnicoView] = []
    chamado: DetalheView = {}
    timeline: list[TimelineView] = []
    tecnicos: list[TecnicoOpcaoView] = []
    categorias_tratativa: list[TecnicoOpcaoView] = []
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
    mensagem_fila: str = ""
    mensagem_detalhe_tecnico: str = ""
    mensagem_tratativa: str = ""
    mensagem_sucesso_tratativa: str = ""

    @staticmethod
    def status_filtros() -> list[str]:
        return ["Novo", "Em Atendimento", "Aguardando Solicitante", "Aguardando Mudança", "Resolvido", "Solução Rejeitada", "Encerrado", "Cancelado"]

    @staticmethod
    def prioridades_tratativa() -> list[str]:
        return ["Baixa", "Média", "Alta", "Urgente"]

    @rx.var
    def responsaveis_filtro(self) -> list[str]:
        opcoes = ["0 — Não atribuído"] + [
            f"{tecnico['id']} — {tecnico['nome']}" for tecnico in self.tecnicos
        ]
        if (
            self.responsavel_filtro_transitorio_id is not None
            and all(
                tecnico["id"] != self.responsavel_filtro_transitorio_id
                for tecnico in self.tecnicos
            )
        ):
            opcoes.append(
                f"{self.responsavel_filtro_transitorio_id} — Técnico não listado"
            )
        return opcoes

    def _opcao_responsavel(self, responsavel_id: int | None, somente_nao_atribuido: bool) -> str:
        if somente_nao_atribuido:
            return "0 — Não atribuído"
        if responsavel_id is None:
            return ""
        opcao = next(
            (
                f"{item['id']} — {item['nome']}"
                for item in self.tecnicos
                if item["id"] == responsavel_id
            ),
            "",
        )
        if opcao:
            if self.responsavel_filtro_transitorio_id == responsavel_id:
                self.responsavel_filtro_transitorio_id = None
            return opcao
        if responsavel_id == self.responsavel_filtro_transitorio_id:
            return f"{responsavel_id} — Técnico não listado"
        return ""

    def _incorporar_responsaveis_da_fila(self, itens) -> None:
        """Reaproveita responsáveis retornados pela própria lista da fila."""
        catalogo = {item["id"]: item["nome"] for item in self.tecnicos}
        for chamado in itens:
            tecnico = chamado.tecnico
            if tecnico is not None:
                catalogo[tecnico.id] = tecnico.nome
        self.tecnicos = [
            {"id": tecnico_id, "nome": nome}
            for tecnico_id, nome in sorted(
                catalogo.items(), key=lambda item: (item[1].casefold(), item[0])
            )
        ]

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
    def ha_rascunho_pendente(self) -> bool:
        return self.ha_mudanca_funcional_pendente or bool(
            self.comentario_status_pendente.strip()
        )

    @rx.var
    def pode_salvar_tratativa(self) -> bool:
        if not self.ha_mudanca_funcional_pendente:
            return bool(self.comentario_status_pendente.strip())
        if self.edicao_funcional_bloqueada:
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

    def _atualizar_detalhe(
        self,
        detalhe: DetalheChamadoTecnico,
        categorias: list[TecnicoOpcaoView] | None = None,
    ) -> None:
        self._atualizar_chamado(detalhe.chamado)
        self.tecnicos = [
            {"id": tecnico.id, "nome": tecnico.nome}
            for tecnico in detalhe.tecnicos
        ]
        if categorias is not None:
            self.categorias_tratativa = categorias
        nomes_tecnicos = {item["id"]: item["nome"] for item in self.tecnicos}
        nomes_categorias = {
            item["id"]: item["nome"] for item in self.categorias_tratativa
        }
        nomes_categorias[detalhe.chamado.categoria.id] = detalhe.chamado.categoria.nome
        eventos = [
            evento_timeline_para_dict(
                evento,
                tecnicos=nomes_tecnicos,
                categorias=nomes_categorias,
            )
            for evento in detalhe.timeline
        ]
        comentarios = {item["id"]: item for item in eventos if item["tipo"] == "comentario"}
        comentarios_agrupados = {
            item["comentario_interacao_id"]
            for item in eventos
            if item["tipo"] == "alteracao_chamado"
            and item["comentario_interacao_id"] in comentarios
        }
        for item in eventos:
            comentario_id = item["comentario_interacao_id"]
            if item["tipo"] == "alteracao_chamado" and comentario_id in comentarios:
                comentario = comentarios[comentario_id]
                item["comentario_conteudo"] = comentario["conteudo"]
                item["comentario_visibilidade_texto"] = comentario["visibilidade_texto"]
        self.timeline = [
            item
            for item in eventos
            if not (item["tipo"] == "comentario" and item["id"] in comentarios_agrupados)
        ]
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
        self.detalhe_tecnico_carregado = True

    async def _validar_acesso_fila(self) -> str | None:
        if self.deve_trocar_senha:
            return DESTINO_PRIMEIRO_ACESSO
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

    @rx.event
    async def redirecionar_alias_fila(self):
        revalidar = not (
            self.sessao_confirmada
            and self._auth_token
            and self.role in {"tecnico", "diretoria", "administrador"}
        )
        if revalidar:
            self._iniciar_carregamento()
            yield
        destino = await self._validar_acesso_fila()
        if revalidar:
            self._finalizar_carregamento()
        yield rx.redirect(destino or "/chamados")

    @rx.event
    async def redirecionar_alias_detalhe(self):
        revalidar = not (
            self.sessao_confirmada
            and self._auth_token
            and self.role in {"tecnico", "diretoria", "administrador"}
        )
        if revalidar:
            self._iniciar_carregamento()
            yield
        destino = await self._validar_acesso_fila()
        if revalidar:
            self._finalizar_carregamento()
        if destino is not None:
            yield rx.redirect(destino)
            return
        chamado_id = self.router.page.params.get("chamado_id", "")
        yield rx.redirect(f"/chamados/{chamado_id}")

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
        """Mantém o tratamento específico de detalhe e tratativa."""
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
    def alterar_filtro_prioridade(self, valor: str) -> None: self.filtro_prioridade = valor
    @rx.event
    def alterar_filtro_responsavel(self, valor: str) -> None:
        responsavel_id = self._id_da_opcao(valor)
        if valor == "0 — Não atribuído" or responsavel_id in {item["id"] for item in self.tecnicos} or responsavel_id == self.responsavel_filtro_transitorio_id:
            self.filtro_responsavel = valor
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
        self.comentario_status_pendente = valor

    @rx.event
    def alterar_visibilidade_comentario_status_pendente(self, valor: str) -> None:
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

    def _responsavel_solicitado(self) -> tuple[int | None, bool] | None:
        if not self.filtro_responsavel:
            return None, False
        if self.filtro_responsavel == "0 — Não atribuído":
            return None, True
        responsavel_id = self._id_da_opcao(self.filtro_responsavel)
        if responsavel_id not in {item["id"] for item in self.tecnicos} and responsavel_id != self.responsavel_filtro_transitorio_id:
            self.mensagem_fila = "Selecione um Responsável válido."
            return None
        return responsavel_id, False

    @staticmethod
    def _inicio_do_dia(data: str) -> int:
        return int(datetime.strptime(data, "%Y-%m-%d").replace(tzinfo=ZoneInfo("America/Sao_Paulo")).timestamp() * 1000)

    @staticmethod
    def _data_do_timestamp(instante: int | None) -> str:
        if instante is None:
            return ""
        return datetime.fromtimestamp(
            instante / 1000, tz=ZoneInfo("America/Sao_Paulo")
        ).strftime("%Y-%m-%d")

    def _filtros_solicitados(self) -> tuple[int | None, str, int | None, int | None, int | None, str, int | None, bool, list[str]] | None:
        numero = self.filtro_numero.strip()
        if numero and (not numero.isdigit() or int(numero) <= 0):
            self.mensagem_fila = "Informe um número de chamado válido."; return None
        if self.filtro_status and self.filtro_status not in self.status_filtros():
            self.mensagem_fila = "Informe um status válido."; return None
        if self.filtro_prioridade and self.filtro_prioridade not in self.prioridades_tratativa():
            self.mensagem_fila = "Informe uma prioridade válida."; return None
        responsavel = self._responsavel_solicitado()
        if responsavel is None:
            return None
        responsavel_id, somente_nao_atribuido = responsavel
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
        etiquetas = ([f"Número: {numero}"] if numero else []) + ([f"Status: {self.filtro_status}"] if self.filtro_status else []) + ([f"Prioridade: {self.filtro_prioridade}"] if self.filtro_prioridade else []) + ([f"Responsável: {self.filtro_responsavel.split(' — ', 1)[-1]}"] if self.filtro_responsavel else []) + ([f"Totem: {self.filtro_ativo.split(' — ', 1)[-1]}"] if self.filtro_ativo else []) + ([f"Abertura a partir de: {self.filtro_data_inicio}"] if self.filtro_data_inicio else []) + ([f"Abertura até: {self.filtro_data_fim}"] if self.filtro_data_fim else [])
        return (int(numero) if numero else None, self.filtro_status, ativo_id, inicio, fim, self.filtro_prioridade, responsavel_id, somente_nao_atribuido, etiquetas)

    def _restaurar_filtros_confirmados(self) -> None:
        self.filtro_numero = self.filtro_numero_confirmado
        self.filtro_status = self.filtro_status_confirmado
        self.filtro_ativo = self.filtro_ativo_confirmado
        self.filtro_prioridade = self.filtro_prioridade_confirmada
        self.filtro_responsavel = self.filtro_responsavel_confirmado
        self.filtro_data_inicio = self.filtro_data_inicio_confirmada
        self.filtro_data_fim = self.filtro_data_fim_confirmada

    def _limpar_contexto_fila(self) -> None:
        """Descarta dados protegidos e filtros associados a outra identidade."""
        self.filtro_numero = ""
        self.filtro_status = ""
        self.filtro_ativo = ""
        self.filtro_prioridade = ""
        self.filtro_responsavel = ""
        self.filtro_data_inicio = ""
        self.filtro_data_fim = ""
        self.filtro_numero_confirmado = ""
        self.filtro_status_confirmado = ""
        self.filtro_ativo_confirmado = ""
        self.filtro_prioridade_confirmada = ""
        self.filtro_responsavel_confirmado = ""
        self.filtro_data_inicio_confirmada = ""
        self.filtro_data_fim_confirmada = ""
        self.numero_aplicado = None
        self.status_aplicado = ""
        self.ativo_id_aplicado = None
        self.prioridade_aplicada = ""
        self.responsavel_id_aplicado = None
        self.somente_nao_atribuido_aplicado = False
        self.responsavel_filtro_transitorio_id = None
        self.data_inicio_aplicada = None
        self.data_fim_aplicada = None
        self.filtros_aplicados = []
        self.escopo_rapido = "todos"
        self.ordenar_por = "numero"
        self.direcao_ordenacao = "DESC"
        self.escopo_preferencia_carregada = ""
        self.ativos = []
        self.total_chamados = 0
        self.chamados = []
        self.chamado = {}
        self.timeline = []
        self.tecnicos = []
        self.categorias_tratativa = []
        self.detalhe_tecnico_carregado = False
        self.responsavel_confirmado_id = None
        self.status_confirmado = ""
        self.prioridade_confirmada = ""
        self.categoria_confirmada_id = None
        self.ultima_atualizacao_confirmada = None
        self._copiar_confirmado_para_pendente()

    def _sincronizar_contexto_fila(self) -> bool:
        """Isola a fila entre identidades e reinicia o escopo a cada sessão."""
        if self.usuario_id is None:
            self._limpar_contexto_fila()
            self.usuario_id_contexto_fila = None
            self._token_contexto_fila = ""
            self.versao_sessao_contexto_fila = -1
            return True
        if self.usuario_id_contexto_fila is None:
            self.usuario_id_contexto_fila = self.usuario_id
            self._token_contexto_fila = self._auth_token
            self.versao_sessao_contexto_fila = self._versao_sessao
            return False
        identidade_alterada = self.usuario_id_contexto_fila != self.usuario_id
        if identidade_alterada:
            self._limpar_contexto_fila()
        elif (
            self._token_contexto_fila != self._auth_token
            or self.versao_sessao_contexto_fila != self._versao_sessao
        ):
            # Preferências duráveis serão relidas para a nova sessão; o escopo
            # rápido nunca atravessa login/logout.
            self.escopo_rapido = "todos"
            self.escopo_preferencia_carregada = ""
        self.usuario_id_contexto_fila = self.usuario_id
        self._token_contexto_fila = self._auth_token
        self.versao_sessao_contexto_fila = self._versao_sessao
        return identidade_alterada

    @rx.event
    async def aplicar_filtros(self):
        filtros = self._filtros_solicitados()
        if filtros is None: return
        async for evento in self._carregar_fila(
            filtros=filtros,
            persistir=True,
            escopo_rapido=self.escopo_rapido,
        ):
            yield evento

    @rx.event
    async def limpar_filtros(self):
        filtros = (None, "", None, None, None, "", None, False, [])
        async for evento in self._carregar_fila(
            filtros=filtros,
            persistir=True,
            escopo_rapido=self.escopo_rapido,
        ):
            yield evento

    @rx.event
    async def selecionar_escopo_rapido(self, escopo: str):
        if self.role != "tecnico" or escopo not in {"todos", "atribuidos_a_mim"}:
            return
        async for evento in self._carregar_fila(
            filtros=(None, "", None, None, None, "", None, False, []),
            persistir=False,
            escopo_rapido=escopo,
            alteracao_explicita=True,
            carregar_preferencia=True,
        ):
            yield evento

    @rx.event
    async def carregar_fila(self):
        async for evento in self._carregar_fila(
            filtros=(self.numero_aplicado, self.status_aplicado, self.ativo_id_aplicado, self.data_inicio_aplicada, self.data_fim_aplicada, self.prioridade_aplicada, self.responsavel_id_aplicado, self.somente_nao_atribuido_aplicado, self.filtros_aplicados),
            persistir=False,
            escopo_rapido=self.escopo_rapido,
            carregar_preferencia=self.escopo_preferencia_carregada != self.escopo_rapido,
        ):
            yield evento

    @rx.event
    async def ordenar_fila(self, coluna: str):
        if coluna not in {"numero", "titulo", "status", "prioridade", "totem", "categoria", "responsavel", "criado_em", "ultima_atualizacao_em"}:
            return
        direcao_candidata = "ASC" if coluna != self.ordenar_por else ("DESC" if self.direcao_ordenacao == "ASC" else "ASC")
        async for evento in self._carregar_fila(
            filtros=(self.numero_aplicado, self.status_aplicado, self.ativo_id_aplicado, self.data_inicio_aplicada, self.data_fim_aplicada, self.prioridade_aplicada, self.responsavel_id_aplicado, self.somente_nao_atribuido_aplicado, self.filtros_aplicados),
            persistir=True, escopo_rapido=self.escopo_rapido,
            ordenacao_candidata=(coluna, direcao_candidata),
        ):
            yield evento

    async def _carregar_fila(
        self,
        *,
        filtros: tuple[int | None, str, int | None, int | None, int | None, str, int | None, bool, list[str]],
        persistir: bool,
        escopo_rapido: str,
        alteracao_explicita: bool = False,
        carregar_preferencia: bool = False,
        ordenacao_candidata: tuple[str, str] | None = None,
    ):
        if self.carregando_fila:
            return
        self.carregando_fila = True
        self.mensagem_fila = ""
        yield
        try:
            destino = await self._validar_acesso_fila()
            if destino is not None:
                yield rx.redirect(destino)
                return
            if not self.sessao_confirmada:
                return
            identidade_alterada = self._sincronizar_contexto_fila()
            if identidade_alterada:
                filtros = (None, "", None, None, None, "", None, False, [])
            escopo_solicitado = (
                escopo_rapido if alteracao_explicita else self.escopo_rapido
            )
            escopo_efetivo = (
                escopo_solicitado
                if self.role == "tecnico"
                and escopo_solicitado in {"todos", "atribuidos_a_mim"}
                else "todos"
            )
            # Perfis globais nunca carregam nem exibem um escopo pessoal que
            # tenha permanecido no State de um Técnico que saiu da sessão.
            if self.role != "tecnico":
                self.escopo_rapido = "todos"
            try:
                cliente = criar_cliente_service_desk()
                deve_carregar_preferencia = carregar_preferencia or (not persistir and self.escopo_preferencia_carregada != escopo_efetivo)
                if deve_carregar_preferencia:
                    preferencia = await cliente.obter_preferencia_fila_tecnica(self._auth_token, escopo=escopo_efetivo)
                    self.responsavel_filtro_transitorio_id = (
                        preferencia.responsavel_id
                        if preferencia.responsavel_id is not None
                        else None
                    )
                    responsavel_preferencia = self._opcao_responsavel(
                        preferencia.responsavel_id,
                        preferencia.somente_nao_atribuido,
                    )
                    etiquetas_preferencia = ([f"Número: {preferencia.numero}"] if preferencia.numero is not None else []) + ([f"Status: {preferencia.status}"] if preferencia.status else []) + ([f"Prioridade: {preferencia.prioridade}"] if preferencia.prioridade else []) + ([f"Responsável: {responsavel_preferencia.split(' — ', 1)[-1]}"] if responsavel_preferencia else [])
                    filtros = (preferencia.numero, preferencia.status or "", preferencia.ativo_id, preferencia.data_inicio, preferencia.data_fim, preferencia.prioridade or "", preferencia.responsavel_id, preferencia.somente_nao_atribuido, etiquetas_preferencia)
                    ordenar_por, direcao = preferencia.ordenar_por, preferencia.direcao
                elif ordenacao_candidata is not None:
                    ordenar_por, direcao = ordenacao_candidata
                else:
                    ordenar_por, direcao = self.ordenar_por, self.direcao_ordenacao
                numero, status, ativo_id, inicio, fim, prioridade, responsavel_id, somente_nao_atribuido, etiquetas = filtros
                consulta = {"numero": numero, "status": status or None, "ativo_id": ativo_id, "data_inicio": inicio, "data_fim": fim, "somente_atribuidos_a_mim": escopo_efetivo == "atribuidos_a_mim"}
                if prioridade:
                    consulta["prioridade"] = prioridade
                if responsavel_id is not None:
                    consulta["responsavel_id"] = responsavel_id
                elif somente_nao_atribuido:
                    consulta["responsavel_id"] = 0
                if ordenar_por != "numero":
                    consulta["ordenar_por"] = ordenar_por
                if direcao != "DESC":
                    consulta["direcao"] = direcao
                resultado = await cliente.listar_chamados_tecnico(self._auth_token, **consulta)
                ativos_carregados: list[str] | None = None
                if not self.ativos:
                    ativos = await cliente.listar_ativos_tecnico(self._auth_token)
                    ativos_carregados = [f"{item.id} — {item.nome_ativo}" for item in ativos]
                # Consulta candidata antes do save; o State só confirma após ambos.
                if persistir:
                    await cliente.salvar_preferencia_fila_tecnica(self._auth_token, escopo=escopo_efetivo, numero=numero, status=status or None, ativo_id=ativo_id, data_inicio=inicio, data_fim=fim, prioridade=prioridade or None, responsavel_id=responsavel_id, somente_nao_atribuido=somente_nao_atribuido, ordenar_por=ordenar_por, direcao=direcao)
                self._incorporar_responsaveis_da_fila(resultado.items)
                responsavel_opcao = self._opcao_responsavel(
                    responsavel_id, somente_nao_atribuido
                )
                if responsavel_opcao:
                    etiqueta_responsavel = (
                        f"Responsável: {responsavel_opcao.split(' — ', 1)[-1]}"
                    )
                    if any(
                        etiqueta.startswith("Responsável:") for etiqueta in etiquetas
                    ):
                        etiquetas = [
                            etiqueta_responsavel
                            if etiqueta.startswith("Responsável:")
                            else etiqueta
                            for etiqueta in etiquetas
                        ]
                    else:
                        etiquetas = [*etiquetas, etiqueta_responsavel]
                    filtros = (
                        numero,
                        status,
                        ativo_id,
                        inicio,
                        fim,
                        prioridade,
                        responsavel_id,
                        somente_nao_atribuido,
                        etiquetas,
                    )
                self.chamados = [_tecnico_para_dict(item) for item in resultado.items]
                self.total_chamados = resultado.total
                self.escopo_rapido = escopo_efetivo
                self.ordenar_por, self.direcao_ordenacao = ordenar_por, direcao
                self.escopo_preferencia_carregada = escopo_efetivo
                if ativos_carregados is not None:
                    self.ativos = ativos_carregados
                if persistir or deve_carregar_preferencia:
                    self.numero_aplicado, self.status_aplicado, self.ativo_id_aplicado, self.data_inicio_aplicada, self.data_fim_aplicada, self.prioridade_aplicada, self.responsavel_id_aplicado, self.somente_nao_atribuido_aplicado, self.filtros_aplicados = filtros
                    self.filtro_numero = str(numero) if numero is not None else ""
                    self.filtro_status = status
                    self.filtro_ativo = next((item for item in self.ativos if item.startswith(f"{ativo_id} —")), "") if ativo_id else ""
                    self.filtro_prioridade = prioridade
                    self.filtro_responsavel = responsavel_opcao
                    self.filtro_data_inicio = self._data_do_timestamp(inicio)
                    self.filtro_data_fim = self._data_do_timestamp(fim - 86_400_000) if fim is not None else ""
                    self.filtro_numero_confirmado = self.filtro_numero
                    self.filtro_status_confirmado = self.filtro_status
                    self.filtro_ativo_confirmado = self.filtro_ativo
                    self.filtro_prioridade_confirmada = self.filtro_prioridade
                    self.filtro_responsavel_confirmado = self.filtro_responsavel
                    self.filtro_data_inicio_confirmada = self.filtro_data_inicio
                    self.filtro_data_fim_confirmada = self.filtro_data_fim
            except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
                destino = self._registrar_erro_fila(erro)
                if persistir:
                    self._restaurar_filtros_confirmados()
                if destino is not None:
                    yield rx.redirect(destino)
                    return
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            self._registrar_erro_fila(erro)
            if persistir:
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
        comentario = self.comentario_status_pendente.strip()
        if not self.ha_mudanca_funcional_pendente and not comentario:
            self.mensagem_tratativa = "Nenhuma alteração ou comentário pendente para salvar."
            return
        if self.ha_mudanca_funcional_pendente and self.edicao_funcional_bloqueada:
            self.mensagem_tratativa = "Chamado terminal não permite edição funcional."
            return
        if self.status_pendente_alterado and not comentario:
            self.mensagem_tratativa = "Mudança de Status exige comentário."
            return
        if (
            self.status_pendente_exige_comentario_publico
            and self.visibilidade_comentario_status_pendente != "publica"
        ):
            self.mensagem_tratativa = "Este Status exige comentário Público."
            return
        chamado_id = self.chamado.get("id")
        if not isinstance(chamado_id, int) or chamado_id <= 0:
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
            if not self.ha_mudanca_funcional_pendente:
                resultado = await cliente.criar_comentario_operacional(
                    self._auth_token,
                    chamado_id,
                    conteudo=comentario,
                    visibilidade=self.visibilidade_comentario_status_pendente,
                )
                self._atualizar_detalhe(resultado)
                self.mensagem_sucesso_tratativa = "Comentário adicionado."
                return

            tecnico_id = self._id_pendente(
                self.responsavel_pendente_id,
                permitir_nao_atribuido=True,
            )
            categoria_id = self._id_pendente(self.categoria_pendente_id)
            if categoria_id is None or self.ultima_atualizacao_confirmada is None:
                self.mensagem_tratativa = (
                    "Detalhe do chamado incompatível. Recarregue a página."
                )
                return
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
                        comentario if comentario else None
                    ),
                    visibilidade_comentario_status=(
                        self.visibilidade_comentario_status_pendente if comentario else None
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
