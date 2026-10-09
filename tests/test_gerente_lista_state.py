"""State e apresentação da lista operacional do Gerente."""

from __future__ import annotations

import asyncio
import inspect

import pytest

import app.chamados.gerente.pages as paginas
import app.chamados.gerente.state as gerente_module
from app.chamados.gerente.state import ChamadosGerenteState
from app.services.service_desk import (
    AtivoServiceDesk,
    CategoriaServiceDesk,
    ChamadoDetalhe,
    ChamadoResumo,
    ListaChamadosGerente,
    ReferenciaAtivo,
    ReferenciaCategoria,
    ReferenciaUsuario,
)
from app.services.xano import (
    XanoContratoInvalido,
    XanoIndisponivel,
    XanoNaoAutenticado,
    XanoRateLimitado,
)
from app.states.auth import MENSAGEM_EXPIRADA, MENSAGEM_INDISPONIVEL


def executar_evento(handler, estado, *args):
    async def coletar():
        return [evento async for evento in handler.fn(estado, *args)]

    return asyncio.run(coletar())


def resumo(*, descricao="Descrição", criado_em=100, ultima_atualizacao_em=100):
    return ChamadoResumo(
        id=7,
        titulo="Falha operacional",
        descricao=descricao,
        status="Novo",
        prioridade="Alta",
        origem="manual",
        criado_em=criado_em,
        ultima_atualizacao_em=ultima_atualizacao_em,
        ativo=ReferenciaAtivo(id=1, nome_ativo="Totem 01"),
        categoria=ReferenciaCategoria(id=2, nome="Rede"),
    )


def detalhe():
    return ChamadoDetalhe(
        id=7,
        titulo="Falha operacional",
        descricao="Descrição",
        status="Novo",
        prioridade="Alta",
        origem="manual",
        criado_em=100,
        ultima_atualizacao_em=100,
        sla_horas_aplicado=2,
        ativo=ReferenciaAtivo(id=1, nome_ativo="Totem 01"),
        categoria=ReferenciaCategoria(id=2, nome="Rede"),
        solicitante=ReferenciaUsuario(id=8, nome="Gerente"),
        tecnico=None,
    )


class ClienteListaFalso:
    def __init__(self):
        self.consultas = []
        self.consultas_ativos = 0
        self.criacoes = []

    async def listar_chamados(self, token, **kwargs):
        self.consultas.append((token, kwargs))
        return ListaChamadosGerente(items=[resumo()], total=1)

    async def listar_ativos(self, token):
        self.consultas_ativos += 1
        return [AtivoServiceDesk(1, "Totem 01", "Totem", "online")]

    async def listar_categorias(self, token):
        return [CategoriaServiceDesk(2, "Rede", "Incidente", "Falha", 2)]

    async def abrir_chamado(self, token, **kwargs):
        self.criacoes.append((token, kwargs))
        return detalhe()


class ClienteListaComFalha(ClienteListaFalso):
    def __init__(self, erro):
        super().__init__()
        self.erro = erro

    async def listar_chamados(self, token, **kwargs):
        self.consultas.append((token, kwargs))
        raise self.erro


def novo_estado():
    estado = ChamadosGerenteState(_reflex_internal_init=True)
    object.__setattr__(estado, "_auth_token", "token-de-teste")
    object.__setattr__(estado, "sessao_confirmada", True)
    object.__setattr__(estado, "usuario_id", 8)
    object.__setattr__(estado, "role", "gerente")
    return estado


def liberar_validacao(monkeypatch):
    async def validar(_estado):
        return None

    monkeypatch.setattr(ChamadosGerenteState, "_validar_gerente", validar)


