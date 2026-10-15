import asyncio
import inspect

import pytest

import app.chamados.gerente.pages as paginas_gerente
import app.chamados.tecnico.pages as paginas_chamados
import app.chamados.tecnico.state as chamados_module
from app.services.service_desk import (
    ChamadoDetalhe,
    ChamadoResumo,
    ListaChamadosGerente,
    DetalheChamadoTecnico,
    EventoTimelineChamado,
    ReferenciaAtivo,
    ReferenciaCategoria,
    ReferenciaLoja,
    ReferenciaUsuario,
)
from app.services.xano import XanoConflito, XanoContratoInvalido, XanoIndisponivel, XanoNaoAutorizado
from app.states.auth import MENSAGEM_INDISPONIVEL, MENSAGEM_NAO_AUTORIZADO
from app.chamados.shared import _detalhe_para_dict, _tecnico_para_dict
from app.chamados.tecnico import ChamadosTecnicoState


def executar_evento(handler, estado, *args):
    async def coletar():
        return [evento async for evento in handler.fn(estado, *args)]

    return asyncio.run(coletar())


def resumo_tecnico(*, status="Novo", tecnico=None, atribuido_em=0):
    return ChamadoResumo(
        id=32,
        titulo="TESTE E2E - Falha operacional",
        status=status,
        prioridade="Alta",
        origem="manual",
        criado_em=1780000000000,
        ultima_atualizacao_em=1780000000000,
        ativo=ReferenciaAtivo(id=1, nome_ativo="Totem de teste"),
        categoria=ReferenciaCategoria(id=2, nome="Falha de Rede"),
        descricao="Descrição de teste",
        sla_horas_aplicado=2,
        atribuido_em=atribuido_em,
        solicitante=ReferenciaUsuario(id=8, nome="Gerente"),
        tecnico=tecnico,
    )


def detalhe_tecnico(
    *,
    status="Novo",
    tecnico=None,
    atribuido_em=1780000001000,
    criador_sistema=None,
    loja=None,
):
    return ChamadoDetalhe(
        id=32,
        titulo="TESTE E2E - Falha operacional",
        descricao="Descrição de teste",
        status=status,
        prioridade="Alta",
        origem="manual",
        criado_em=1780000000000,
        ultima_atualizacao_em=1780000000000,
        sla_horas_aplicado=2,
        ativo=ReferenciaAtivo(id=1, nome_ativo="Totem de teste"),
        categoria=ReferenciaCategoria(id=2, nome="Falha de Rede"),
        solicitante=ReferenciaUsuario(id=8, nome="Gerente"),
        tecnico=tecnico,
        atribuido_em=atribuido_em,
        criador_sistema=criador_sistema,
        loja=loja,
    )


class ClienteTecnicoFalso:
    def __init__(
        self,
        *,
        resultado_assuncao=None,
        erro_assuncao=None,
        resultado_detalhe=None,
        erro_detalhe=None,
        erro_ativos=None,
        listas=None,
    ):
        self.resultado_assuncao = resultado_assuncao or detalhe_tecnico(
            tecnico=ReferenciaUsuario(id=9, nome="Técnico 9")
        )
        self.erro_assuncao = erro_assuncao
        self.resultado_detalhe = resultado_detalhe
        self.erro_detalhe = erro_detalhe
        self.erro_ativos = erro_ativos
        self.listas = listas or {}
        self.consultas = []
        self.assuncoes = []
        self.detalhes = []
        self.atribuicoes = []

    async def listar_chamados_tecnico(self, token, **filtros):
        self.consultas.append((token, filtros))
        resultado = self.listas.get("resultado", [])
        if isinstance(resultado, Exception):
            raise resultado
        return ListaChamadosGerente(items=resultado, total=len(resultado))

    async def listar_ativos_monitoramento(self, token):
        if self.erro_ativos is not None:
            raise self.erro_ativos
        return []

    async def alterar_responsavel_tecnico(
        self, token, chamado_id, acao, tecnico_id=None
    ):
        self.atribuicoes.append((token, chamado_id, acao, tecnico_id))
        if acao == "assumir":
            self.assuncoes.append((token, chamado_id))
        if self.erro_assuncao is not None:
            raise self.erro_assuncao
        return self.resultado_assuncao

    async def obter_chamado_tecnico(self, token, chamado_id):
        self.detalhes.append((token, chamado_id))
        if self.erro_detalhe is not None:
            raise self.erro_detalhe
        return self.resultado_detalhe or DetalheChamadoTecnico(
            chamado=self.resultado_assuncao,
            timeline=[],
            tecnicos=[ReferenciaUsuario(id=9, nome="Técnico 9")],
        )


