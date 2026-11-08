"""Contrato estático dos documentos reconciliados com o Xano publicado.

Change `reconciliar-contratos-publicados`: regra de Loja ativa na criação
administrativa de Gerente e nas opções de Loja, e gate do Gerente na abertura
manual. Lê o XanoScript versionado; não executa o runtime Xano.
"""

import re
from pathlib import Path


X = Path(__file__).resolve().parents[1] / "xano"
OPCOES = (X / "function/administracao/listar_opcoes_lojas.xs").read_text(encoding="utf-8")
VALIDACAO = (X / "function/administracao/validar_criacao_usuario.xs").read_text(encoding="utf-8")
ABERTURA_API = (X / "api/mira_service_desk/gerente/chamados_POST.xs").read_text(encoding="utf-8")

STATUS_ATIVOS = ('"Ativa"', '"ativa"', '"Ativo"')


def compacto(texto):
    return re.sub(r"\s+", "", texto)


def test_opcoes_de_loja_listam_somente_lojas_ativas():
    consulta = OPCOES[OPCOES.index("db.query lojas"):OPCOES.index("} as $lojas")]
    where = re.search(r"where = (.*)", consulta).group(1)
    for status in STATUS_ATIVOS:
        assert f"$db.lojas.status == {status}" in where
    assert "!=" not in where


def test_gerente_exige_loja_existente_e_ativa():
    precondicao = compacto(
        'precondition ($loja != null && ($loja.status == "Ativa" || $loja.status == "ativa" || $loja.status == "Ativo"))'
    )
    assert precondicao in compacto(VALIDACAO)
    assert 'error = "Loja inexistente ou Inativa."' in VALIDACAO


def test_validacao_preserva_casos_de_loja_ativa_e_legada():
    assert 'test "aceita gerente com loja existente"' in VALIDACAO
    assert 'test "aceita gerente com loja legada Ativo"' in VALIDACAO
    assert 'test "rejeita gerente loja inexistente"' in VALIDACAO
    assert "db.add" not in VALIDACAO


def test_abertura_manual_exige_perfil_gerente_antes_da_funcao():
    stack = ABERTURA_API[ABERTURA_API.index("stack {"):ABERTURA_API.index("response =")]
    gate = compacto('function.run "autorizacao/exigir_perfil" {input = {usuarios_id: $auth.id, gerente: true}}')
    assert gate in compacto(stack)
    assert stack.index('"autorizacao/exigir_perfil"') < stack.index('"service_desk/abrir_chamado_manual"')
    assert "administrador" not in stack
