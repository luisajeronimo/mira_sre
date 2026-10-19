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
    PreferenciaFilaTecnica,
    DetalheChamadoTecnico,
    EventoTimelineChamado,
    ReferenciaAtivo,
    ReferenciaCategoria,
    ReferenciaLoja,
    ReferenciaUsuario,
)
from app.services.xano import (
    XanoConflito,
    XanoContratoInvalido,
    XanoEntradaInvalida,
    XanoIndisponivel,
    XanoNaoAutenticado,
    XanoNaoAutorizado,
)
from app.states.auth import AuthState, MENSAGEM_INDISPONIVEL, MENSAGEM_NAO_AUTORIZADO
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
    prioridade="Alta",
    categoria=None,
    ultima_atualizacao_em=1780000000000,
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
        prioridade=prioridade,
        origem="manual",
        criado_em=1780000000000,
        ultima_atualizacao_em=ultima_atualizacao_em,
        sla_horas_aplicado=2,
        ativo=ReferenciaAtivo(id=1, nome_ativo="Totem de teste"),
        categoria=categoria or ReferenciaCategoria(id=2, nome="Falha de Rede"),
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
        categorias=None,
        erro_categorias=None,
        resultado_save=None,
        erro_save=None,
        resultado_comentario=None,
        erro_comentario=None,
        listas=None,
        preferencias=None,
        erro_preferencia=None,
    ):
        self.resultado_assuncao = resultado_assuncao or detalhe_tecnico(
            tecnico=ReferenciaUsuario(id=9, nome="Técnico 9")
        )
        self.erro_assuncao = erro_assuncao
        self.resultado_detalhe = resultado_detalhe
        self.erro_detalhe = erro_detalhe
        self.erro_ativos = erro_ativos
        self.categorias = categorias or [
            type("Categoria", (), {"id": 2, "nome": "Falha de Rede"})()
        ]
        self.erro_categorias = erro_categorias
        self.resultado_save = resultado_save
        self.erro_save = erro_save
        self.resultado_comentario = resultado_comentario
        self.erro_comentario = erro_comentario
        self.listas = listas or {}
        self.preferencias = preferencias or {}
        self.erro_preferencia = erro_preferencia
        self.consultas = []
        self.assuncoes = []
        self.detalhes = []
        self.atribuicoes = []
        self.saves = []
        self.comentarios = []
        self.preferencias_salvas = []

    async def listar_chamados_tecnico(self, token, **filtros):
        self.consultas.append((token, filtros))
        resultado = self.listas.get("resultado", [])
        if isinstance(resultado, Exception):
            raise resultado
        return ListaChamadosGerente(items=resultado, total=len(resultado))

    async def listar_ativos_tecnico(self, token):
        if self.erro_ativos is not None:
            raise self.erro_ativos
        return []

    async def obter_preferencia_fila_tecnica(self, token, *, escopo):
        if self.erro_preferencia is not None:
            raise self.erro_preferencia
        return self.preferencias.get(escopo, PreferenciaFilaTecnica(
            escopo=escopo, numero=None, status=None, ativo_id=None,
            data_inicio=None, data_fim=None, prioridade=None,
            ordenar_por="numero", direcao="DESC",
        ))

    async def salvar_preferencia_fila_tecnica(self, token, **payload):
        self.preferencias_salvas.append((token, payload))
        return PreferenciaFilaTecnica(
            escopo=payload["escopo"], numero=payload["numero"],
            status=payload["status"], ativo_id=payload["ativo_id"],
            data_inicio=payload["data_inicio"], data_fim=payload["data_fim"],
            prioridade=payload["prioridade"], ordenar_por=payload["ordenar_por"],
            direcao=payload["direcao"],
        )

    async def listar_categorias_tratativa(self, token):
        if self.erro_categorias is not None:
            raise self.erro_categorias
        return self.categorias

    async def salvar_tratativa_chamado(self, token, chamado_id, **payload):
        self.saves.append((token, chamado_id, payload))
        if self.erro_save is not None:
            raise self.erro_save
        return self.resultado_save or DetalheChamadoTecnico(
            chamado=self.resultado_assuncao,
            timeline=[],
            tecnicos=[ReferenciaUsuario(id=9, nome="Técnico 9")],
        )

    async def criar_comentario_operacional(self, token, chamado_id, **payload):
        self.comentarios.append((token, chamado_id, payload))
        if self.erro_comentario is not None:
            raise self.erro_comentario
        return self.resultado_comentario or DetalheChamadoTecnico(
            chamado=self.resultado_assuncao,
            timeline=[],
            tecnicos=[ReferenciaUsuario(id=9, nome="Técnico 9")],
        )

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