def novo_estado_tecnico(role="tecnico"):
    estado = ChamadosTecnicoState(_reflex_internal_init=True)
    object.__setattr__(estado, "_auth_token", "token-de-teste")
    object.__setattr__(estado, "sessao_confirmada", True)
    object.__setattr__(estado, "usuario_id", 9)
    object.__setattr__(estado, "role", role)
    return estado


def liberar_validacao_de_sessao(monkeypatch):
    async def validar(_estado):
        return None

    monkeypatch.setattr(ChamadosTecnicoState, "_validar_tecnico", validar)
    monkeypatch.setattr(ChamadosTecnicoState, "_validar_acesso_fila", validar)


@pytest.mark.parametrize("role", ["tecnico", "diretoria", "administrador"])
def test_aplicar_filtros_consulta_filtros_explicitos(monkeypatch, role):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso()
    monkeypatch.setattr(
        chamados_module,
        "criar_cliente_service_desk",
        lambda: cliente,
    )
    estado = novo_estado_tecnico(role)

    estado.filtro_numero = "102"
    estado.filtro_status = "Novo"
    executar_evento(ChamadosTecnicoState.aplicar_filtros, estado)

    assert estado.numero_aplicado == 102
    assert estado.status_aplicado == "Novo"
    assert cliente.consultas == [("token-de-teste", {"numero": 102, "status": "Novo", "ativo_id": None, "data_inicio": None, "data_fim": None})]
    assert estado.carregando_fila is False


@pytest.mark.parametrize("role", ["tecnico", "diretoria", "administrador"])
def test_fila_global_revalida_e_autoriza_perfis_previstos(monkeypatch, role):
    async def revalidar(_estado):
        return None

    monkeypatch.setattr(ChamadosTecnicoState, "_revalidar", revalidar)
    estado = novo_estado_tecnico(role)

    assert asyncio.run(estado._validar_acesso_fila()) is None


def test_fila_global_redireciona_perfil_fora_do_escopo(monkeypatch):
    async def revalidar(_estado):
        return None

    monkeypatch.setattr(ChamadosTecnicoState, "_revalidar", revalidar)
    estado = novo_estado_tecnico("gerente")

    assert asyncio.run(estado._validar_acesso_fila()) == "/gerente"


