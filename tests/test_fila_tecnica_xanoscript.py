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
CATEGORIAS_TRATATIVA = (
    ROOT / "xano/function/service_desk/listar_categorias_tratativa.xs"
).read_text(encoding="utf-8")
CATEGORIAS_TRATATIVA_API = (
    ROOT / "xano/api/mira_service_desk/tecnico/categorias_GET.xs"
).read_text(encoding="utf-8")
SAVE_TRATATIVA = (
    ROOT / "xano/function/service_desk/validar_save_tratativa_chamado.xs"
).read_text(encoding="utf-8")
SAVE_TRATATIVA_API = (
    ROOT / "xano/api/mira_service_desk/tecnico/chamados/chamados_id_tratativa_POST.xs"
).read_text(encoding="utf-8")
COMENTARIO_OPERACIONAL = (
    ROOT / "xano/function/service_desk/criar_comentario_operacional.xs"
).read_text(encoding="utf-8")
COMENTARIO_OPERACIONAL_API = (
    ROOT
    / "xano/api/mira_service_desk/tecnico/chamados/chamados_id_comentarios_POST.xs"
).read_text(encoding="utf-8")
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
    assert 'tipo_evento: "alteracao_chamado"' in DETALHE
    assert "json? alteracoes?" in (ROOT / "xano/table/interacoes_chamado.xs").read_text(
        encoding="utf-8"
    )
    assert 'alteracoes: $$.alteracoes' in DETALHE
    assert "{id: 12, tipo: \"comentario\"" in DETALHE
    assert "{id: 14, tipo: \"reatribuicao\"" in DETALHE


def test_listagem_normaliza_timestamp_de_atribuicao_nulo_do_xano():
    assert "atribuido_em: ($$.atribuido_em != null && $$.atribuido_em != 0) ? $$.atribuido_em : null" in LISTAGEM


def test_catalogo_de_tratativa_lista_somente_categoria_ativa_sem_regra_manual():
    schema = (ROOT / "xano/table/categorias_servico.xs").read_text(encoding="utf-8")

    assert "bool ativo?=true" in schema
    assert (
        "where = $db.categorias_servico.ativo == true || "
        "$db.categorias_servico.ativo == null"
    ) in CATEGORIAS_TRATATIVA
    assert 'ativo: null' in CATEGORIAS_TRATATIVA
    assert "permite_abertura_manual ==" not in CATEGORIAS_TRATATIVA
    assert "function.run \"autorizacao/exigir_perfil\"" in CATEGORIAS_TRATATIVA
    assert "tecnico: true, diretoria: true, administrador: true" in CATEGORIAS_TRATATIVA
    assert 'query "tecnico/categorias" verb=GET' in CATEGORIAS_TRATATIVA_API
    assert 'auth = "usuarios"' in CATEGORIAS_TRATATIVA_API
    assert 'function.run "service_desk/listar_categorias_tratativa"' in CATEGORIAS_TRATATIVA_API


def test_detalhe_preserva_categoria_persistida_sem_consultar_ativo():
    assert 'categoria: {id: $input.registro.categoria_id, nome: $input.registro.categoria_nome}' in (
        ROOT / "xano/function/service_desk/construir_dto_chamado_tecnico.xs"
    ).read_text(encoding="utf-8")
    assert 'where: $db.chamados.categorias_servico_id == $db.categoria.id' in DETALHE
    assert "categoria.ativo" not in DETALHE