def test_lista_aplica_consulta_server_side_e_mantem_total(monkeypatch):
    liberar_validacao(monkeypatch)
    cliente = ClienteListaFalso()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()
    estado.filtro_numero = "7"
    estado.filtro_status = "Novo"
    estado.filtro_ativo = "1 — Totem 01"
    estado.filtro_data_inicio = "2026-10-01"
    estado.filtro_data_fim = "2026-10-02"

    executar_evento(ChamadosGerenteState.aplicar_filtros, estado)

    assert estado.total_chamados == 1
    assert len(estado.chamados) == 1
    assert estado.filtros_aplicados == [
        "Número: 7",
        "Status: Novo",
        "Totem: Totem 01",
        "Abertura a partir de: 2026-10-01",
        "Abertura até: 2026-10-02",
    ]
    _, consulta = cliente.consultas[-1]
    assert consulta["numero"] == 7
    assert consulta["status"] == "Novo"
    assert consulta["ativo_id"] == 1
    assert consulta["data_inicio"] < consulta["data_fim"]
    assert consulta["ordenar_por"] == "criado_em"
    assert consulta["direcao"] == "DESC"


def test_limpar_preserva_ordenacao_e_reconsulta(monkeypatch):
    liberar_validacao(monkeypatch)
    cliente = ClienteListaFalso()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()
    estado.ordenar_por = "prioridade"
    estado.direcao = "ASC"
    estado.filtro_status = "Novo"
    estado.status_aplicado = "Novo"
    estado.filtros_aplicados = ["Status: Novo"]

    executar_evento(ChamadosGerenteState.limpar_filtros_lista, estado)

    assert estado.filtros_aplicados == []
    assert estado.filtro_status == ""
    assert estado.ordenar_por == "prioridade"
    assert estado.direcao == "ASC"
    assert cliente.consultas[-1][1]["status"] is None


def test_ordenacao_nao_reordena_items_localmente(monkeypatch):
    liberar_validacao(monkeypatch)
    cliente = ClienteListaFalso()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()

    executar_evento(ChamadosGerenteState.alternar_ordenacao, estado, "status")

    assert estado.ordenar_por == "status"
    assert estado.direcao == "ASC"
    assert cliente.consultas[-1][1]["ordenar_por"] == "status"
    assert cliente.consultas[-1][1]["direcao"] == "ASC"


def test_sessao_confirmada_sobrevive_a_ordenacoes_repetidas(monkeypatch):
    cliente = ClienteListaFalso()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()
    validacoes = 0

    async def validar(_estado):
        nonlocal validacoes
        validacoes += 1
        return None

    monkeypatch.setattr(ChamadosGerenteState, "_validar_gerente", validar)

    for _ in range(4):
        executar_evento(ChamadosGerenteState.alternar_ordenacao, estado, "status")

    assert len(cliente.consultas) == 4
    assert validacoes == 0
    assert estado._auth_token == "token-de-teste"
    assert estado.sessao_confirmada is True
    assert estado.mensagem_chamados == ""
    assert cliente.consultas_ativos == 1


def test_sessao_confirmada_sobrevive_a_filtros_e_limpezas_repetidos(monkeypatch):
    cliente = ClienteListaFalso()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()

    for _ in range(2):
        estado.filtro_status = "Novo"
        executar_evento(ChamadosGerenteState.aplicar_filtros, estado)
        executar_evento(ChamadosGerenteState.limpar_filtros_lista, estado)

    assert len(cliente.consultas) == 4
    assert estado._auth_token == "token-de-teste"
    assert estado.sessao_confirmada is True
    assert estado.filtros_aplicados == []


@pytest.mark.parametrize(
    "erro",
    [
        XanoIndisponivel("timeout"),
        XanoRateLimitado(retry_after_segundos=2),
        XanoContratoInvalido("shape"),
    ],
)
def test_erro_de_lista_nao_invalida_sessao_confirmada(monkeypatch, erro):
    cliente = ClienteListaComFalha(erro)
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()

    eventos = executar_evento(ChamadosGerenteState.carregar_lista, estado)

    assert eventos == [None]
    assert estado._auth_token == "token-de-teste"
    assert estado.sessao_confirmada is True
    assert estado.mensagem_chamados == MENSAGEM_INDISPONIVEL