def test_marcadores_privados_da_fila_sao_backend_only():
    assert "_auth_token" in ChamadosTecnicoState.backend_vars
    assert "_token_contexto_fila" in ChamadosTecnicoState.backend_vars
    assert "_auth_token" not in ChamadosTecnicoState.base_vars
    assert "_token_contexto_fila" not in ChamadosTecnicoState.base_vars


def test_filtro_de_responsavel_usa_id_e_nao_atribuido_sem_comparar_nomes():
    estado = novo_estado_tecnico()
    estado.tecnicos = [{"id": 17, "nome": "Ana Técnica"}]

    estado.filtro_responsavel = "17 — Ana Técnica"
    filtros = estado._filtros_solicitados()
    assert filtros is not None
    assert filtros[6:8] == (17, False)
    assert "Responsável: Ana Técnica" in filtros[-1]

    estado.filtro_responsavel = "0 — Não atribuído"
    filtros = estado._filtros_solicitados()
    assert filtros is not None
    assert filtros[6:8] == (None, True)


def test_fila_global_exibe_responsavel_ordenavel_sem_coluna_atribuido_em():
    fonte = inspect.getsource(paginas_chamados._fila_tecnico)
    assert '_cabecalho_ordenavel("Responsável", "responsavel")' in fonte
    assert 'rx.table.column_header_cell("Atribuído em")' not in fonte
    assert 'rx.table.cell(item["atribuido_em_texto"])' not in fonte


def liberar_validacao_de_sessao(monkeypatch):
    async def validar(_estado):
        return None

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
    assert cliente.consultas == [("token-de-teste", {"numero": 102, "status": "Novo", "ativo_id": None, "data_inicio": None, "data_fim": None, "somente_atribuidos_a_mim": False})]
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

    assert asyncio.run(estado._validar_acesso_fila()) == "/inicio"


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

    assert cliente.consultas == [("token-de-teste", {"numero": 102, "status": None, "ativo_id": None, "data_inicio": None, "data_fim": None, "somente_atribuidos_a_mim": False})]


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
    assert cliente.consultas == [("token-de-teste", {"numero": None, "status": None, "ativo_id": None, "data_inicio": None, "data_fim": None, "somente_atribuidos_a_mim": False})]


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