def test_save_da_tratativa_persiste_em_transacao_unica_e_retorna_detalhe_canonico():
    assert 'query "tecnico/chamados/{chamados_id}/tratativa" verb=POST' in SAVE_TRATATIVA_API
    assert 'auth = "usuarios"' in SAVE_TRATATIVA_API
    assert 'function.run "service_desk/validar_save_tratativa_chamado"' in SAVE_TRATATIVA_API
    for campo in (
        "int? tecnico_id?",
        "text status filters=trim",
        "text prioridade filters=trim",
        "int categorias_servico_id",
        "timestamp ultima_atualizacao_em",
        "text? comentario_status? filters=trim",
        "text? visibilidade_comentario_status? filters=trim",
    ):
        assert campo in SAVE_TRATATIVA

    assert 'function.run "autorizacao/exigir_perfil"' in SAVE_TRATATIVA
    assert "tecnico: true, diretoria: true, administrador: true" in SAVE_TRATATIVA
    assert "$input.ultima_atualizacao_em != $chamado.ultima_atualizacao_em" in SAVE_TRATATIVA
    assert "HTTP/1.1 409 Conflict" in SAVE_TRATATIVA
    assert '$input.status == "Aguardando Terceiro"' not in SAVE_TRATATIVA
    inicio_transacao = SAVE_TRATATIVA.index("db.transaction {")
    patch_chamado = SAVE_TRATATIVA.index("db.patch chamados")
    confirmacao_persistida = SAVE_TRATATIVA.index("} as $chamado_persistido")
    comentario_status = SAVE_TRATATIVA.index('tipo_evento: "comentario"')
    evento_alteracao = SAVE_TRATATIVA.index('tipo_evento: "alteracao_chamado"')
    detalhe_canonico = SAVE_TRATATIVA.index('function.run "service_desk/obter_chamado_tecnico"')

    assert inicio_transacao < patch_chamado < confirmacao_persistida < comentario_status < evento_alteracao < detalhe_canonico
    assert 'response = $detalhe' in SAVE_TRATATIVA
    assert 'if ($houve_diferenca_funcional)' in SAVE_TRATATIVA
    assert "precondition ($comentario_status_criado != null)" in SAVE_TRATATIVA
    assert 'tecnico_id: $input.tecnico_id' in SAVE_TRATATIVA
    assert 'atribuido_em: $atribuido_em_resultante' in SAVE_TRATATIVA
    assert 'ultima_atualizacao_em: $instante' in SAVE_TRATATIVA
    assert 'value = $responsavel_alterado || $status_alterado || $prioridade_alterada || $categoria_alterada' in SAVE_TRATATIVA
    assert 'value = ($chamado_persistido.tecnico_id == null || $chamado_persistido.tecnico_id == 0) ? null : $chamado_persistido.tecnico_id' in SAVE_TRATATIVA
    confirmacao_nao_nula = SAVE_TRATATIVA.index("precondition ($chamado_persistido != null)")
    tecnico_persistido = SAVE_TRATATIVA.index("var $tecnico_persistido_id", confirmacao_nao_nula)
    confirmacao_campos = SAVE_TRATATIVA.index("precondition ($tecnico_persistido_id == $input.tecnico_id", tecnico_persistido)
    assert confirmacao_nao_nula < tecnico_persistido < confirmacao_campos
    assert 'test "libera responsável"' in SAVE_TRATATIVA


def test_save_gera_um_evento_estruturado_completo_e_preserva_categoria_inativa_sem_troca():
    assert SAVE_TRATATIVA.count('db.add interacoes_chamado') == 2
    assert SAVE_TRATATIVA.count('data = {tipo_evento: "alteracao_chamado"') == 1
    assert 'value = $alteracoes|set:"responsavel":' in SAVE_TRATATIVA
    assert 'value = $alteracoes|set:"status":' in SAVE_TRATATIVA
    assert 'value = $alteracoes|set:"prioridade":' in SAVE_TRATATIVA
    assert 'value = $alteracoes|set:"categoria":' in SAVE_TRATATIVA
    assert 'value = $alteracoes|set:"sla_horas_aplicado":' in SAVE_TRATATIVA
    assert 'if ($categoria_alterada)' in SAVE_TRATATIVA
    assert 'if ($categoria == null || $categoria.ativo == false)' in SAVE_TRATATIVA
    assert 'test "preserva categoria inativa sem troca"' in SAVE_TRATATIVA
    assert 'test "salva sem diferença"' in SAVE_TRATATIVA
    # O cenário Xano sem diferenças percorre o contrato sem mock de escrita;
    # o bloco de patch/interações só é alcançável dentro desta guarda.
    inicio_sem_diferenca = SAVE_TRATATIVA.index('if ($houve_diferenca_funcional)')
    patch_chamado = SAVE_TRATATIVA.index("db.patch chamados")
    assert inicio_sem_diferenca < patch_chamado


