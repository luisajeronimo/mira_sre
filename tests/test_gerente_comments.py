"""Contratos locais de comentários públicos e atualização observável."""

import asyncio
from pathlib import Path

import httpx
import pytest

import app.chamados.gerente.pages as paginas
import app.chamados.gerente.state as gerente_module
from app.chamados.gerente.state import ChamadosGerenteState
from app.services.service_desk import (
    AutorComentarioPublico,
    ChamadoDetalhe,
    ComentarioPublico,
    ReferenciaAtivo,
    ReferenciaCategoria,
    ReferenciaUsuario,
    XanoServiceDeskCliente,
)
from app.services.xano import XanoContratoInvalido, XanoEntradaInvalida, XanoNaoEncontrado


BASE_URL = "https://xano.example/api:mira-service-desk"
ROOT = Path(__file__).parents[1]


def executar(corrotina):
    return asyncio.run(corrotina)


def detalhe(*, ultima_atualizacao_em=1780000000000, status="Novo"):
    return ChamadoDetalhe(
        id=101,
        titulo="Falha observada",
        descricao="Totem não conecta",
        status=status,
        prioridade="Alta",
        origem="manual",
        criado_em=1780000000000,
        sla_horas_aplicado=2,
        ativo=ReferenciaAtivo(id=1, nome_ativo="Totem 01"),
        categoria=ReferenciaCategoria(id=2, nome="Falha de Rede"),
        solicitante=ReferenciaUsuario(id=8, nome="Gerente"),
        tecnico=None,
        ultima_atualizacao_em=ultima_atualizacao_em,
    )


def comentario_payload(*, autor={"nome": "Gerente"}, **alteracoes):
    dados = {
        "id": 12,
        "conteudo": "Comentário público",
        "criado_em": 1780000002000,
        "autor": autor,
    }
    dados.update(alteracoes)
    return dados


def novo_estado():
    estado = ChamadosGerenteState(_reflex_internal_init=True)
    object.__setattr__(estado, "_auth_token", "token-de-teste")
    object.__setattr__(estado, "sessao_confirmada", True)
    object.__setattr__(estado, "usuario_id", 8)
    object.__setattr__(estado, "role", "gerente")
    object.__setattr__(estado, "chamado_id", "101")
    return estado


def liberar_validacao(monkeypatch):
    async def validar(_estado):
        return None

    monkeypatch.setattr(ChamadosGerenteState, "_validar_gerente", validar)


def executar_evento(handler, estado):
    async def coletar():
        return [evento async for evento in handler.fn(estado)]

    return asyncio.run(coletar())


def test_cliente_usa_contratos_especificos_e_payload_minimo():
    requisicoes = []

    def responder(requisicao: httpx.Request) -> httpx.Response:
        requisicoes.append(requisicao)
        if requisicao.method == "POST":
            return httpx.Response(201, json={"comentario": comentario_payload()})
        return httpx.Response(
            200,
            json={"items": [comentario_payload(), comentario_payload(id=11, autor=None)]},
        )

    cliente = XanoServiceDeskCliente(BASE_URL, transport=httpx.MockTransport(responder))
    comentarios = executar(cliente.listar_comentarios_publicos("token", 101))
    criado = executar(cliente.criar_comentario_publico("token", 101, conteudo="Texto"))

    assert comentarios[0].autor == AutorComentarioPublico(nome="Gerente")
    assert comentarios[1].autor is None
    assert criado.conteudo == "Comentário público"
    assert [str(item.url) for item in requisicoes] == [
        f"{BASE_URL}/gerente/chamados/101/comentarios",
        f"{BASE_URL}/gerente/chamados/101/comentarios",
    ]
    assert requisicoes[0].method == "GET"
    assert requisicoes[1].method == "POST"
    assert requisicoes[1].read() == b'{"conteudo":"Texto"}'


@pytest.mark.parametrize(
    "payload",
    [
        comentario_payload(autor={"nome": "Gerente", "email": "vaza@example.test"}),
        comentario_payload(autor={"id": 8, "nome": "Gerente"}),
        comentario_payload(extra="não permitido"),
        comentario_payload(autor={"nome": ""}),
    ],
)
def test_dto_comentario_falha_fechado_para_campos_nao_publicos(payload):
    cliente = XanoServiceDeskCliente(
        BASE_URL,
        transport=httpx.MockTransport(lambda _: httpx.Response(200, json={"items": [payload]})),
    )

    with pytest.raises(XanoContratoInvalido):
        executar(cliente.listar_comentarios_publicos("token", 101))


class ClienteComentariosFalso:
    def __init__(self, *, status="Novo", erro=None):
        self.status = status
        self.erro = erro
        self.criacoes = []

    async def obter_chamado(self, token, chamado_id):
        return detalhe(ultima_atualizacao_em=1780000002000, status=self.status)

    async def listar_comentarios_publicos(self, token, chamado_id):
        return [
            ComentarioPublico(
                id=11,
                conteudo="Anterior",
                criado_em=1780000001000,
                autor=None,
            )
        ]

    async def criar_comentario_publico(self, token, chamado_id, *, conteudo):
        self.criacoes.append((token, chamado_id, conteudo))
        if self.erro is not None:
            raise self.erro
        return ComentarioPublico(
            id=12,
            conteudo=conteudo.strip(),
            criado_em=1780000002000,
            autor=AutorComentarioPublico(nome="Gerente"),
        )


