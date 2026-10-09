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
    _detalhe_para_dict,
    _resumo_para_dict,
    comentario_publico_para_dict,
)
from app.services.service_desk import PRIORIDADES_CHAMADO, criar_cliente_service_desk
from app.services.xano import (
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

    filtro_numero: str = ""
    filtro_status: str = ""
    filtro_ativo: str = ""
    filtro_data_inicio: str = ""
    filtro_data_fim: str = ""
    numero_aplicado: int | None = None
    status_aplicado: str = ""
    ativo_id_aplicado: int | None = None
    data_inicio_aplicada: int | None = None
    data_fim_aplicada: int | None = None
    filtros_aplicados: list[str] = []
    ordenar_por: str = "criado_em"
    direcao: str = "DESC"
    total_chamados: int = 0

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
        if self.sessao_confirmada and self.role == "gerente" and self._auth_token:
            return None
        return await self._validar_gerente()

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

        if self.filtro_status and self.filtro_status not in self.status_filtros():
            self.mensagem_chamados = "Informe um status válido."
            return False

        ativo_id = self._id_da_opcao(self.filtro_ativo)
        if self.filtro_ativo and ativo_id is None:
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

        self.numero_aplicado = numero
        self.status_aplicado = self.filtro_status
        self.ativo_id_aplicado = ativo_id
        self.data_inicio_aplicada = inicio
        self.data_fim_aplicada = fim

        filtros: list[str] = []
        if numero is not None:
            filtros.append(f"Número: {numero}")
        if self.filtro_status:
            filtros.append(f"Status: {self.filtro_status}")
        if self.filtro_ativo:
            filtros.append(f"Totem: {self.filtro_ativo.split(' — ', 1)[-1]}")
        if self.filtro_data_inicio:
            filtros.append(f"Abertura a partir de: {self.filtro_data_inicio}")
        if self.filtro_data_fim:
            filtros.append(f"Abertura até: {self.filtro_data_fim}")
        self.filtros_aplicados = filtros
        return True

    def _limpar_filtros(self) -> None:
        self.filtro_numero = ""
        self.filtro_status = ""
        self.filtro_ativo = ""
        self.filtro_data_inicio = ""
        self.filtro_data_fim = ""
        self.numero_aplicado = None
        self.status_aplicado = ""
        self.ativo_id_aplicado = None
        self.data_inicio_aplicada = None
        self.data_fim_aplicada = None
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
        self.filtro_status = valor

    @rx.event
    def alterar_filtro_ativo(self, valor: str):
        self.filtro_ativo = valor

    @rx.event
    def alterar_filtro_data_inicio(self, valor: str):
        self.filtro_data_inicio = valor

    @rx.event
    def alterar_filtro_data_fim(self, valor: str):
        self.filtro_data_fim = valor

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
        if self.carregando_chamados:
            # Eventos rápidos de ordenação/filtro não abrem uma segunda
            # consulta concorrente. A última intenção será atendida pela
            # carga que já está em andamento, sem criar um request storm.
            self.consulta_chamados_pendente = True
            return
        self.carregando_chamados = True
        self._limpar_mensagens_funcionais()
        yield
        try:
            while True:
                self.consulta_chamados_pendente = False
                destino = await self._garantir_gerente()
                if destino is not None:
                    yield rx.redirect(destino)
                    return
                if not self.sessao_confirmada:
                    return

                cliente = criar_cliente_service_desk()
                chamada = cliente.listar_chamados(
                    self._auth_token,
                    numero=self.numero_aplicado,
                    status=self.status_aplicado or None,
                    ativo_id=self.ativo_id_aplicado,
                    data_inicio=self.data_inicio_aplicada,
                    data_fim=self.data_fim_aplicada,
                    ordenar_por=self.ordenar_por,
                    direcao=self.direcao,
                )
                if self.ativos:
                    resultado = await chamada
                    ativos = None
                else:
                    resultado, ativos = await asyncio.gather(
                        chamada,
                        cliente.listar_ativos(self._auth_token),
                        return_exceptions=True,
                    )
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

                self.chamados = [
                    _resumo_para_dict(item) for item in resultado.items
                ]
                self.total_chamados = resultado.total
                if ativos is not None:
                    self.ativos = [
                        f"{item.id} — {item.nome_ativo}" for item in ativos
                    ]

                # Só repete automaticamente quando a consulta anterior
                # terminou com sucesso e houve uma nova intenção concorrente.
                # Em falha transitória, a próxima ação explícita faz a nova
                # tentativa, evitando retry agressivo e novo 429.
                if not self.consulta_chamados_pendente:
                    break
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro(erro, "mensagem_chamados")
            if destino is not None:
                yield rx.redirect(destino)
                return
        finally:
            self.carregando_chamados = False

    @rx.event
    async def aplicar_filtros(self):
        if not self._preparar_filtros_aplicados():
            return
        async for evento in self.carregar_lista():
            yield evento

    @rx.event
    async def limpar_filtros_lista(self):
        self._limpar_filtros()
        async for evento in self.carregar_lista():
            yield evento

    @rx.event
    async def alternar_ordenacao(self, coluna: str):
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
        try:
            cliente = criar_cliente_service_desk()
            ativos, categorias = await asyncio.gather(
                cliente.listar_ativos(self._auth_token),
                cliente.listar_categorias(self._auth_token),
            )
            self.ativos = [f"{item.id} — {item.nome_ativo}" for item in ativos]
            self.ativos_formulario = [
                {"id": item.id, "nome": item.nome_ativo} for item in ativos
            ]
            self.categorias = [f"{item.id} — {item.nome}" for item in categorias]
            self.categorias_formulario = [
                {"id": item.id, "nome": item.nome} for item in categorias
            ]
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro(erro, "mensagem_formulario")
            if destino is not None:
                self.carregando_formulario = False
                yield rx.redirect(destino)
                return
        self.carregando_formulario = False

    @rx.event
    async def carregar_detalhe(self):
        if self.carregando_detalhe:
            return
        self.carregando_detalhe = True
        self.detalhe_carregado = False
        self.chamado = {}
        self.comentarios = []
        self.rascunho_comentario = ""
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
            self.chamado = _detalhe_para_dict(resultado)
            self.detalhe_carregado = True
            self.carregando_comentarios = True
            try:
                comentarios = await cliente.listar_comentarios_publicos(
                    self._auth_token,
                    chamado_id,
                )
                self.comentarios = [
                    comentario_publico_para_dict(comentario)
                    for comentario in comentarios
                ]
            except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
                destino = self._registrar_erro(erro, "mensagem_comentarios")
                if destino is not None:
                    self.carregando_detalhe = False
                    yield rx.redirect(destino)
                    return
            finally:
                self.carregando_comentarios = False
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro(erro, "mensagem_detalhe")
            if destino is not None:
                self.carregando_detalhe = False
                yield rx.redirect(destino)
            return
        self.carregando_detalhe = False

    @rx.event
    async def publicar_comentario(self):
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
            self.comentarios = [comentario_publico_para_dict(comentario)] + self.comentarios
            self.rascunho_comentario = ""
            resultado = await cliente.obter_chamado(self._auth_token, chamado_id)
            self.chamado = _detalhe_para_dict(resultado)
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
            destino = self._registrar_erro(erro, "mensagem_comentarios")
            if destino is not None:
                self.enviando_comentario = False
                yield rx.redirect(destino)
                return
        self.enviando_comentario = False

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
        if self.enviando:
            return
        self.enviando = True
        self.mensagem_formulario = ""
        self.mensagem_sucesso = ""
        yield
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
            self.chamado = _detalhe_para_dict(resultado)
            self._limpar_formulario_local()
            self.enviando = False
            yield rx.toast.success("Chamado aberto com sucesso.")
            yield rx.redirect(f"/gerente/chamados/{resultado.id}")
            return
        except Exception as erro:  # noqa: BLE001 - convertido em erro sanitizado
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
        return rx.redirect("/gerente")

    @rx.event
    def voltar_para_lista(self):
        """Navega sem alterar nem descartar explicitamente o rascunho."""
        return rx.redirect("/gerente")