def test_save_valida_status_comentario_responsavel_e_categoria_sem_regra_manual():
    assert 'error = "Mudança de Status exige comentário."' in SAVE_TRATATIVA
    assert 'error = "Este Status exige comentário Público."' in SAVE_TRATATIVA
    assert '$responsavel.role == "tecnico"' in SAVE_TRATATIVA
    assert '$categoria.ativo == false' in SAVE_TRATATIVA
    assert "permite_abertura_manual" not in SAVE_TRATATIVA
    assert 'test "preserva categoria inativa sem troca"' in SAVE_TRATATIVA
    assert 'test "rejeita categoria inativa na troca"' in SAVE_TRATATIVA


def test_save_cobre_rollback_conflito_status_invalido_e_status_terminais_no_xano():
    # Estes são casos de teste inline do Xano, não somente afirmações Python:
    # cada um recebe mocks completos do caminho que alcança ou aborta a transação.
    for caso in (
        'test "falha ao persistir chamado"',
        'test "falha ao criar comentário de status"',
        'test "falha ao criar auditoria"',
        'test "rejeita versão desatualizada"',
        'test "rejeita aguardando terceiro"',
        'test "encerra manualmente com alterações"',
        'test "cancela com alterações combinadas"',
    ):
        assert caso in SAVE_TRATATIVA

    assert '"falha ao persistir chamado": null' in SAVE_TRATATIVA
    falha_patch = SAVE_TRATATIVA.index('"falha ao persistir chamado": null')
    patch_iniciado = SAVE_TRATATIVA.rfind("db.patch chamados", 0, falha_patch)
    patch_confirmado = SAVE_TRATATIVA.index("precondition ($chamado_atualizado != null)", falha_patch)
    comentario = SAVE_TRATATIVA.index('tipo_evento: "comentario"', patch_confirmado)
    auditoria = SAVE_TRATATIVA.index('tipo_evento: "alteracao_chamado"', comentario)
    assert patch_iniciado < falha_patch < patch_confirmado < comentario < auditoria

    falha_comentario = SAVE_TRATATIVA.index('"falha ao criar comentário de status": null')
    falha_auditoria = SAVE_TRATATIVA.index('"falha ao criar auditoria": null')
    precondition_comentario = SAVE_TRATATIVA.index("precondition ($comentario_status_criado != null)", falha_comentario)
    precondition_auditoria = SAVE_TRATATIVA.index("precondition ($evento_alteracao != null)", falha_auditoria)
    assert comentario < falha_comentario < precondition_comentario < auditoria
    assert auditoria < falha_auditoria < precondition_auditoria

    conflito = SAVE_TRATATIVA.index("$input.ultima_atualizacao_em != $chamado.ultima_atualizacao_em")
    status_invalido = SAVE_TRATATIVA.index("!$status_atual_valido || !$status_resultante_valido || !$prioridade_valida")
    terminal = SAVE_TRATATIVA.index('$chamado.status == "Encerrado" || $chamado.status == "Cancelado"', status_invalido)
    assert status_invalido < terminal < conflito < patch_iniciado
    assert '"encerra manualmente com alterações": {id: 101, tecnico_id: 10' in SAVE_TRATATIVA
    assert 'status: "Encerrado"' in SAVE_TRATATIVA
    assert '"cancela com alterações combinadas": {id: 101, tecnico_id: 10' in SAVE_TRATATIVA
    assert 'status: "Cancelado"' in SAVE_TRATATIVA
    assert 'status: "Aguardando Terceiro"' not in SAVE_TRATATIVA.split('input = {usuarios_id: 12, chamados_id: 101, tecnico_id: null, status: "Aguardando Terceiro"')[0]
    assert 'error = "Status ou prioridade inválido para tratativa."' in SAVE_TRATATIVA