def test_pesquisa_por_numero_envia_o_valor_atual_ao_service(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso()
    monkeypatch.setattr(
        chamados_module,
        "criar_cliente_service_desk",
        lambda: cliente,
    )
    estado = novo_estado_tecnico("diretoria")
    estado.filtro_numero = " 102 "

    executar_evento(ChamadosTecnicoState.aplicar_filtros, estado)

    assert cliente.consultas == [("token-de-teste", {"numero": 102, "status": None, "ativo_id": None, "data_inicio": None, "data_fim": None})]


def test_limpar_filtros_recarrega_fila_sem_numero(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso()
    monkeypatch.setattr(
        chamados_module,
        "criar_cliente_service_desk",
        lambda: cliente,
    )
    estado = novo_estado_tecnico("administrador")
    estado.filtro_numero = "102"

    executar_evento(ChamadosTecnicoState.limpar_filtros, estado)

    assert estado.filtro_numero == ""
    assert cliente.consultas == [("token-de-teste", {"numero": None, "status": None, "ativo_id": None, "data_inicio": None, "data_fim": None})]


def test_falha_da_consulta_preserva_filtro_e_resultado_aplicados(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    anterior = _tecnico_para_dict(resumo_tecnico())
    cliente = ClienteTecnicoFalso(
        listas={"resultado": XanoContratoInvalido("contrato incompatível")}
    )
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado.chamados = [anterior]
    estado.filtro_status = "Novo"

    executar_evento(ChamadosTecnicoState.aplicar_filtros, estado)

    assert cliente.consultas[0][1]["status"] == "Novo"
    assert estado.status_aplicado == ""
    assert estado.filtro_status == ""
    assert estado.chamados == [anterior]
    assert "identidade" not in estado.mensagem_fila.casefold()
    assert "resposta do serviço" in estado.mensagem_fila


def test_falha_ao_carregar_totens_nao_substitui_resultado_confirmado(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    anterior = _tecnico_para_dict(resumo_tecnico())
    cliente = ClienteTecnicoFalso(
        listas={"resultado": [resumo_tecnico()]},
        erro_ativos=XanoIndisponivel("falha"),
    )
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado.chamados = [anterior]
    estado.total_chamados = 1
    estado.filtro_status_confirmado = "Novo"
    estado.status_aplicado = "Novo"
    estado.filtros_aplicados = ["Status: Novo"]
    estado.filtro_status = "Encerrado"

    executar_evento(ChamadosTecnicoState.aplicar_filtros, estado)

    assert estado.chamados == [anterior]
    assert estado.total_chamados == 1
    assert estado.filtro_status == "Novo"
    assert estado.filtros_aplicados == ["Status: Novo"]


def test_erro_403_na_fila_preserva_sessao(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(listas={"resultado": XanoNaoAutorizado("negado")})
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()

    executar_evento(ChamadosTecnicoState.carregar_fila, estado)

    assert estado.sessao_confirmada is True
    assert estado.mensagem_fila == MENSAGEM_NAO_AUTORIZADO


def test_numero_invalido_nao_submete_nem_altera_filtro_aplicado(monkeypatch):
    cliente = ClienteTecnicoFalso()
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado.filtro_numero = "abc"

    executar_evento(ChamadosTecnicoState.aplicar_filtros, estado)

    assert cliente.consultas == []
    assert estado.numero_aplicado is None
    assert estado.mensagem_fila == "Informe um número de chamado válido."


def test_limpar_filtros_com_falha_restaura_os_valores_aplicados(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(
        listas={"resultado": XanoContratoInvalido("contrato incompatível")}
    )
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado.filtro_status_confirmado = "Novo"
    estado.filtro_numero_confirmado = "101"
    estado.status_aplicado = "Novo"
    estado.numero_aplicado = 101
    estado.filtros_aplicados = ["Status: Novo", "Número: 101"]

    executar_evento(ChamadosTecnicoState.limpar_filtros, estado)

    assert cliente.consultas[0][1]["numero"] is None
    assert estado.filtro_status == "Novo"
    assert estado.filtro_numero == "101"
    assert estado.filtros_aplicados == ["Status: Novo", "Número: 101"]


def test_contrato_invalido_no_detalhe_nao_vira_erro_de_identidade(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(erro_detalhe=XanoContratoInvalido("contrato"))
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    object.__setattr__(estado, "chamado_id", "32")

    executar_evento(ChamadosTecnicoState.carregar_detalhe_tecnico, estado)

    assert estado.sessao_confirmada is True
    assert "identidade" not in estado.mensagem_detalhe_tecnico.casefold()
    assert "resposta do serviço" in estado.mensagem_detalhe_tecnico


def test_fila_global_reutiliza_tabela_e_filtros_sem_abas_de_visao():
    fonte = inspect.getsource(paginas_chamados._fila_tecnico)

    assert "rx.table.root" in fonte
    assert "Situação de atribuição" not in fonte
    assert "Atribuídos a outros Técnicos" not in fonte
    assert 'item["tecnico_nome"]' in fonte
    assert "selecionar_visao" not in fonte
    assert '"Não atribuídos"' not in fonte


def test_elegibilidade_visual_usa_status_e_tecnico_sem_condicionar_timestamp():
    legado_com_timestamp = resumo_tecnico(atribuido_em=1780000001000)
    tecnico_atribuido = resumo_tecnico(
        tecnico=ReferenciaUsuario(id=13, nome="Outro Técnico"),
        atribuido_em=1780000001000,
    )
    status_diferente = resumo_tecnico(status="Em Atendimento", atribuido_em=0)
    status_nulo = resumo_tecnico(status=None)

    assert _tecnico_para_dict(legado_com_timestamp)["pode_assumir"] is True
    assert _detalhe_para_dict(
        detalhe_tecnico(atribuido_em=1780000001000)
    )["pode_assumir"] is True
    assert _tecnico_para_dict(tecnico_atribuido)["pode_assumir"] is False
    assert _tecnico_para_dict(status_diferente)["pode_assumir"] is True
    assert _tecnico_para_dict(status_nulo)["status"] == "Não informado"
    assert _tecnico_para_dict(status_nulo)["pode_assumir"] is False


@pytest.mark.parametrize(
    "status",
    [
        "Novo",
        "Em Atendimento",
        "Aguardando Solicitante",
        "Aguardando Mudança",
        "Resolvido",
        "Solução Rejeitada",
    ],
)
def test_assumir_e_atribuir_sao_elegiveis_em_qualquer_status_nao_terminal(status):
    resumo = _tecnico_para_dict(resumo_tecnico(status=status))
    detalhe = _detalhe_para_dict(detalhe_tecnico(status=status))

    assert resumo["pode_assumir"] is True
    assert detalhe["pode_assumir"] is True
    assert detalhe["pode_atribuir"] is True


@pytest.mark.parametrize("status", ["Encerrado", "Cancelado", None, "Desconhecido"])
def test_status_terminal_ou_nao_reconhecido_nao_oferece_acoes(status):
    resumo = _tecnico_para_dict(resumo_tecnico(status=status))
    detalhe = _detalhe_para_dict(
        detalhe_tecnico(
            status=status,
            tecnico=ReferenciaUsuario(id=13, nome="Outro Técnico"),
        )
    )
    estado = novo_estado_tecnico("administrador")
    estado._atualizar_chamado(
        detalhe_tecnico(
            status=status,
            tecnico=ReferenciaUsuario(id=13, nome="Outro Técnico"),
        )
    )

    assert resumo["pode_assumir"] is False
    assert detalhe["pode_assumir"] is False
    assert detalhe["pode_atribuir"] is False
    assert estado.chamado["pode_liberar"] is False


def test_detalhe_mostra_nome_do_bot_somente_quando_persistido():
    automatico = _detalhe_para_dict(
        detalhe_tecnico(criador_sistema="bot_fiscalizacao")
    )
    legado = _detalhe_para_dict(detalhe_tecnico(criador_sistema=None))

    assert automatico["criador_sistema_nome"] == "Bot de Fiscalização"
    assert legado["criador_sistema_nome"] == ""


def test_detalhes_apresentam_autoria_persistida_sem_ampliar_listagens():
    detalhe_gerente = inspect.getsource(paginas_gerente._detalhe)
    detalhe_tecnico = inspect.getsource(paginas_chamados._detalhe_tecnico)
    lista_gerente = inspect.getsource(paginas_gerente._lista)
    fila_tecnica = inspect.getsource(paginas_chamados._fila_tecnico)

    for detalhe in (detalhe_gerente, detalhe_tecnico):
        assert '"criador_sistema_nome"] != ""' in detalhe
        assert "Criado por: " in detalhe
        assert "Origem: " in detalhe

    assert "criador_sistema" not in lista_gerente
    assert "criador_sistema" not in fila_tecnica


def test_assuncao_bem_sucedida_atualiza_detalhe_timeline_e_fila(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(
        resultado_assuncao=detalhe_tecnico(
            tecnico=ReferenciaUsuario(id=9, nome="Técnico 9"),
        ),
        resultado_detalhe=DetalheChamadoTecnico(
            chamado=detalhe_tecnico(
                tecnico=ReferenciaUsuario(id=9, nome="Técnico 9"),
            ),
            timeline=[
                EventoTimelineChamado(
                    id=55,
                    tipo="atribuicao",
                    conteudo=None,
                    visibilidade="interna",
                    criado_em=1780000001000,
                    autor=ReferenciaUsuario(id=9, nome="Técnico 9"),
                    tecnico_anterior=None,
                    tecnico_novo=ReferenciaUsuario(id=9, nome="Técnico 9"),
                )
            ],
            tecnicos=[ReferenciaUsuario(id=9, nome="Técnico 9")],
        ),
        listas={"todos": []},
    )
    monkeypatch.setattr(
        chamados_module,
        "criar_cliente_service_desk",
        lambda: cliente,
    )
    estado = novo_estado_tecnico()
    estado.chamados = [_tecnico_para_dict(resumo_tecnico())]

    executar_evento(ChamadosTecnicoState.assumir, estado, 32)

    assert cliente.assuncoes == [("token-de-teste", 32)]
    assert cliente.atribuicoes == [("token-de-teste", 32, "assumir", None)]
    assert cliente.detalhes == [("token-de-teste", 32)]
    assert cliente.consultas[0][1]["numero"] is None
    assert estado.chamado["status"] == "Novo"
    assert estado.chamado["tecnico_nome"] == "Técnico 9"
    assert estado.chamado["atribuido_em_texto"] != "Não informado"
    assert estado.mensagem_sucesso_responsavel == "Chamado assumido."
    assert estado.timeline[0]["tipo"] == "atribuicao"
    assert estado.timeline[0]["tecnico_novo_nome"] == "Técnico 9"
    assert estado.assumindo_id is None
    assert estado.carregando_fila is False
    assert estado.chamados == []


def test_falha_ao_carregar_outro_detalhe_limpa_timeline_anterior(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(erro_detalhe=RuntimeError("falha de rede"))
    monkeypatch.setattr(
        chamados_module,
        "criar_cliente_service_desk",
        lambda: cliente,
    )
    estado = novo_estado_tecnico()
    evento_chamado_anterior = EventoTimelineChamado(
        id=55,
        tipo="atribuicao",
        conteudo=None,
        visibilidade="interna",
        criado_em=1780000001000,
        autor=ReferenciaUsuario(id=9, nome="Técnico 9"),
        tecnico_anterior=None,
        tecnico_novo=ReferenciaUsuario(id=9, nome="Técnico 9"),
    )
    estado._atualizar_detalhe(
        DetalheChamadoTecnico(
            chamado=detalhe_tecnico(),
            timeline=[evento_chamado_anterior],
            tecnicos=[ReferenciaUsuario(id=9, nome="Técnico 9")],
        )
    )
    object.__setattr__(estado, "chamado_id", "33")

    executar_evento(ChamadosTecnicoState.carregar_detalhe_tecnico, estado)

    assert cliente.detalhes == [("token-de-teste", 33)]
    assert estado.chamado == {}
    assert estado.timeline == []
    assert estado.tecnicos == []
    assert estado.tecnico_alvo_id == ""
    assert estado.mensagem_detalhe_tecnico == MENSAGEM_INDISPONIVEL
    assert estado.detalhe_tecnico_carregado is False


def test_detalhe_confirmado_expoe_campos_do_contrato_e_evitar_renderizacao_vazia():
    estado = novo_estado_tecnico("diretoria")

    estado._atualizar_detalhe(
        DetalheChamadoTecnico(
            chamado=detalhe_tecnico(loja=ReferenciaLoja(id=3, nome="Loja Centro")),
            timeline=[],
            tecnicos=[],
        )
    )

    assert estado.detalhe_tecnico_carregado is True
    assert estado.chamado["id"] == 32
    assert estado.chamado["ativo_nome"] == "Totem de teste"
    assert estado.chamado["loja_nome"] == "Loja Centro"
    assert estado.chamado["categoria_nome"] == "Falha de Rede"
    assert estado.chamado["solicitante_nome"] == "Gerente"


def test_pagina_do_detalhe_so_renderiza_campos_apos_carga_confirmada():
    fonte = inspect.getsource(paginas_chamados._detalhe_tecnico)

    assert "ChamadosTecnicoState.detalhe_tecnico_carregado" in fonte
    assert "ChamadosTecnicoState.chamado[\"loja_nome\"]" in fonte
    assert "ChamadosTecnicoState.chamado[\"ativo_nome\"]" in fonte
    assert "ChamadosTecnicoState.chamado[\"categoria_nome\"]" in fonte
    assert "ChamadosTecnicoState.chamado[\"solicitante_nome\"]" in fonte


def test_conflito_informa_e_recarrega_sem_substituir_detalhe_local(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(erro_assuncao=XanoConflito("detalhe interno"))
    monkeypatch.setattr(
        chamados_module,
        "criar_cliente_service_desk",
        lambda: cliente,
    )
    estado = novo_estado_tecnico()
    detalhe_anterior = {
        "id": 32,
        "tecnico_nome": "Não atribuído",
        "pode_assumir": True,
    }
    estado.chamado = detalhe_anterior
    estado.chamados = [_tecnico_para_dict(resumo_tecnico())]

    executar_evento(ChamadosTecnicoState.assumir, estado, 32)

    assert cliente.assuncoes == [("token-de-teste", 32)]
    assert cliente.consultas[0][1]["numero"] is None
    assert estado.chamado == detalhe_anterior
    assert estado.mensagem_assuncao == "A atribuição do chamado foi alterada por outra operação."
    assert estado.assumindo_id is None
    assert estado.carregando_fila is False


def test_excecao_inesperada_libera_loading_e_nao_expoe_detalhe(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(
        erro_assuncao=RuntimeError("resposta interna sensível")
    )
    monkeypatch.setattr(
        chamados_module,
        "criar_cliente_service_desk",
        lambda: cliente,
    )
    estado = novo_estado_tecnico()
    estado.chamados = [_tecnico_para_dict(resumo_tecnico())]

    executar_evento(ChamadosTecnicoState.assumir, estado, 32)

    assert estado.assumindo_id is None
    assert estado.carregando_fila is False
    assert estado.mensagem_assuncao == MENSAGEM_INDISPONIVEL
    assert "sensível" not in estado.mensagem_assuncao
    assert cliente.consultas[0][1]["numero"] is None


def test_detalhe_tecnico_oferece_gestao_de_responsavel_e_timeline_sem_status():
    fonte = "\n".join(
        (
            inspect.getsource(paginas_chamados._fila_tecnico),
            inspect.getsource(paginas_chamados._detalhe_tecnico),
        )
    ).casefold()

    for acao in ("assumir", "atribuir técnico", "reatribuir técnico", "liberar responsável", "linha do tempo"):
        assert acao in fonte
    for acao in ("resolver", "alterar status", "mudar status"):
        assert acao not in fonte


def test_atribuir_preserva_status_e_recarrega_timeline_do_xano(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    tecnico_anterior = ReferenciaUsuario(id=13, nome="Técnico A")
    tecnico_novo = ReferenciaUsuario(id=14, nome="Técnico B")
    chamado_atribuido = detalhe_tecnico(
        status="Resolvido",
        tecnico=tecnico_novo,
        atribuido_em=1780000002000,
    )
    evento = EventoTimelineChamado(
        id=56,
        tipo="reatribuicao",
        conteudo=None,
        visibilidade="interna",
        criado_em=1780000002000,
        autor=ReferenciaUsuario(id=7, nome="Diretoria"),
        tecnico_anterior=tecnico_anterior,
        tecnico_novo=tecnico_novo,
    )
    cliente = ClienteTecnicoFalso(
        resultado_assuncao=chamado_atribuido,
        resultado_detalhe=DetalheChamadoTecnico(
            chamado=chamado_atribuido,
            timeline=[evento],
            tecnicos=[tecnico_anterior, tecnico_novo],
        ),
        listas={"todos": []},
    )
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico("diretoria")
    estado._atualizar_detalhe(
        DetalheChamadoTecnico(
            chamado=detalhe_tecnico(status="Resolvido", tecnico=tecnico_anterior),
            timeline=[],
            tecnicos=[tecnico_anterior, tecnico_novo],
        )
    )
    estado.selecionar_tecnico_alvo("14")

    executar_evento(ChamadosTecnicoState.atribuir_responsavel, estado)

    assert cliente.atribuicoes == [("token-de-teste", 32, "atribuir", 14)]
    assert cliente.detalhes == [("token-de-teste", 32)]
    assert estado.chamado["status"] == "Resolvido"
    assert estado.chamado["tecnico_nome"] == "Técnico B"
    assert estado.timeline[0]["titulo"] == "Reatribuição"
    assert estado.timeline[0]["tecnico_anterior_nome"] == "Técnico A"
    assert estado.timeline[0]["tecnico_novo_nome"] == "Técnico B"


@pytest.mark.parametrize(
    ("role", "usuario_id", "responsavel_id", "pode_liberar"),
    [
        ("tecnico", 13, 13, True),
        ("tecnico", 13, 14, False),
        ("diretoria", 7, 14, True),
        ("administrador", 6, 14, True),
    ],
)
def test_liberacao_visivel_conforme_perfil_e_responsavel(
    role, usuario_id, responsavel_id, pode_liberar
):
    estado = novo_estado_tecnico(role)
    object.__setattr__(estado, "usuario_id", usuario_id)

    estado._atualizar_chamado(
        detalhe_tecnico(
            status="Em Atendimento",
            tecnico=ReferenciaUsuario(id=responsavel_id, nome="Técnico responsável"),
        )
    )

    assert estado.chamado["pode_liberar"] is pode_liberar


def test_liberar_nao_envia_tecnico_id_nem_altera_status(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(
        resultado_assuncao=detalhe_tecnico(status="Em Atendimento", tecnico=None),
        resultado_detalhe=DetalheChamadoTecnico(
            chamado=detalhe_tecnico(status="Em Atendimento", tecnico=None),
            timeline=[],
            tecnicos=[ReferenciaUsuario(id=13, nome="Técnico A")],
        ),
        listas={"todos": []},
    )
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico("administrador")
    estado._atualizar_chamado(
        detalhe_tecnico(
            status="Em Atendimento",
            tecnico=ReferenciaUsuario(id=13, nome="Técnico A"),
        )
    )

    executar_evento(ChamadosTecnicoState.liberar_responsavel, estado)

    assert cliente.atribuicoes == [("token-de-teste", 32, "liberar", None)]
    assert estado.chamado["status"] == "Em Atendimento"
    assert estado.chamado["tecnico_nome"] == "Não atribuído"


def test_operacao_de_atribuicao_e_bloqueada_visualmente_em_terminal(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso()
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico("diretoria")
    estado._atualizar_detalhe(
        DetalheChamadoTecnico(
            chamado=detalhe_tecnico(
                status="Cancelado",
                tecnico=ReferenciaUsuario(id=13, nome="Técnico A"),
            ),
            timeline=[],
            tecnicos=[ReferenciaUsuario(id=14, nome="Técnico B")],
        )
    )
    estado.tecnico_alvo_id = "14"

    executar_evento(ChamadosTecnicoState.atribuir_responsavel, estado)
    executar_evento(ChamadosTecnicoState.liberar_responsavel, estado)

    assert cliente.atribuicoes == []
    assert estado.chamado["pode_atribuir"] is False
    assert estado.chamado["pode_liberar"] is False