def test_detalhe_carrega_campos_e_comentarios_publicos(monkeypatch):
    liberar_validacao(monkeypatch)
    cliente = ClienteComentariosFalso()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()

    executar_evento(ChamadosGerenteState.carregar_detalhe, estado)

    assert estado.chamado["ativo_nome"] == "Totem 01"
    assert estado.chamado["categoria_nome"] == "Falha de Rede"
    assert estado.chamado["tecnico_nome"] == "Não atribuído"
    assert estado.chamado["ultima_atualizacao_em_texto"] != "Não informado"
    assert estado.comentarios[0]["autor_nome"] == "Não informado"


def test_ultima_atualizacao_legada_e_apresentada_sem_inferencia():
    from app.chamados.shared import _detalhe_para_dict

    assert _detalhe_para_dict(detalhe(ultima_atualizacao_em=None))["ultima_atualizacao_em_texto"] == "Não informado"


def test_postagem_atualiza_state_com_dto_servidor_e_descarta_rascunho(monkeypatch):
    liberar_validacao(monkeypatch)
    cliente = ClienteComentariosFalso()
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()
    estado.rascunho_comentario = " Novo comentário "

    executar_evento(ChamadosGerenteState.publicar_comentario, estado)

    assert cliente.criacoes == [("token-de-teste", 101, " Novo comentário ")]
    assert estado.rascunho_comentario == ""
    assert estado.comentarios[0]["conteudo"] == "Novo comentário"
    assert estado.chamado["ultima_atualizacao_em_texto"] != "Não informado"


def test_erro_de_comentario_e_sanitizado_sem_limpar_rascunho(monkeypatch):
    liberar_validacao(monkeypatch)
    cliente = ClienteComentariosFalso(erro=XanoEntradaInvalida("interno"))
    monkeypatch.setattr(gerente_module, "criar_cliente_service_desk", lambda: cliente)
    estado = novo_estado()
    estado.rascunho_comentario = "   "

    executar_evento(ChamadosGerenteState.publicar_comentario, estado)

    assert estado.rascunho_comentario == "   "
    assert estado.mensagem_comentarios == "Os dados informados são inválidos."


def test_troca_de_rota_com_erro_limpa_detalhe_e_comentarios_residuais(monkeypatch):
    liberar_validacao(monkeypatch)

    class ClienteQueFalhaNoDetalhe(ClienteComentariosFalso):
        async def obter_chamado(self, token, chamado_id):
            raise XanoNaoEncontrado("interno")

    monkeypatch.setattr(
        gerente_module,
        "criar_cliente_service_desk",
        lambda: ClienteQueFalhaNoDetalhe(),
    )
    estado = novo_estado()
    estado.chamado = {"id": 99, "status": "Encerrado"}
    estado.comentarios = [{"id": 1, "conteudo": "antigo", "criado_em_texto": "x", "autor_nome": "A"}]
    estado.rascunho_comentario = "antigo"
    estado.detalhe_carregado = True

    executar_evento(ChamadosGerenteState.carregar_detalhe, estado)

    assert estado.chamado == {}
    assert estado.comentarios == []
    assert estado.rascunho_comentario == ""
    assert estado.detalhe_carregado is False
    assert estado.mensagem_detalhe == "Chamado não encontrado."


def test_descarte_do_rascunho_e_exclusivamente_local():
    estado = novo_estado()
    estado.rascunho_comentario = "rascunho"

    ChamadosGerenteState.descartar_rascunho_comentario.fn(estado)

    assert estado.rascunho_comentario == ""


def test_terminal_oculta_postagem_mas_mantem_leitura_planejada():
    fonte = Path(paginas.__file__).read_text()

    assert 'ChamadosGerenteState.chamado["status"] != "Encerrado"' in fonte
    assert 'ChamadosGerenteState.chamado["status"] != "Cancelado"' in fonte
    assert 'rx.heading("Comentários"' in fonte
    assert fonte.count("ChamadosGerenteState.detalhe_carregado") >= 2


def test_xanoscript_preserva_timestamps_e_visibilidade_fechada():
    chamados = (ROOT / "xano/table/chamados.xs").read_text()
    interacoes = (ROOT / "xano/table/interacoes_chamado.xs").read_text()
    manual = (ROOT / "xano/function/service_desk/abrir_chamado_manual.xs").read_text()
    assumir = (ROOT / "xano/function/service_desk/assumir_chamado_tecnico.xs").read_text()
    heartbeat = (ROOT / "xano/api/apis_from_table_telemetria_equipamentos/verificar_falhas_GET.xs").read_text()
    listar = (ROOT / "xano/function/service_desk/listar_comentarios_publicos_gerente.xs").read_text()
    criar = (ROOT / "xano/function/service_desk/criar_comentario_publico_gerente.xs").read_text()

    assert "timestamp? ultima_atualizacao_em?" in chamados
    assert 'values = ["publica", "interna"]' in interacoes
    assert "ultima_atualizacao_em: $criado_em" in manual
    assert "ultima_atualizacao_em: $atribuido_em" in assumir
    assert "ultima_atualizacao_em: $criado_em" in heartbeat
    assert '$db.interacoes_chamado.visibilidade == "publica"' in listar
    assert 'sort = {interacoes_chamado.criado_em: "desc"}' in listar
    assert "db.transaction" in criar
    assert 'visibilidade: "publica"' in criar
    assert "ultima_atualizacao_em: $criado_em" in criar
