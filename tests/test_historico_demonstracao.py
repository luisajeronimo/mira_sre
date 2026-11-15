"""Plano fictício restrito aos Totens já existentes, sem escrita de cadastro."""
import copy
import json
from pathlib import Path
import re
import subprocess

import pytest



FONTE = Path('xano/function/demonstracao/planejar_confiabilidade.xs')


def gerar(variaveis=None, data='2026-11-14'):
    var = {'agora': 1794708000000, 'ocupacao': 4000,
           'ativos': [{'id': i, 'nome_ativo': f'TOT-PAU-00{i}', 'lojas_id': 1, 'tipo': 'Totem'} for i in (1, 2)],
           'telemetrias': [], 'eventos': [{'id': i, 'ativos_referencia_id': i, 'status': 'online', 'detectado_em': 1791169200000} for i in (1, 2)]}
    var.update(variaveis or {})
    fonte = FONTE.read_text().split('code = """', 1)[1].split('"""', 1)[0]
    js = 'const $input=' + json.dumps({'data_base': data}) + ';const $var=' + json.dumps(var) + ';console.log(JSON.stringify((()=>{' + fonte + '})()));'
    r = subprocess.run(['node', '-e', js], capture_output=True, text=True)
    if r.returncode:
        raise ValueError(r.stderr)
    return json.loads(r.stdout)


def test_plano_real_tem_242_fatos_60_pares_e_cadencia():
    previa = gerar()
    plano = previa['plano']
    assert [a['id'] for a in plano['ativos']] == [1, 2]
    assert plano['contagens'] == {'telemetrias': 122, 'transicoes': 120, 'total': 242}
    assert previa['faltantes'] == 242
    assert len(plano['etapas']) == 62
    for e in plano['etapas']:
        if e['indice'] < 0:
            continue
        last, rec = (a['evento_timestamp'] for a in e['amostras'])
        off, on = (v['detectado_em'] for v in e['eventos'])
        assert last < off < rec <= on < plano['t1']
        assert 16 <= (off-last)/60000 <= 20
        assert 30 <= (rec-last)/60000 <= 180
        assert off % 300000 == on % 300000 == 0
        assert on-rec < 300000


@pytest.mark.parametrize('mudanca', ['data', 'capacidade', 'cadastro', 'ocupada', 'duplicidade', 'conteudo'])
def test_plano_real_rejeita_conflitos(mudanca):
    var = {}
    data = '2026-11-14'
    a = copy.deepcopy(gerar()['plano']['etapas'][1]['amostras'][0])
    if mudanca == 'data':
        data = '2026-11-15'
    elif mudanca == 'capacidade':
        var['ocupacao'] = 99999
    elif mudanca == 'cadastro':
        var['ativos'] = []
    elif mudanca == 'ocupada':
        var['telemetrias'] = [{**a, 'id': 99, 'evento_timestamp': a['evento_timestamp']+60000}]
    elif mudanca == 'duplicidade':
        var['telemetrias'] = [{**a, 'id': 99}, {**a, 'id': 100}]
    else:
        var['telemetrias'] = [{**a, 'id': 99, 'uso_cpu': 99}]
    with pytest.raises(ValueError):
        gerar(var, data)


def test_plano_reutiliza_fatos_exatos_sem_contar_como_conflito():
    a = gerar()['plano']['etapas'][1]['amostras'][0]
    p = gerar({'telemetrias': [{**a, 'id': 99}]})
    assert p['existentes'] == 1 and p['faltantes'] == 241


def test_namespace_nao_cria_cadastro_nem_edita_qualquer_registro():
    for p in FONTE.parent.glob('*.xs'):
        s = p.read_text()
        assert not re.search(r'db\.(?:edit|patch|del|truncate|add_or_edit)\b', s), p
        assert set(re.findall(r'db\.add\s+(\w+)', s)) <= {'telemetria_equipamentos', 'historico_disponibilidade_totens'}