def test_falha_de_autenticacao_real_continua_limpando_sessao(monkeypatch):
    cliente = ClienteListaComFalha(XanoNaoAutenticado("expirada"))
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()
    limpezas = []

    def limpar_sessao(_estado, mensagem):
        limpezas.append(mensagem)

    monkeypatch.setattr(ChamadosGerenteState, "_limpar_sessao", limpar_sessao)

    eventos = executar_evento(ChamadosGerenteState.carregar_lista, estado)

    assert limpezas == [MENSAGEM_EXPIRADA]
    assert eventos[-1].args[0][1]._var_value == "/login"


def test_consulta_concorrente_e_ignorada_sem_sobrescrever_estado(monkeypatch):
    cliente = ClienteListaFalso()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()
    estado.chamados = [{"id": 99, "titulo": "Atual"}]
    estado.total_chamados = 1
    estado.carregando_chamados = True

    eventos = executar_evento(ChamadosGerenteState.carregar_lista, estado)

    assert eventos == []
    assert estado.chamados == [{"id": 99, "titulo": "Atual"}]
    assert estado.total_chamados == 1
    assert cliente.consultas == []


def test_falha_transitoria_permite_nova_consulta_e_limpa_erro(monkeypatch):
    class ClienteRecuperavel(ClienteListaFalso):
        def __init__(self):
            super().__init__()
            self.falhar = True

        async def listar_chamados(self, token, **kwargs):
            self.consultas.append((token, kwargs))
            if self.falhar:
                self.falhar = False
                raise XanoIndisponivel("temporário")
            return ListaChamadosGerente(items=[resumo()], total=1)

    cliente = ClienteRecuperavel()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()

    executar_evento(ChamadosGerenteState.carregar_lista, estado)
    assert estado.carregando_chamados is False
    assert estado.sessao_confirmada is True
    assert estado.mensagem_chamados == MENSAGEM_INDISPONIVEL

    executar_evento(ChamadosGerenteState.carregar_lista, estado)
    assert estado.carregando_chamados is False
    assert estado.mensagem_chamados == ""
    assert estado.total_chamados == 1
    assert len(cliente.consultas) == 2


def test_falha_do_catalogo_secundario_preserva_lista(monkeypatch):
    class ClienteCatalogoIndisponivel(ClienteListaFalso):
        async def listar_ativos(self, token):
            self.consultas_ativos += 1
            raise XanoRateLimitado(retry_after_segundos=1)

    cliente = ClienteCatalogoIndisponivel()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()

    executar_evento(ChamadosGerenteState.carregar_lista, estado)

    assert len(estado.chamados) == 1
    assert estado.total_chamados == 1
    assert estado.sessao_confirmada is True
    assert estado.mensagem_chamados == MENSAGEM_INDISPONIVEL
    assert estado.carregando_chamados is False


def test_falha_de_autenticacao_no_catalogo_secundario_redireciona(monkeypatch):
    class ClienteCatalogoExpirado(ClienteListaFalso):
        async def listar_ativos(self, token):
            self.consultas_ativos += 1
            raise XanoNaoAutenticado("expirada")

    cliente = ClienteCatalogoExpirado()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()
    estado.ativos = []
    def limpar_sessao(_estado, _mensagem):
        object.__setattr__(_estado, "sessao_confirmada", False)
        object.__setattr__(_estado, "_auth_token", "")
    monkeypatch.setattr(ChamadosGerenteState, "_limpar_sessao", limpar_sessao)

    eventos = executar_evento(ChamadosGerenteState.carregar_lista, estado)

    assert eventos[-1].args[0][1]._var_value == "/login"
    assert estado.sessao_confirmada is False
    assert estado.carregando_chamados is False


