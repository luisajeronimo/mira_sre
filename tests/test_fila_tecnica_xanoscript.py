"""Guardas para os trechos Xano que persistem responsável e timeline.

Estes testes não substituem a execução live: eles impedem a regressão do
comando que omitia valores nulos na liberação antes de chegar ao Xano.
"""

from pathlib import Path


ROOT = Path(__file__).parents[1]
ASSUMIR = (ROOT / "xano/function/service_desk/assumir_chamado_tecnico.xs").read_text(
    encoding="utf-8"
)
DETALHE = (ROOT / "xano/function/service_desk/obter_chamado_tecnico.xs").read_text(
    encoding="utf-8"
)
LISTAGEM = (ROOT / "xano/function/service_desk/listar_chamados_tecnico.xs").read_text(
    encoding="utf-8"
)


def test_liberacao_envia_nulos_explicitos_antes_do_evento_na_transacao():
    inicio_transacao = ASSUMIR.index("db.transaction {")
    inicio_liberacao = ASSUMIR.index('if ($tipo_evento == "liberacao")')
    fim_liberacao = ASSUMIR.index("else {", inicio_liberacao)
    bloco_liberacao = ASSUMIR[inicio_liberacao:fim_liberacao]
    evento = ASSUMIR.index("db.add interacoes_chamado", inicio_liberacao)

    assert inicio_transacao < inicio_liberacao < evento
    assert "db.patch chamados" in bloco_liberacao
    assert "tecnico_id: null" in bloco_liberacao
    assert "atribuido_em: null" in bloco_liberacao
    assert "ultima_atualizacao_em: $instante" in bloco_liberacao
    assert "precondition ($chamado_liberado != null" in bloco_liberacao
    assert 'tipo_evento: $tipo_evento' in ASSUMIR[evento:]
    assert "tecnico_anterior_id: $tecnico_anterior_id" in ASSUMIR[evento:]
    assert "tecnico_novo_id: $tecnico_novo_id" in ASSUMIR[evento:]


def test_timeline_combina_interacoes_e_ordena_instante_e_id_descendentes():
    assert "value = $interacoes|map:{" in DETALHE
    assert 'ordenacao: (($$.criado_em ?? $$.created_at)|to_text) ~ "-" ~ ($$.id|to_text)' in DETALHE
    assert 'value = ($eventos|sort:"ordenacao":"natural":true)|reverse' in DETALHE
    assert 'test "retorna timeline cronológica decrescente com legado"' in DETALHE
    assert "{id: 12, tipo: \"comentario\"" in DETALHE
    assert "{id: 14, tipo: \"reatribuicao\"" in DETALHE


def test_listagem_normaliza_timestamp_de_atribuicao_nulo_do_xano():
    assert "atribuido_em: ($$.atribuido_em != null && $$.atribuido_em != 0) ? $$.atribuido_em : null" in LISTAGEM