def test_falha_ao_salvar_preferencia_nao_confirma_lista_candidata(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    anterior = _tecnico_para_dict(resumo_tecnico(status="Novo"))
    candidato = resumo_tecnico(status="Encerrado")
    cliente = ClienteTecnicoFalso(listas={"resultado": [candidato]})

    async def falhar_save(_token, **_payload):
        raise XanoIndisponivel("save indisponível")

    cliente.salvar_preferencia_fila_tecnica = falhar_save
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado.chamados = [anterior]
    estado.filtro_status = "Encerrado"

    executar_evento(ChamadosTecnicoState.aplicar_filtros, estado)

    assert cliente.consultas[0][1]["status"] == "Encerrado"
    assert estado.chamados == [anterior]
    assert estado.status_aplicado == ""
    assert estado.filtro_status == ""


def test_prioridade_e_ordenacao_sao_persistidas_apos_consulta(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso()
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado.filtro_prioridade = "Urgente"

    executar_evento(ChamadosTecnicoState.aplicar_filtros, estado)
    executar_evento(ChamadosTecnicoState.ordenar_fila, estado, "titulo")

    assert cliente.consultas[0][1]["prioridade"] == "Urgente"
    assert cliente.consultas[-1][1]["ordenar_por"] == "titulo"
    assert cliente.consultas[-1][1]["direcao"] == "ASC"
    assert cliente.preferencias_salvas[-1][1]["ordenar_por"] == "titulo"


@pytest.mark.parametrize("falha", ["consulta", "save"])
def test_ordenacao_candidata_nao_altera_state_confirmado_em_falha(monkeypatch, falha):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso()
    estado = novo_estado_tecnico()

    async def falhar_consulta(_token, **_filtros):
        assert (estado.ordenar_por, estado.direcao_ordenacao) == ("numero", "DESC")
        raise XanoIndisponivel("consulta indisponível")

    async def falhar_save(_token, **_payload):
        assert (estado.ordenar_por, estado.direcao_ordenacao) == ("numero", "DESC")
        raise XanoIndisponivel("save indisponível")

    if falha == "consulta":
        cliente.listar_chamados_tecnico = falhar_consulta
    else:
        cliente.salvar_preferencia_fila_tecnica = falhar_save
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)

    executar_evento(ChamadosTecnicoState.ordenar_fila, estado, "titulo")

    assert (estado.ordenar_por, estado.direcao_ordenacao) == ("numero", "DESC")


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


def test_tecnico_alterna_para_atribuidos_a_mim_sem_vazar_filtros_do_outro_escopo(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso()
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado.numero_aplicado = 38
    estado.status_aplicado = "Novo"
    estado.filtros_aplicados = ["Número: 38", "Status: Novo"]

    executar_evento(
        ChamadosTecnicoState.selecionar_escopo_rapido,
        estado,
        "atribuidos_a_mim",
    )

    assert estado.escopo_rapido == "atribuidos_a_mim"
    assert cliente.consultas[-1][1] == {
        "numero": None,
        "status": None,
        "ativo_id": None,
        "data_inicio": None,
        "data_fim": None,
        "somente_atribuidos_a_mim": True,
    }


def test_limpar_filtros_preserva_escopo_atribuidos_a_mim(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso()
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado.escopo_rapido = "atribuidos_a_mim"
    estado.usuario_id_contexto_fila = 9
    estado._token_contexto_fila = "token-de-teste"
    estado.versao_sessao_contexto_fila = 0

    executar_evento(ChamadosTecnicoState.limpar_filtros, estado)

    assert estado.escopo_rapido == "atribuidos_a_mim"
    assert cliente.consultas[-1][1]["somente_atribuidos_a_mim"] is True


def test_troca_de_identidade_limpa_dados_e_filtros_antes_da_fila_global(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    antigo = _tecnico_para_dict(resumo_tecnico())
    novo = resumo_tecnico(tecnico=ReferenciaUsuario(id=18, nome="Diretoria"))
    cliente = ClienteTecnicoFalso(listas={"resultado": [novo]})
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado.usuario_id_contexto_fila = 9
    estado._token_contexto_fila = "token-tecnico"
    estado.escopo_rapido = "atribuidos_a_mim"
    estado.numero_aplicado = 38
    estado.filtro_numero = "38"
    estado.filtro_numero_confirmado = "38"
    estado.filtros_aplicados = ["Número: 38"]
    estado.ativos = ["1 — Totem protegido"]
    estado.chamados = [antigo]
    estado.total_chamados = 1
    object.__setattr__(estado, "_auth_token", "token-diretoria")
    object.__setattr__(estado, "role", "diretoria")
    object.__setattr__(estado, "usuario_id", 18)

    executar_evento(ChamadosTecnicoState.carregar_fila, estado)

    assert cliente.consultas == [
        (
            "token-diretoria",
            {
                "numero": None,
                "status": None,
                "ativo_id": None,
                "data_inicio": None,
                "data_fim": None,
                "somente_atribuidos_a_mim": False,
            },
        )
    ]
    assert estado.escopo_rapido == "todos"
    assert estado.numero_aplicado is None
    assert estado.filtro_numero == ""
    assert estado.filtros_aplicados == []
    assert estado.chamados == [_tecnico_para_dict(novo)]
    assert antigo not in estado.chamados


def test_reentrada_do_mesmo_tecnico_recarrega_preferencia_do_escopo_todos(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(preferencias={"todos": PreferenciaFilaTecnica(
        escopo="todos", numero=38, status="Novo", ativo_id=None,
        data_inicio=None, data_fim=None, prioridade=None,
        ordenar_por="numero", direcao="DESC",
    )})
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado.usuario_id_contexto_fila = 9
    estado._token_contexto_fila = "token-de-teste"
    estado.versao_sessao_contexto_fila = 0
    estado.escopo_rapido = "atribuidos_a_mim"
    estado.numero_aplicado = 38
    estado.status_aplicado = "Novo"
    estado.filtros_aplicados = ["Número: 38", "Status: Novo"]
    object.__setattr__(estado, "_versao_sessao", 1)

    executar_evento(ChamadosTecnicoState.carregar_fila, estado)

    assert estado.escopo_rapido == "todos"
    assert cliente.consultas[-1] == (
        "token-de-teste",
        {
            "numero": 38,
            "status": "Novo",
            "ativo_id": None,
            "data_inicio": None,
            "data_fim": None,
            "somente_atribuidos_a_mim": False,
        },
    )
    assert estado.filtros_aplicados == ["Número: 38", "Status: Novo"]


def test_carga_inicial_reaproveita_responsaveis_retornados_pela_fila(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(listas={"resultado": [
        resumo_tecnico(tecnico=ReferenciaUsuario(id=17, nome="Ana Técnica")),
        resumo_tecnico(tecnico=ReferenciaUsuario(id=11, nome="Bruno Técnico")),
    ]})
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()

    executar_evento(ChamadosTecnicoState.carregar_fila, estado)

    assert estado.tecnicos == [
        {"id": 17, "nome": "Ana Técnica"},
        {"id": 11, "nome": "Bruno Técnico"},
    ]
    assert estado.responsaveis_filtro == [
        "0 — Não atribuído", "17 — Ana Técnica", "11 — Bruno Técnico"
    ]


def test_preferencia_por_responsavel_restaura_rotulo_do_item_retornado(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(
        listas={"resultado": [
            resumo_tecnico(tecnico=ReferenciaUsuario(id=17, nome="Ana Técnica"))
        ]},
        preferencias={"todos": PreferenciaFilaTecnica(
            escopo="todos", numero=None, status=None, ativo_id=None,
            data_inicio=None, data_fim=None, prioridade=None,
            responsavel_id=17, somente_nao_atribuido=False,
            ordenar_por="numero", direcao="DESC",
        )},
    )
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()

    executar_evento(ChamadosTecnicoState.carregar_fila, estado)

    assert cliente.consultas[-1][1]["responsavel_id"] == 17
    assert estado.filtro_responsavel == "17 — Ana Técnica"
    assert estado.filtro_responsavel_confirmado == "17 — Ana Técnica"
    assert "Responsável: Ana Técnica" in estado.filtros_aplicados


def test_preferencia_por_responsavel_vazia_preserva_id_transitorio_ao_reaplicar(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(
        preferencias={"todos": PreferenciaFilaTecnica(
            escopo="todos", numero=None, status=None, ativo_id=None,
            data_inicio=None, data_fim=None, prioridade=None,
            responsavel_id=17, somente_nao_atribuido=False,
            ordenar_por="numero", direcao="DESC",
        )},
    )
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()

    executar_evento(ChamadosTecnicoState.carregar_fila, estado)

    assert estado.filtro_responsavel == "17 — Técnico não listado"
    assert estado.responsaveis_filtro == [
        "0 — Não atribuído", "17 — Técnico não listado"
    ]
    assert "Responsável: Técnico não listado" in estado.filtros_aplicados

    estado.filtro_status = "Novo"
    executar_evento(ChamadosTecnicoState.aplicar_filtros, estado)

    assert cliente.consultas[-1][1]["responsavel_id"] == 17
    assert cliente.preferencias_salvas[-1][1]["responsavel_id"] == 17

    cliente.listas["resultado"] = [
        resumo_tecnico(tecnico=ReferenciaUsuario(id=17, nome="Ana Técnica"))
    ]
    executar_evento(ChamadosTecnicoState.aplicar_filtros, estado)

    assert estado.filtro_responsavel == "17 — Ana Técnica"
    assert estado.filtro_responsavel_confirmado == "17 — Ana Técnica"
    assert estado.responsaveis_filtro == ["0 — Não atribuído", "17 — Ana Técnica"]
    assert estado.responsavel_filtro_transitorio_id is None
    assert "Responsável: Ana Técnica" in estado.filtros_aplicados


@pytest.mark.parametrize(
    ("erro", "sessao_confirmada", "mensagem"),
    [
        (XanoNaoAutenticado("expirado"), False, MENSAGEM_INDISPONIVEL),
        (XanoNaoAutorizado("negado"), True, MENSAGEM_NAO_AUTORIZADO),
    ],
)
def test_troca_de_identidade_distingue_401_e_403_sem_reusar_dados_protegidos(
    monkeypatch, erro, sessao_confirmada, mensagem
):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(listas={"resultado": erro})
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    raiz = AuthState(_reflex_internal_init=True)
    estado = ChamadosTecnicoState(parent_state=raiz, _reflex_internal_init=True)
    object.__setattr__(raiz, "_auth_token", "token-diretoria")
    object.__setattr__(raiz, "sessao_confirmada", True)
    object.__setattr__(raiz, "role", "diretoria")
    object.__setattr__(raiz, "usuario_id", 18)
    estado.usuario_id_contexto_fila = 9
    estado._token_contexto_fila = "token-tecnico"
    estado.escopo_rapido = "atribuidos_a_mim"
    estado.chamados = [_tecnico_para_dict(resumo_tecnico())]

    eventos = executar_evento(ChamadosTecnicoState.carregar_fila, estado)

    assert cliente.consultas[-1][1]["somente_atribuidos_a_mim"] is False
    assert estado.chamados == []
    assert estado.escopo_rapido == "todos"
    assert raiz.sessao_confirmada is sessao_confirmada
    if isinstance(erro, XanoNaoAutenticado):
        assert eventos[-1].args[0][1]._var_value == "/login"
    else:
        assert estado.mensagem_fila == mensagem


@pytest.mark.parametrize("role", ["diretoria", "administrador"])
def test_diretoria_e_admin_nao_alteram_para_escopo_pessoal(monkeypatch, role):
    cliente = ClienteTecnicoFalso()
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico(role)

    executar_evento(
        ChamadosTecnicoState.selecionar_escopo_rapido,
        estado,
        "atribuidos_a_mim",
    )

    assert estado.escopo_rapido == "todos"
    assert cliente.consultas == []


def test_erro_da_fila_nao_renderiza_empty_state_simultaneamente():
    fonte = inspect.getsource(paginas_chamados._fila_tecnico)

    assert 'ChamadosTecnicoState.mensagem_fila != ""' in fonte
    assert fonte.index('ChamadosTecnicoState.mensagem_fila != ""') < fonte.index(
        'ChamadosTecnicoState.chamados.length() == 0'
    )


def test_visao_rapida_esta_fora_dos_filtros_e_so_aparece_para_tecnico():
    fonte = inspect.getsource(paginas_chamados._fila_tecnico)

    assert fonte.index('"Atribuídos a mim"') < fonte.index('rx.text("Filtros"')
    assert 'AuthState.role == "tecnico"' in fonte
    assert "Atribuídos a outros Técnicos" not in fonte


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
    assert "pode_liberar" not in estado.chamado


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


def test_carregar_detalhe_copia_estado_confirmado_para_pendente_e_catalogo(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(
        resultado_detalhe=DetalheChamadoTecnico(
            chamado=detalhe_tecnico(
                tecnico=ReferenciaUsuario(id=9, nome="Técnico 9"),
                categoria=ReferenciaCategoria(id=9, nome="Categoria inativa"),
            ),
            timeline=[],
            tecnicos=[ReferenciaUsuario(id=9, nome="Técnico 9")],
        ),
        categorias=[type("Categoria", (), {"id": 2, "nome": "Falha de Rede"})()],
    )
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    object.__setattr__(estado, "chamado_id", "32")

    executar_evento(ChamadosTecnicoState.carregar_detalhe_tecnico, estado)

    assert estado.responsavel_confirmado_id == 9
    assert estado.responsavel_pendente_id == "9"
    assert estado.status_confirmado == estado.status_pendente == "Novo"
    assert estado.prioridade_confirmada == estado.prioridade_pendente == "Alta"
    assert estado.categoria_confirmada_id == 9
    assert estado.categoria_pendente_id == "9"
    assert estado.categorias_tratativa == [{"id": 2, "nome": "Falha de Rede"}]


def test_edicao_pendente_nao_persiste_e_descartar_restaura_confirmado():
    estado = novo_estado_tecnico()
    estado._atualizar_detalhe(
        DetalheChamadoTecnico(
            chamado=detalhe_tecnico(tecnico=ReferenciaUsuario(id=9, nome="Técnico 9")),
            timeline=[],
            tecnicos=[ReferenciaUsuario(id=9, nome="Técnico 9"), ReferenciaUsuario(id=10, nome="Técnico 10")],
        ),
        categorias=[{"id": 2, "nome": "Falha de Rede"}],
    )

    ChamadosTecnicoState.alterar_responsavel_pendente.fn(estado, "10")
    ChamadosTecnicoState.alterar_prioridade_pendente.fn(estado, "Urgente")
    ChamadosTecnicoState.alterar_status_pendente.fn(estado, "Em Atendimento")

    assert estado.responsavel_confirmado_id == 9
    assert estado.responsavel_pendente_id == "10"
    assert estado.prioridade_confirmada == "Alta"
    assert estado.prioridade_pendente == "Urgente"
    assert estado.ha_mudanca_funcional_pendente is True

    ChamadosTecnicoState.descartar_mudancas_tratativa.fn(estado)

    assert estado.responsavel_pendente_id == "9"
    assert estado.status_pendente == "Novo"
    assert estado.prioridade_pendente == "Alta"
    assert estado.comentario_status_pendente == ""
    assert estado.ha_mudanca_funcional_pendente is False


def test_save_tratativa_usa_pendente_e_substitui_estado_por_detalhe_canonico(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    retorno = DetalheChamadoTecnico(
        chamado=detalhe_tecnico(
            status="Em Atendimento",
            prioridade="Urgente",
            tecnico=ReferenciaUsuario(id=10, nome="Técnico 10"),
            atribuido_em=1780000002000,
            ultima_atualizacao_em=1780000002000,
        ),
        timeline=[],
        tecnicos=[ReferenciaUsuario(id=9, nome="Técnico 9"), ReferenciaUsuario(id=10, nome="Técnico 10")],
    )
    cliente = ClienteTecnicoFalso(resultado_save=retorno)
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado._atualizar_detalhe(
        DetalheChamadoTecnico(
            chamado=detalhe_tecnico(tecnico=ReferenciaUsuario(id=9, nome="Técnico 9")),
            timeline=[],
            tecnicos=retorno.tecnicos,
        ),
        categorias=[{"id": 2, "nome": "Falha de Rede"}],
    )
    ChamadosTecnicoState.alterar_responsavel_pendente.fn(estado, "10")
    ChamadosTecnicoState.alterar_prioridade_pendente.fn(estado, "Urgente")
    ChamadosTecnicoState.alterar_status_pendente.fn(estado, "Em Atendimento")
    ChamadosTecnicoState.alterar_comentario_status_pendente.fn(estado, "Início")
    ChamadosTecnicoState.alterar_visibilidade_comentario_status_pendente.fn(estado, "interna")

    executar_evento(ChamadosTecnicoState.salvar_tratativa, estado)

    assert cliente.saves == [
        (
            "token-de-teste",
            32,
            {
                "tecnico_id": 10,
                "status": "Em Atendimento",
                "prioridade": "Urgente",
                "categorias_servico_id": 2,
                "ultima_atualizacao_em": 1780000000000,
                "comentario_status": "Início",
                "visibilidade_comentario_status": "interna",
            },
        )
    ]
    assert estado.status_confirmado == estado.status_pendente == "Em Atendimento"
    assert estado.prioridade_confirmada == estado.prioridade_pendente == "Urgente"
    assert estado.responsavel_confirmado_id == 10
    assert estado.responsavel_pendente_id == "10"
    assert estado.ultima_atualizacao_confirmada == 1780000002000
    assert estado.comentario_status_pendente == ""
    assert estado.mensagem_sucesso_tratativa == "Alterações salvas."


def test_save_nao_status_envia_comentario_opcional_uma_unica_vez(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso()
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado._atualizar_detalhe(
        DetalheChamadoTecnico(chamado=detalhe_tecnico(), timeline=[], tecnicos=[])
    )
    ChamadosTecnicoState.alterar_prioridade_pendente.fn(estado, "Urgente")
    ChamadosTecnicoState.alterar_comentario_status_pendente.fn(
        estado, "Prioridade elevada após nova análise."
    )
    ChamadosTecnicoState.alterar_visibilidade_comentario_status_pendente.fn(
        estado, "interna"
    )

    executar_evento(ChamadosTecnicoState.salvar_tratativa, estado)

    assert cliente.saves[0][2]["comentario_status"] == "Prioridade elevada após nova análise."
    assert cliente.saves[0][2]["visibilidade_comentario_status"] == "interna"
    assert cliente.comentarios == []


def test_salvar_sem_mudanca_funcional_publica_somente_comentario(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    comentario = EventoTimelineChamado(
        id=90,
        tipo="comentario",
        conteudo="Comentário sem alteração funcional.",
        visibilidade="publica",
        criado_em=1780000004000,
        autor=ReferenciaUsuario(id=9, nome="Técnico 9"),
        tecnico_anterior=None,
        tecnico_novo=None,
    )
    cliente = ClienteTecnicoFalso(
        resultado_comentario=DetalheChamadoTecnico(
            chamado=detalhe_tecnico(ultima_atualizacao_em=1780000004000),
            timeline=[comentario],
            tecnicos=[],
        )
    )
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado._atualizar_detalhe(
        DetalheChamadoTecnico(chamado=detalhe_tecnico(), timeline=[], tecnicos=[])
    )
    ChamadosTecnicoState.alterar_comentario_status_pendente.fn(
        estado, "Comentário sem alteração funcional."
    )

    executar_evento(ChamadosTecnicoState.salvar_tratativa, estado)

    assert cliente.saves == []
    assert cliente.comentarios == [
        (
            "token-de-teste",
            32,
            {"conteudo": "Comentário sem alteração funcional.", "visibilidade": "publica"},
        )
    ]
    assert estado.timeline[0]["tipo"] == "comentario"
    assert estado.mensagem_sucesso_tratativa == "Comentário adicionado."


def test_salvar_fica_indisponivel_sem_alteracao_ou_comentario():
    estado = novo_estado_tecnico()
    estado._atualizar_detalhe(
        DetalheChamadoTecnico(chamado=detalhe_tecnico(), timeline=[], tecnicos=[])
    )

    assert estado.ha_rascunho_pendente is False
    assert estado.pode_salvar_tratativa is False


def test_timeline_agrupa_por_id_estruturado_e_lista_todos_os_diffs():
    comentario = EventoTimelineChamado(
        id=70,
        tipo="comentario",
        conteudo="Ação validada.",
        visibilidade="publica",
        criado_em=1780000003000,
        autor=ReferenciaUsuario(id=9, nome="Técnico 9"),
        tecnico_anterior=None,
        tecnico_novo=None,
    )
    alteracao = EventoTimelineChamado(
        id=71,
        tipo="alteracao_chamado",
        conteudo=None,
        visibilidade="interna",
        criado_em=1780000003000,
        autor=ReferenciaUsuario(id=9, nome="Técnico 9"),
        tecnico_anterior=None,
        tecnico_novo=None,
        alteracoes={
            "comentario_interacao_id": 70,
            "responsavel": {"anterior": None, "resultante": 10},
            "prioridade": {"anterior": "Alta", "resultante": "Urgente"},
            "categoria": {"anterior": 2, "resultante": 3},
        },
    )
    estado = novo_estado_tecnico()

    estado._atualizar_detalhe(
        DetalheChamadoTecnico(
            chamado=detalhe_tecnico(),
            timeline=[alteracao, comentario],
            tecnicos=[
                ReferenciaUsuario(id=9, nome="Técnico 9"),
                ReferenciaUsuario(id=10, nome="Técnico 10"),
            ],
        ),
        categorias=[
            {"id": 2, "nome": "Falha de Rede"},
            {"id": 3, "nome": "Falha de Energia"},
        ],
    )

    assert len(estado.timeline) == 1
    assert estado.timeline[0]["comentario_conteudo"] == "Ação validada."
    assert estado.timeline[0]["comentario_visibilidade_texto"] == "Público"
    assert estado.timeline[0]["alteracoes_detalhadas"] == [
        {"campo": "Responsável", "anterior": "Não atribuído", "resultante": "Técnico 10"},
        {"campo": "Prioridade", "anterior": "Alta", "resultante": "Urgente"},
        {"campo": "Categoria", "anterior": "Falha de Rede", "resultante": "Falha de Energia"},
    ]


@pytest.mark.parametrize(
    "status",
    ["Resolvido", "Aguardando Solicitante", "Cancelado"],
)
def test_status_publico_obrigatorio_no_rascunho(status):
    estado = novo_estado_tecnico()
    estado._atualizar_detalhe(DetalheChamadoTecnico(chamado=detalhe_tecnico(), timeline=[], tecnicos=[]))

    ChamadosTecnicoState.alterar_status_pendente.fn(estado, status)
    ChamadosTecnicoState.alterar_comentario_status_pendente.fn(estado, "Justificativa")
    ChamadosTecnicoState.alterar_visibilidade_comentario_status_pendente.fn(estado, "interna")

    assert estado.status_pendente_exige_comentario_publico is True
    assert estado.visibilidade_comentario_status_pendente == "publica"
    assert estado.pode_salvar_tratativa is True


@pytest.mark.parametrize("visibilidade", ["publica", "interna"])
def test_status_nao_restrito_aceita_visibilidades_no_rascunho(visibilidade):
    estado = novo_estado_tecnico()
    estado._atualizar_detalhe(DetalheChamadoTecnico(chamado=detalhe_tecnico(), timeline=[], tecnicos=[]))

    ChamadosTecnicoState.alterar_status_pendente.fn(estado, "Encerrado")
    ChamadosTecnicoState.alterar_comentario_status_pendente.fn(estado, "Justificativa")
    ChamadosTecnicoState.alterar_visibilidade_comentario_status_pendente.fn(estado, visibilidade)

    assert estado.status_pendente_exige_comentario_publico is False
    assert estado.pode_salvar_tratativa is True


def test_terminal_bloqueia_edicao_e_save_sem_chamar_service(monkeypatch):
    cliente = ClienteTecnicoFalso()
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado._atualizar_detalhe(DetalheChamadoTecnico(chamado=detalhe_tecnico(status="Encerrado"), timeline=[], tecnicos=[]))

    ChamadosTecnicoState.alterar_prioridade_pendente.fn(estado, "Urgente")
    executar_evento(ChamadosTecnicoState.salvar_tratativa, estado)

    assert estado.edicao_funcional_bloqueada is True
    assert estado.prioridade_pendente == "Alta"
    assert cliente.saves == []
    assert "nenhuma alteração" in estado.mensagem_tratativa.casefold()


def test_conflito_recarrega_detalhe_canonico_e_descarta_rascunho(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    atual = DetalheChamadoTecnico(
        chamado=detalhe_tecnico(prioridade="Baixa", ultima_atualizacao_em=1780000003000),
        timeline=[],
        tecnicos=[],
    )
    cliente = ClienteTecnicoFalso(
        erro_save=XanoConflito("conflito"),
        resultado_detalhe=atual,
    )
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado._atualizar_detalhe(DetalheChamadoTecnico(chamado=detalhe_tecnico(), timeline=[], tecnicos=[]))
    ChamadosTecnicoState.alterar_prioridade_pendente.fn(estado, "Urgente")

    executar_evento(ChamadosTecnicoState.salvar_tratativa, estado)

    assert cliente.saves
    assert cliente.detalhes == [("token-de-teste", 32)]
    assert estado.prioridade_confirmada == estado.prioridade_pendente == "Baixa"
    assert estado.ultima_atualizacao_confirmada == 1780000003000
    assert "recarregado" in estado.mensagem_tratativa


def test_erro_de_validacao_nao_confirma_rascunho(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    cliente = ClienteTecnicoFalso(erro_save=XanoEntradaInvalida("inválido"))
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado._atualizar_detalhe(DetalheChamadoTecnico(chamado=detalhe_tecnico(), timeline=[], tecnicos=[]))
    ChamadosTecnicoState.alterar_prioridade_pendente.fn(estado, "Urgente")

    executar_evento(ChamadosTecnicoState.salvar_tratativa, estado)

    assert estado.prioridade_confirmada == "Alta"
    assert estado.prioridade_pendente == "Urgente"
    assert estado.mensagem_sucesso_tratativa == ""
    assert estado.mensagem_tratativa == "Os dados informados são inválidos."


def test_pagina_do_detalhe_so_renderiza_campos_apos_carga_confirmada():
    fonte = inspect.getsource(paginas_chamados._detalhe_tecnico)

    assert "ChamadosTecnicoState.detalhe_tecnico_carregado" in fonte
    assert "ChamadosTecnicoState.chamado[\"loja_nome\"]" in fonte
    assert "ChamadosTecnicoState.chamado[\"ativo_nome\"]" in fonte
    assert "ChamadosTecnicoState.chamado[\"categoria_nome\"]" in fonte
    assert "ChamadosTecnicoState.chamado[\"solicitante_nome\"]" in fonte


def test_detalhe_tecnico_usa_um_unico_grid_sem_acao_separada_de_comentario():
    fonte = "\n".join(
        (
            inspect.getsource(paginas_chamados._fila_tecnico),
            inspect.getsource(paginas_chamados._detalhe_tecnico),
        )
    ).casefold()

    for acao in ("assumir", "atribuir técnico", "reatribuir técnico", "liberar responsável"):
        assert acao not in fonte
    assert '"adicionar comentário"' not in fonte
    assert 'rx.text("tratativa"' not in fonte
    assert 'columns="3"' in fonte
    for controle in (
        'rx.text("responsável"',
        'rx.text("status"',
        'rx.text("prioridade"',
        'rx.text("categoria"',
    ):
        assert controle in fonte
        assert fonte.count(controle) == 1
    for controle in (
        'rx.text("comentário"',
        'rx.text("descrição"',
        '"linha do tempo"',
    ):
        assert controle in fonte


def test_terminal_comenta_pelo_unico_salvar_e_atualiza_detalhe_canonico(monkeypatch):
    liberar_validacao_de_sessao(monkeypatch)
    comentario = EventoTimelineChamado(
        id=88,
        tipo="comentario",
        conteudo="Atualização em chamado encerrado.",
        visibilidade="interna",
        criado_em=1780000003000,
        autor=ReferenciaUsuario(id=9, nome="Técnico 9"),
        tecnico_anterior=None,
        tecnico_novo=None,
    )
    cliente = ClienteTecnicoFalso(
        resultado_comentario=DetalheChamadoTecnico(
            chamado=detalhe_tecnico(status="Encerrado", ultima_atualizacao_em=1780000003000),
            timeline=[comentario],
            tecnicos=[ReferenciaUsuario(id=9, nome="Técnico 9")],
        )
    )
    monkeypatch.setattr(chamados_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado_tecnico()
    estado._atualizar_detalhe(
        DetalheChamadoTecnico(
            chamado=detalhe_tecnico(status="Encerrado"),
            timeline=[],
            tecnicos=[ReferenciaUsuario(id=9, nome="Técnico 9")],
        )
    )
    ChamadosTecnicoState.alterar_comentario_status_pendente.fn(
        estado, "Atualização em chamado encerrado."
    )
    ChamadosTecnicoState.alterar_visibilidade_comentario_status_pendente.fn(
        estado, "interna"
    )

    executar_evento(ChamadosTecnicoState.salvar_tratativa, estado)

    assert cliente.comentarios == [
        (
            "token-de-teste",
            32,
            {"conteudo": "Atualização em chamado encerrado.", "visibilidade": "interna"},
        )
    ]
    assert estado.comentario_status_pendente == ""
    assert estado.ultima_atualizacao_confirmada == 1780000003000
    assert estado.timeline[0]["conteudo"] == "Atualização em chamado encerrado."
    assert estado.mensagem_sucesso_tratativa == "Comentário adicionado."