def test_intencoes_concorrentes_coalescem_em_uma_nova_consulta(monkeypatch):
    class ClienteLento(ClienteListaFalso):
        def __init__(self):
            super().__init__()
            self.iniciada = asyncio.Event()
            self.liberar = asyncio.Event()

        async def listar_chamados(self, token, **kwargs):
            self.consultas.append((token, kwargs))
            self.iniciada.set()
            await self.liberar.wait()
            return ListaChamadosGerente(items=[resumo()], total=1)

    cliente = ClienteLento()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()

    async def executar_concorrencia():
        primeira = ChamadosGerenteState.carregar_lista.fn(estado)
        assert await primeira.__anext__() is None
        tarefa = asyncio.create_task(primeira.__anext__())
        await cliente.iniciada.wait()

        segunda = ChamadosGerenteState.carregar_lista.fn(estado)
        assert [evento async for evento in segunda] == []
        assert estado.consulta_chamados_pendente is True

        cliente.liberar.set()
        with pytest.raises(StopAsyncIteration):
            await tarefa
        assert len(cliente.consultas) == 2
        assert estado.carregando_chamados is False

    asyncio.run(executar_concorrencia())


def test_limpar_e_descartar_formulario_nao_chamam_backend(monkeypatch):
    cliente = ClienteListaFalso()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()
    estado.ativo_formulario = "1 — Totem 01"
    estado.categoria_formulario = "2 — Rede"
    estado.prioridade_formulario = "Alta"
    estado.titulo_formulario = "Título"
    estado.descricao_formulario = "Descrição"

    ChamadosGerenteState.limpar_formulario.fn(estado)
    assert estado.titulo_formulario == ""
    assert estado.descricao_formulario == ""
    assert cliente.criacoes == []

    estado.titulo_formulario = "Rascunho"
    ChamadosGerenteState.descartar_formulario.fn(estado)
    assert estado.titulo_formulario == ""
    assert cliente.criacoes == []


def test_salvar_mantem_payload_funcional_e_emite_feedback_observavel(monkeypatch):
    cliente = ClienteListaFalso()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()
    estado.ativo_formulario = "1 — Totem 01"
    estado.categoria_formulario = "2 — Rede"
    estado.prioridade_formulario = "Alta"
    estado.titulo_formulario = "Título"
    estado.descricao_formulario = "Descrição"

    eventos = executar_evento(ChamadosGerenteState.abrir_chamado, estado)

    assert cliente.criacoes == [
        (
            "token-de-teste",
            {
                "ativos_referencia_id": 1,
                "categorias_servico_id": 2,
                "prioridade": "Alta",
                "titulo": "Título",
                "descricao": "Descrição",
            },
        )
    ]
    assert len(eventos) >= 3  # loading, toast de sucesso e redirecionamento
    assert estado.titulo_formulario == ""


def test_selecao_de_ativo_e_categoria_atualiza_state_e_payload(monkeypatch):
    cliente = ClienteListaFalso()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()

    ChamadosGerenteState.alterar_ativo_formulario.fn(estado, "1")
    ChamadosGerenteState.alterar_categoria_formulario.fn(estado, "2")
    estado.prioridade_formulario = "Alta"
    estado.titulo_formulario = "Título"
    estado.descricao_formulario = "Descrição"

    executar_evento(ChamadosGerenteState.abrir_chamado, estado)

    assert estado.mensagem_formulario == ""
    assert cliente.criacoes[-1][1]["ativos_referencia_id"] == 1
    assert cliente.criacoes[-1][1]["categorias_servico_id"] == 2


@pytest.mark.parametrize(
    ("ativo", "categoria"),
    [("1", ""), ("", "2"), ("", "")],
)
def test_selecao_incompleta_mantem_erro_de_formulario(monkeypatch, ativo, categoria):
    cliente = ClienteListaFalso()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()
    estado.ativo_formulario = ativo
    estado.categoria_formulario = categoria

    executar_evento(ChamadosGerenteState.abrir_chamado, estado)

    assert estado.mensagem_formulario == "Selecione um ativo e uma categoria."
    assert cliente.criacoes == []


