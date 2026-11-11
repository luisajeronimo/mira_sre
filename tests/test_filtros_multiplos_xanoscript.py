"""Guardas estáticas dos arquivos locais; não executam o runtime Xano."""
from pathlib import Path
import re
import pytest

ROOT = Path(__file__).parents[1] / "xano/function/service_desk"


def fonte(nome):
    return (ROOT / f"{nome}.xs").read_text(encoding="utf-8")


@pytest.mark.parametrize("sufixo", ["fila_tecnica", "filtros_gerente"])
def test_fallback_exclusivo_de_null_e_snapshot_neutraliza_legado(sufixo):
    obter = fonte(f"obter_preferencia_{sufixo}")
    salvar = fonte(f"salvar_preferencia_{sufixo}")
    assert 'if ($salva != null && $salva.filtros_multiplos == null)' in obter
    assert 'elseif ($salva != null && $salva.filtros_multiplos != null)' in obter
    assert 'value = $salva.filtros_multiplos' in obter
    assert 'Preferência persistida inválida.' in obter
    assert '$multiplos|is_object' in obter
    for campo in ('status', 'ativo_ids', 'loja_ids', 'prioridades', 'responsavel_ids'):
        assert f'$multiplos.{campo}|is_array' in obter
        assert f'{campo}:' in salvar
    assert '$multiplos.incluir_nao_atribuido|is_bool' in obter
    upsert = salvar.split('db.add_or_edit preferencias_fila_chamados', 1)[1]
    for campo in ('status', 'ativos_referencia_id', 'lojas_id', 'prioridade', 'responsavel_id'):
        assert f'{campo}: null' in upsert
    assert 'somente_nao_atribuido: false' in upsert
    assert 'filtros_multiplos: $multiplos' in upsert
    assert 'usuarios_id: $usuario.id' in upsert
    assert 'field_value = $chave_logica' in upsert


def test_colecoes_or_alimentam_sequencialmente_intersecao_and():
    lista = fonte('listar_chamados_tecnico')
    bloco = lista[lista.index('var $chamados_filtrados'):lista.index('var $items')]
    for colecao, campo in (('status_normalizados', 'status'), ('ativo_ids', 'ativo_id'), ('prioridades', 'prioridade'), ('loja_ids', 'loja_id')):
        assert f'array.filter ($chamados_filtrados) if (${colecao}|in:$this.{campo})' in bloco
    # O publicado testa `$input.incluir_nao_atribuido` (bool?) diretamente; equivale a `== true`.
    assert re.search(r'\(\$responsavel_ids\|in:\$this\.tecnico_id\) \|\| \(\$input\.incluir_nao_atribuido( == true)? &&', bloco)
    filtros = re.findall(r'array.filter \(\$chamados_filtrados\).*?as \$resultado_filtrado\s+var.update \$chamados_filtrados', bloco)
    assert len(filtros) == 7
    assert 'sort =' not in bloco


def test_eventos_novos_omitem_visibilidade_e_publico_exige_comentario():
    assumir = fonte('assumir_chamado_tecnico')
    evento = assumir.split('db.add interacoes_chamado', 1)[1].split('mock =', 1)[0]
    assert 'tipo_evento: $tipo_evento' in evento
    assert 'visibilidade' not in evento
    save = fonte('validar_save_tratativa_chamado')
    assert 'tipo_evento: "comentario"' in save
    assert 'visibilidade: $input.visibilidade_comentario_status' in save
    operacional = save.split('data = {tipo_evento: "alteracao_chamado"', 1)[1].split('mock =', 1)[0]
    assert 'visibilidade' not in operacional
    assert '? $$.visibilidade : null' in fonte('obter_chamado_tecnico')
    publico = fonte('listar_comentarios_publicos_gerente')
    assert '$db.interacoes_chamado.tipo_evento == "comentario"' in publico
    assert '$db.interacoes_chamado.visibilidade == "publica"' in publico
    assert 'obter_chamado_gerente_autorizado' in publico
