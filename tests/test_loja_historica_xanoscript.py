"""Contrato estático da regra de Loja histórica (change regularizar-loja-historica-totem).

Lê o XanoScript copiado do publicado. Não executa o runtime Xano; os cenários
com dados (vínculo anterior, transferência, marco, própria Loja) dependem de
registros que não existem e não foram criados.
"""

import re
from pathlib import Path

import pytest


ROOT = Path(__file__).parents[1]
X = ROOT / "xano"


def fonte(caminho):
    return (X / caminho).read_text(encoding="utf-8")


def compacto(texto):
    """Ignora espaços e delimitadores ``` da formatação exportada pelo Xano."""
    return re.sub(r"\s+|```", "", texto)


def logica(caminho):
    """Remove blocos `mock` e `test` para examinar somente a lógica."""
    texto = fonte(caminho)
    for inicio in (r"\bmock = \{", r'\n\s*test "[^"]*" \{'):
        saida, i = [], 0
        while True:
            m = re.compile(inicio).search(texto, i)
            if not m:
                saida.append(texto[i:])
                break
            saida.append(texto[i:m.start()])
            k, prof = texto.index("{", m.start()), 0
            while k < len(texto):
                if texto.startswith("```", k):
                    k = texto.index("```", k + 3) + 3
                    continue
                prof += {"{": 1, "}": -1}.get(texto[k], 0)
                if texto[k] == "}" and prof == 0:
                    break
                k += 1
            i = k + 1
        texto = "".join(saida)
    return "\n".join(linha for linha in texto.splitlines() if not linha.lstrip().startswith("//"))


RESOLVEDOR = "function/administracao/resolver_loja_totem_no_instante.xs"
FATO = "function/administracao/obter_loja_historica_fato.xs"
TRANSFERIR = "function/administracao/transferir_totem.xs"
AUTORIZADO = "function/service_desk/obter_chamado_gerente_autorizado.xs"
DETALHE_GERENTE = "function/service_desk/obter_chamado_gerente.xs"
DETALHE_SOLICITANTE = "function/service_desk/obter_chamado_solicitante.xs"
LISTA_GERENTE = "function/service_desk/listar_chamados_gerente.xs"
ABERTURA = "function/service_desk/abrir_chamado_manual.xs"
HEARTBEAT = "api/apis_from_table_telemetria_equipamentos/verificar_falhas_GET.xs"


def test_tabela_de_vinculos_preserva_tipos_instante_e_unicidade():
    tabela = compacto(fonte("table/historico_vinculos_totem_loja.xs"))
    assert compacto('values = ["criacao", "marco", "transferencia"]') in tabela
    assert compacto("timestamp efetivado_em") in tabela
    assert compacto("int? loja_origem_id?") in tabela and compacto("int loja_destino_id") in tabela
    assert compacto('{name: "ativos_referencia_id"}, {name: "efetivado_em"}') in tabela
    assert compacto('type : "btree|unique"') in tabela


def test_campo_identificacao_do_totem_preservado():
    """Evita o DROP_FIELD apontado pelo dry-run completo antes da regularização."""
    assert compacto("text? identificacao? filters=trim") in compacto(fonte("table/ativos_referencia.xs"))


def test_t1_t2_resolvedor_usa_vinculo_mais_recente_ate_o_instante():
    texto = compacto(logica(RESOLVEDOR))
    assert compacto(
        "where = $db.historico_vinculos_totem_loja.ativos_referencia_id == $input.ativos_referencia_id"
        " && $db.historico_vinculos_totem_loja.efetivado_em <= $input.instante"
    ) in texto
    assert compacto('sort = {historico_vinculos_totem_loja.efetivado_em: "desc"}') in texto
    assert compacto('return = {type: "single"}') in texto
    assert compacto("value = $vinculo.loja_destino_id") in texto


def test_t3_sem_vinculo_resolve_null_sem_fallback_para_loja_atual():
    texto = logica(RESOLVEDOR)
    assert compacto("var $lojas_id { value = null }") in compacto(texto)
    assert compacto("if ($input.instante != null)") in compacto(texto)
    assert "ativos_referencia" not in texto.replace("ativos_referencia_id", "")
    assert not re.search(r"\bdb\.(add|edit|patch|del)\b", texto)


