"""Contrato estático de segurança das consultas genéricas de interações.

Os testes leem o XanoScript versionado e verificam autorização, ordem entre
autorização e leitura, entradas aceitas e filtros dos contratos funcionais.
Eles não executam o runtime Xano e não substituem os testes XanoScript nem os
testes HTTP integrados.
"""

import re
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
GRUPO = ROOT / "xano/api/apis_from_table_interacoes_chamado"
LISTA = GRUPO / "interacoes_chamado_GET.xs"
POR_ID = GRUPO / "interacoes_chamado/interacoes_chamado_id_GET.xs"
EXIGIR_PERFIL = ROOT / "xano/function/autorizacao/exigir_perfil.xs"
COMENTARIOS_GERENTE = ROOT / "xano/function/service_desk/listar_comentarios_publicos_gerente.xs"
GERENTE_AUTORIZADO = ROOT / "xano/function/service_desk/obter_chamado_gerente_autorizado.xs"


def fonte(caminho):
    return caminho.read_text(encoding="utf-8")


def stack(texto):
    inicio = texto.index("stack {")
    return texto[inicio:texto.index("\n  response =", inicio)]


def bloco_input(texto):
    inicio = texto.index("input {")
    return texto[inicio:texto.index("}", inicio) + 1]


def chamada_autorizacao(texto):
    inicio = texto.index('function.run "autorizacao/')
    return texto[inicio:texto.index("} as $usuario", inicio)]


@pytest.mark.parametrize("caminho", [LISTA, POR_ID], ids=["lista", "por_id"])
def test_perfis_operacionais_autorizados_e_gerente_negado_pela_sessao(caminho):
    autorizacao = chamada_autorizacao(fonte(caminho))
    assert 'function.run "autorizacao/exigir_perfil"' in autorizacao
    assert "usuarios_id: $auth.id" in autorizacao
    assert "tecnico: true" in autorizacao
    for perfil in ("tecnico", "diretoria", "administrador"):
        assert f"{perfil}: true" in autorizacao
    assert "gerente: true" not in autorizacao
    assert "$input" not in autorizacao


@pytest.mark.parametrize("caminho", [LISTA, POR_ID], ids=["lista", "por_id"])
def test_autorizacao_ocorre_antes_de_qualquer_leitura(caminho):
    corpo = stack(fonte(caminho))
    posicao_autorizacao = corpo.index('function.run "autorizacao/exigir_perfil"')
    leituras = [m.start() for m in re.finditer(r"\bdb\.(get|query|has)\b", corpo)]
    assert leituras
    assert all(posicao > posicao_autorizacao for posicao in leituras)


@pytest.mark.parametrize("caminho", [LISTA, POR_ID], ids=["lista", "por_id"])
def test_consulta_generica_nao_possui_caminho_para_gerente(caminho):
    corpo = stack(fonte(caminho))
    assert "gerente" not in corpo
    assert "lojas_id" not in corpo
    assert "exigir_escopo_loja" not in corpo


@pytest.mark.parametrize("caminho", [LISTA, POR_ID], ids=["lista", "por_id"])
def test_consulta_generica_nao_escreve(caminho):
    corpo = stack(fonte(caminho))
    assert not re.search(r"\bdb\.(add|edit|patch|del|bulk|transaction)\b", corpo)


def test_lista_nao_aceita_filtros_do_cliente():
    texto = fonte(LISTA)
    assert re.fullmatch(r"input \{\s*\}", bloco_input(texto))
    assert "$input" not in stack(texto)


def test_por_id_aceita_somente_identificador_validado():
    texto = fonte(POR_ID)
    entradas = [linha.strip() for linha in bloco_input(texto).splitlines()[1:-1] if linha.strip()]
    assert entradas == ["int interacoes_chamado_id? filters=min:1"]
    assert re.findall(r"\$input\.\w+", stack(texto)) == ["$input.interacoes_chamado_id"]


def test_tecnico_preserva_lista_completa_e_resposta_bruta():
    texto = fonte(LISTA)
    consulta = texto[texto.index("db.query interacoes_chamado {"):texto.index("} as $interacoes_chamado")]
    assert "where" not in consulta
    assert 'return = {type: "list"}' in consulta
    assert "response = $interacoes_chamado" in texto


def test_tecnico_preserva_detalhe_e_nao_encontrado():
    texto = fonte(POR_ID)
    corpo = stack(texto)
    assert corpo.index("db.get interacoes_chamado") < corpo.index("precondition ($interacoes_chamado != null)")
    assert 'error_type = "notfound"' in corpo
    assert "response = $interacoes_chamado" in texto


def test_falha_de_autorizacao_usa_gate_central_sem_conteudo():
    texto = fonte(EXIGIR_PERFIL)
    assert "precondition ($usuario.deve_trocar_senha != true)" in texto
    assert "precondition ($permitido)" in texto
    assert 'error = "Acesso não autorizado."' in texto
    assert '($usuario.role == "gerente" && $input.gerente)' in texto
    assert 'test "nega perfil nao previsto"' in texto


def test_contrato_funcional_entrega_somente_comentario_publico_da_propria_loja():
    comentarios = fonte(COMENTARIOS_GERENTE)
    assert 'function.run "service_desk/obter_chamado_gerente_autorizado"' in comentarios
    assert '$db.interacoes_chamado.visibilidade == "publica"' in comentarios
    assert '$db.interacoes_chamado.tipo_evento == "comentario"' in comentarios
    assert '$db.interacoes_chamado.mensagem != ""' in comentarios
    projecao = comentarios[comentarios.index("array.push $items"):]
    for campo_privado in ("visibilidade:", "alteracoes", "usuarios_id", "email", "role"):
        assert campo_privado not in projecao.split("response =")[0]

    # Escopo pela Loja histórica do Totem no instante do chamado (change
    # regularizar-loja-historica-totem): sem vínculo, nenhum Gerente é autorizado.
    escopo = re.sub(r"\s+", " ", fonte(GERENTE_AUTORIZADO))
    assert 'function.run "administracao/resolver_loja_totem_no_instante"' in escopo
    assert "instante : $registro.criado_em" in escopo
    assert "precondition ($historico.lojas_id != null && $historico.lojas_id == $usuario.lojas_id)" in escopo
    assert "$registro.ativo_lojas_id == $usuario.lojas_id" not in escopo


def test_nenhum_consumidor_depende_das_consultas_genericas():
    alvos = ("interacoes_chamado_GET", "interacoes_chamado_id_GET", "/interacoes_chamado")
    for pasta in ("app", "simulator", "fiscal"):
        for arquivo in (ROOT / pasta).rglob("*.py"):
            conteudo = arquivo.read_text(encoding="utf-8")
            assert not any(alvo in conteudo for alvo in alvos), arquivo
