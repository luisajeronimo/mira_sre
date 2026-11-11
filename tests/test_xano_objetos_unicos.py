"""Cada objeto Xano (tipo, grupo, nome, verbo) tem um único documento versionado.

Dois arquivos para o mesmo objeto tornam ambíguo o `xano workspace push`; a
duplicação de `gerente/ativos-historicos` GET surgiu no merge de `main`
(nomes de arquivo diferentes, sem conflito Git) e foi removida em 2026-11-08.
"""

import collections
import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
CABECALHO = re.compile(r'^(function|query|table|task|middleware|trigger)\s+"?([^"\s]+)"?(?:\s+verb=(\w+))?', re.M)
GRUPO = re.compile(r'^\s*api_group\s*=\s*"([^"]+)"', re.M)


def test_nenhum_objeto_xano_tem_dois_documentos():
    vistos = collections.defaultdict(list)
    for arquivo in (ROOT / "xano").rglob("*.xs"):
        texto = arquivo.read_text(encoding="utf-8")
        cabecalho = CABECALHO.search(texto)
        if not cabecalho:
            continue
        grupo = GRUPO.search(texto)
        chave = (cabecalho.group(1), grupo.group(1) if grupo else "", cabecalho.group(2), cabecalho.group(3) or "")
        vistos[chave].append(arquivo.relative_to(ROOT).as_posix())
    duplicados = {chave: arquivos for chave, arquivos in vistos.items() if len(arquivos) > 1}
    assert duplicados == {}