@pytest.mark.parametrize("caminho", [ABERTURA, HEARTBEAT], ids=["abertura-manual", "heartbeat"])
def test_t4_chamado_novo_cria_marco_somente_sem_vinculo_e_no_instante_do_chamado(caminho):
    texto = compacto(logica(caminho))
    assert compacto('sort = {historico_vinculos_totem_loja.efetivado_em: "desc"}') in texto
    assert re.search(r"if\(\$ultimo_vinculo==null(&&\$ativo_atual\.lojas_id!=null)?\)\{dbaddhistorico_vinculos_totem_loja".replace("dbadd", r"db\.add"), texto)
    bloco = texto[texto.index("db.addhistorico_vinculos_totem_loja"):]
    bloco = bloco[: bloco.index("}as$marco")]
    assert 'tipo:"marco"' in bloco
    assert "efetivado_em:$criado_em" in bloco
    assert "loja_destino_id:$ativo_atual.lojas_id" in bloco
    assert "criado_em:$criado_em" in texto[texto.index("db.addchamados"):]


def test_marco_exige_loja_atual_e_nao_faz_fallback():
    abertura = compacto(logica(ABERTURA))
    heartbeat = compacto(logica(HEARTBEAT))

    assert compacto(
        "precondition ($ativo_atual != null && $ativo_atual.lojas_id != null"
    ) in abertura
    assert compacto(
        "if ($ultimo_vinculo == null && $ativo_atual.lojas_id != null)"
    ) in heartbeat
    assert heartbeat.index("if($ultimo_vinculo==null&&$ativo_atual.lojas_id!=null)") < heartbeat.index(
        "db.addhistorico_vinculos_totem_loja"
    )
    assert heartbeat.index("db.addhistorico_vinculos_totem_loja") < heartbeat.index(
        "db.addchamados"
    )
    assert "loja_destino_id:$ativo_atual.lojas_id" in heartbeat


def test_nao_retroatividade_nenhum_vinculo_com_instante_arbitrario():
    """Todo vínculo gravado usa o instante do próprio fato (now ou criado_em do chamado novo)."""
    gravacoes = []
    for caminho in X.rglob("*.xs"):
        texto = compacto(logica(caminho.relative_to(X)))
        for m in re.finditer(r"db\.addhistorico_vinculos_totem_loja\{data=\{(.*?)\}", texto):
            gravacoes.append((caminho.name, m.group(1)))
    assert {nome for nome, _ in gravacoes} == {"verificar_falhas_GET.xs", "abrir_chamado_manual.xs", "transferir_totem.xs", "totens_POST.xs"}
    for nome, dados in gravacoes:
        assert re.search(r"efetivado_em:\$(criado_em|efetivado_em)\b", dados), nome
    for caminho in X.rglob("*.xs"):
        texto = compacto(logica(caminho.relative_to(X)))
        assert not re.search(r"foreach\(\$chamados[^)]*\)\{[^}]*db\.addhistorico_vinculos", texto), caminho.name


def test_t5_t6_autorizador_do_gerente_usa_loja_historica():
    texto = compacto(logica(AUTORIZADO))
    assert compacto('function.run "administracao/resolver_loja_totem_no_instante"') in texto
    assert compacto("instante: $registro.criado_em") in texto
    assert compacto("precondition ($historico.lojas_id != null && $historico.lojas_id == $usuario.lojas_id)") in texto
    assert compacto("$registro.ativo_lojas_id == $usuario.lojas_id") not in texto


def test_detalhe_e_lista_do_gerente_usam_loja_historica():
    detalhe = compacto(logica(DETALHE_GERENTE))
    assert compacto("precondition ($historico.lojas_id != null && $historico.lojas_id == $usuario.lojas_id)") in detalhe
    assert compacto("loja: {id: $loja_historica.id, nome: $loja_historica.nome}") in detalhe
    lista = compacto(logica(LISTA_GERENTE))
    assert compacto("instante: $chamado.criado_em") in lista
    assert compacto("if ($historico.lojas_id != null && $historico.lojas_id == $usuario.lojas_id)") in lista


def test_fato_historico_projeta_loja_ou_null():
    texto = compacto(logica(FATO))
    assert compacto("var $loja { value = null }") in texto
    assert compacto("if ($vinculo.lojas_id != null)") in texto
    assert compacto("response = {loja: $loja}") in texto


def test_transferencia_registra_vinculo_somente_com_mudanca_de_loja_em_transacao():
    texto = compacto(logica(TRANSFERIR))
    assert compacto("db.transaction") in texto
    assert compacto("if ($totem.lojas_id != $input.loja_destino_id)") in texto
    assert compacto('tipo: "transferencia"') in texto
    assert compacto("loja_origem_id: $totem.lojas_id") in texto
    assert texto.index("db.addhistorico_vinculos_totem_loja") < texto.index("db.editativos_referencia")
    assert compacto("exigir_perfil") in texto and compacto("administrador: true") in texto


def test_exclusao_de_totem_remove_somente_vinculo_de_criacao():
    texto = compacto(logica("api/mira_administracao/totens/ativos_referencia_id_DELETE.xs"))
    assert compacto('$vinculos[0].tipo == "criacao"') in texto
    assert compacto("!$tem_chamado") in texto