def test_formulario_exibe_nome_e_transporta_id_nos_selects():
    formulario = inspect.getsource(paginas._formulario)

    assert "ativos_formulario" in formulario
    assert "categorias_formulario" in formulario
    assert 'ativo["id"].to_string()' in formulario
    assert 'categoria["id"].to_string()' in formulario


def test_tabela_e_formulario_implementam_somente_as_acoes_aprovadas():
    lista = inspect.getsource(paginas._lista)
    formulario = inspect.getsource(paginas._formulario)

    for coluna in (
        "Número",
        "Título + ocorrência",
        "Status",
        "Prioridade",
        "Totem",
        "Categoria",
        "Data de abertura",
        "Data da última atualização",
    ):
        assert coluna in lista
    assert "rx.table.root" in lista
    assert "Limpar filtros" in lista
    assert "filtros_aplicados" in lista
    assert "Limpar" in formulario
    assert "Descartar" in formulario
    assert "Voltar para lista de chamados" in formulario
    assert "rx.toast.success" in inspect.getsource(ChamadosGerenteState.abrir_chamado.fn)


def test_salvar_ignora_payload_de_clique_do_mouse_e_consome_state(monkeypatch):
    """Garante que dados de evento DOM (mouse click) não anulem a seleção do State."""
    cliente = ClienteListaFalso()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()
    estado.ativo_formulario = "1"
    estado.categoria_formulario = "2"
    estado.prioridade_formulario = "Alta"
    estado.titulo_formulario = "Título do Chamado"
    estado.descricao_formulario = "Descrição do Chamado"

    payload_clique_mouse = {
        "button": 0,
        "buttons": 0,
        "client_x": 150,
        "client_y": 320,
        "alt_key": False,
        "ctrl_key": False,
        "meta_key": False,
        "shift_key": False,
    }

    eventos = executar_evento(ChamadosGerenteState.abrir_chamado, estado, payload_clique_mouse)

    assert estado.mensagem_formulario == ""
    assert len(cliente.criacoes) == 1
    assert cliente.criacoes[0][1]["ativos_referencia_id"] == 1
    assert cliente.criacoes[0][1]["categorias_servico_id"] == 2
    assert cliente.criacoes[0][1]["prioridade"] == "Alta"
    assert any("Chamado aberto com sucesso" in str(getattr(ev, "args", "")) for ev in eventos if ev is not None)


def test_fluxo_completo_select_evento_clique_e_payload(monkeypatch):
    """Verifica a cadeia: seleção de opção nos componentes -> State -> clique com payload DOM -> criação."""
    cliente = ClienteListaFalso()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()

    # 1. Simula os eventos emitidos pelos selects ao escolher option "1" e "2"
    ChamadosGerenteState.alterar_ativo_formulario.fn(estado, "1")
    ChamadosGerenteState.alterar_categoria_formulario.fn(estado, "2")
    ChamadosGerenteState.alterar_prioridade_formulario.fn(estado, "Alta")
    ChamadosGerenteState.alterar_titulo_formulario.fn(estado, "Totem travado")
    ChamadosGerenteState.alterar_descricao_formulario.fn(estado, "Reinício falhou")

    assert estado.ativo_formulario == "1"
    assert estado.categoria_formulario == "2"

    # 2. Simula o evento de clique do botão Salvar recebido do navegador
    evento_clique = {"button": 0, "clientX": 200, "clientY": 400}
    executar_evento(ChamadosGerenteState.abrir_chamado, estado, evento_clique)

    assert estado.mensagem_formulario == ""
    assert cliente.criacoes[-1][1]["ativos_referencia_id"] == 1
    assert cliente.criacoes[-1][1]["categorias_servico_id"] == 2
    assert cliente.criacoes[-1][1]["titulo"] == "Totem travado"