def test_comentario_operacional_e_contrato_independente_do_save():
    assert (
        'query "tecnico/chamados/{chamados_id}/comentarios" verb=POST'
        in COMENTARIO_OPERACIONAL_API
    )
    assert 'auth = "usuarios"' in COMENTARIO_OPERACIONAL_API
    assert 'function.run "service_desk/criar_comentario_operacional"' in COMENTARIO_OPERACIONAL_API
    assert 'usuarios_id: $auth.id' in COMENTARIO_OPERACIONAL_API
    for campo in ("int chamados_id", "text? conteudo? filters=trim", "text visibilidade filters=trim"):
        assert campo in COMENTARIO_OPERACIONAL_API
    for campo_proibido in (
        "status:",
        "prioridade:",
        "tecnico_id:",
        "categorias_servico_id:",
        "sla_horas_aplicado:",
        "ultima_atualizacao_em:",
    ):
        assert campo_proibido not in COMENTARIO_OPERACIONAL_API


def test_comentario_operacional_valida_autor_visibilidade_e_conteudo():
    assert 'function.run "autorizacao/exigir_perfil"' in COMENTARIO_OPERACIONAL
    assert "tecnico: true, diretoria: true, administrador: true" in COMENTARIO_OPERACIONAL
    assert '$input.conteudo == null || $input.conteudo == ""' in COMENTARIO_OPERACIONAL
    assert 'error = "Comentário não pode estar vazio."' in COMENTARIO_OPERACIONAL
    assert '$input.visibilidade != "publica" && $input.visibilidade != "interna"' in COMENTARIO_OPERACIONAL
    assert 'error = "Visibilidade do comentário inválida."' in COMENTARIO_OPERACIONAL
    assert 'test "rejeita comentário vazio"' in COMENTARIO_OPERACIONAL
    assert 'test "rejeita comentário com espaços"' in COMENTARIO_OPERACIONAL


def test_comentario_operacional_persiste_apenas_comentario_e_ultima_atualizacao():
    inicio_transacao = COMENTARIO_OPERACIONAL.index("db.transaction {")
    cria_comentario = COMENTARIO_OPERACIONAL.index("db.add interacoes_chamado")
    atualiza_chamado = COMENTARIO_OPERACIONAL.index("db.patch chamados")
    detalhe = COMENTARIO_OPERACIONAL.index('function.run "service_desk/obter_chamado_tecnico"')

    assert inicio_transacao < cria_comentario < atualiza_chamado < detalhe
    assert COMENTARIO_OPERACIONAL.count("db.add interacoes_chamado") == 1
    assert 'tipo_evento: "comentario"' in COMENTARIO_OPERACIONAL
    assert 'tipo_evento: "alteracao_chamado"' not in COMENTARIO_OPERACIONAL
    assert "usuarios_id: $usuario.id" in COMENTARIO_OPERACIONAL
    assert "criado_em: $instante" in COMENTARIO_OPERACIONAL
    assert "visibilidade: $input.visibilidade" in COMENTARIO_OPERACIONAL

    patch = COMENTARIO_OPERACIONAL[atualiza_chamado:detalhe]
    assert "data = {ultima_atualizacao_em: $instante}" in patch
    for campo_funcional in (
        "status:",
        "prioridade:",
        "tecnico_id:",
        "categorias_servico_id:",
        "sla_horas_aplicado:",
        "atribuido_em:",
    ):
        assert campo_funcional not in patch


def test_comentario_operacional_aceita_terminal_e_mantem_timeline_compativel():
    assert '"cria comentário em terminal": {id: 103, status: "Encerrado"' in COMENTARIO_OPERACIONAL
    assert 'test "cria comentário em terminal"' in COMENTARIO_OPERACIONAL
    assert 'expect.to_equal ($response.chamado.status) { value = "Encerrado" }' in COMENTARIO_OPERACIONAL
    assert "timeline: [{id: 303, tipo: \"comentario\"" in COMENTARIO_OPERACIONAL
    assert "response = $detalhe" in COMENTARIO_OPERACIONAL
