"""Testes de contrato estático e isolamento para os novos contratos da Sprint 3:
- Rejeição de Solução pelo Gerente (DR2-1, D1, D2)
- Encerramento sob comando manual (DE-1 a DE-5, DE-9, D3)
- Exposição de SLA por perfil (DE-8, D5)
"""

from pathlib import Path
import re
import pytest

ROOT = Path(__file__).resolve().parents[1]
XANO = ROOT / "xano"

REJEICAO_FUNC = XANO / "function/service_desk/rejeitar_solucao_chamado_gerente.xs"
REJEICAO_API = XANO / "api/mira_service_desk/gerente/chamados/chamados_id_rejeitar-solucao_POST.xs"

ENCERRAMENTO_FUNC = XANO / "function/service_desk/encerrar_chamados_resolvidos_elegiveis.xs"
ENCERRAMENTO_API = XANO / "api/mira_service_desk/automacao/encerrar_resolvidos_POST.xs"

SLA_GERENTE_FUNC = XANO / "function/service_desk/obter_consumo_sla_gerente.xs"
SLA_GERENTE_API = XANO / "api/mira_service_desk/gerente/chamados/chamados_id_consumo-sla_GET.xs"

SLA_TECNICO_FUNC = XANO / "function/service_desk/obter_consumo_sla_tecnico.xs"
SLA_TECNICO_API = XANO / "api/mira_service_desk/tecnico/chamados/chamados_id_consumo-sla_GET.xs"

COMENTARIOS_GERENTE = XANO / "function/service_desk/listar_comentarios_publicos_gerente.xs"
COMENTARIOS_SOLICITANTE = XANO / "function/service_desk/listar_comentarios_publicos_solicitante.xs"


def ler(caminho: Path) -> str:
    return caminho.read_text(encoding="utf-8")


def test_rejeicao_solucao_estrutura_e_validacoes():
    texto = ler(REJEICAO_FUNC)
    # Validação de autorização antes de escrita
    assert 'function.run "service_desk/obter_chamado_gerente_autorizado"' in texto
    # Validação de justificativa obrigatória
    assert "422 Unprocessable Entity" in texto
    assert 'return {' in texto
    assert 'sucesso: false' in texto
    assert 'value = $justificativa|trim' in texto
    assert 'if ($justificativa == null || $justificativa == "")' in texto
    assert 'text justificativa? filters=trim' not in ler(REJEICAO_API)
    # Validação de status Resolvido (409)
    assert 'if ($registro.status != "Resolvido")' in texto
    assert "409 Conflict" in texto
    # Validação de concorrência com ultima_atualizacao_em
    assert "if ($input.ultima_atualizacao_em == null || $registro.ultima_atualizacao_em != $input.ultima_atualizacao_em)" in texto
    assert 'value = $input.ultima_atualizacao_em' in texto
    assert '$revalidado.ultima_atualizacao_em != $versao_validada' in texto
    # Transação atômica para as escritas
    assert "db.transaction {" in texto
    assert 'status: "Solução Rejeitada"' in texto
    assert 'visibilidade: "publica"' in texto
    assert 'tipo_evento: "alteracao_chamado"' in texto
    assert 'anterior: "Resolvido"' in texto
    assert 'resultante: "Solução Rejeitada"' in texto
    assert "comentario_interacao_id:" in texto


def test_rejeicao_solucao_endpoint_roteamento():
    api = ler(REJEICAO_API)
    assert 'query "gerente/chamados/{chamados_id}/rejeitar-solucao" verb=POST' in api
    assert 'auth = "usuarios"' in api
    assert 'function.run "service_desk/rejeitar_solucao_chamado_gerente"' in api


def test_encerramento_funcao_regras_e_escritas():
    texto = ler(ENCERRAMENTO_FUNC)
    # Seleção de candidatos
    assert '$db.chamados.status == "Resolvido"' in texto
    # Reconstituição da linha do tempo
    assert '$db.interacoes_chamado.tipo_evento == "alteracao_chamado"' in texto
    # Constante versionada de vigência
    assert "$inicio_vigencia" in texto
    # Prazo de 72 horas em ms (259.200.000 ms)
    assert "259200000" in texto
    # Transação com revalidação
    assert "db.transaction {" in texto
    assert 'if ($revalidado.status != "Resolvido" || $revalidado.ultima_atualizacao_em != $candidato.ultima_atualizacao_em)' in texto
    # Texto oficial do comentário de sistema (DE-3a)
    assert "Chamado encerrado automaticamente após 72 horas em Resolvido sem rejeição da solução." in texto
    # Autor do encerramento é sistema (usuarios_id nulo)
    assert "usuarios_id: null" in texto
    assert 'status: "Encerrado"' in texto
    # Contagens retornadas no envelope
    assert "avaliados:" in texto
    assert "encerrados:" in texto
    assert "fora_vigencia:" in texto
    assert "prazo_nao_vencido:" in texto
    assert "nao_calculaveis:" in texto
    assert "conflitos:" in texto


def test_encerramento_endpoint_autenticacao():
    api = ler(ENCERRAMENTO_API)
    assert 'query "automacao/encerrar-resolvidos" verb=POST' in api
    assert "auth =" not in api  # Sem auth JWT de usuário
    assert "X-Mira-Encerramento-Key" in api
    assert "MIRA_ENCERRAMENTO_AUTOMATION_KEY" in api
    assert "401 Unauthorized" in api
    assert 'function.run "service_desk/encerrar_chamados_resolvidos_elegiveis"' in api


def test_exposicao_sla_gerente_e_tecnico():
    # Gerente
    func_gerente = ler(SLA_GERENTE_FUNC)
    assert 'function.run "service_desk/obter_chamado_gerente_autorizado"' in func_gerente
    assert 'function.run "service_desk/calcular_consumo_sla_chamado"' in func_gerente
    api_gerente = ler(SLA_GERENTE_API)
    assert 'query "gerente/chamados/{chamados_id}/consumo-sla" verb=GET' in api_gerente
    assert 'auth = "usuarios"' in api_gerente

    # Técnico
    func_tecnico = ler(SLA_TECNICO_FUNC)
    assert 'function.run "autorizacao/exigir_perfil"' in func_tecnico
    assert "tecnico: true, diretoria: true, administrador: true" in func_tecnico
    assert 'function.run "service_desk/calcular_consumo_sla_chamado"' in func_tecnico
    api_tecnico = ler(SLA_TECNICO_API)
    assert 'query "tecnico/chamados/{chamados_id}/consumo-sla" verb=GET' in api_tecnico
    assert 'auth = "usuarios"' in api_tecnico

    # Solicitante NÃO tem endpoint de consumo de SLA
    solicitante_sla = list((XANO / "api/mira_service_desk/solicitante").rglob("*sla*.xs"))
    assert solicitante_sla == [], "Solicitante não possui exposição de SLA nesta versão (DE-8)"


def test_comentarios_exibem_autor_sistema_no_encerramento():
    for caminho in (COMENTARIOS_GERENTE, COMENTARIOS_SOLICITANTE):
        texto = ler(caminho)
        assert "Chamado encerrado automaticamente após 72 horas em Resolvido sem rejeição da solução." in texto
        assert '{nome: "Sistema"}' in texto
        assert 'tipo_evento == "alteracao_chamado"' in texto
        assert 'get:"comentario_interacao_id":null' in texto
        assert '$anterior == "Resolvido" && $resultante == "Encerrado" && $comentario_id == $interacao.id' in texto
        assert 'test "identifica somente comentario do encerramento' in texto
