// Lista, somente para leitura, os chamados em que a identidade autenticada é
// a solicitante, independentemente da Loja atual. Sem filtros nem paginação.
function "service_desk/listar_chamados_solicitante" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {
        usuarios_id  : $input.usuarios_id
        gerente      : true
        tecnico      : true
        diretoria    : true
        administrador: true
      }
      mock = {
        "lista chamados do solicitante": {id: 8, nome: "Gerente", email: "gerente@example.test", role: "gerente", lojas_id: 2, deve_trocar_senha: false}
        "lista vazia sem chamados"     : {id: 12, nome: "Técnico", email: "tecnico@example.test", role: "tecnico", lojas_id: null, deve_trocar_senha: false}
      }
    } as $usuario

    db.query chamados {
      join = {
        ativos_referencia: {
          table: "ativos_referencia"
          type: "left"
          where: $db.chamados.ativos_referencia_id == $db.ativos_referencia.id
        }
        categorias_servico: {
          table: "categorias_servico"
          type: "left"
          where: $db.chamados.categorias_servico_id == $db.categorias_servico.id
        }
      }
      eval = {
        ativo_id: $db.ativos_referencia.id
        ativo_nome: $db.ativos_referencia.nome_ativo
        categoria_id: $db.categorias_servico.id
        categoria_nome: $db.categorias_servico.nome
      }
      where = $db.chamados.solicitante_id == $usuario.id
      sort = {chamados.ultima_atualizacao_em: "desc", chamados.id: "desc"}
      return = {type: "list"}
      mock = {
        "lista chamados do solicitante": [
          {id: 102, titulo: "Impressora", descricao: "Sem papel", status: "Resolvido", prioridade: "Média", origem: "manual", criado_em: 1780000000000, ultima_atualizacao_em: 1780000009000, ativo_id: 3, ativo_nome: "Totem 03", categoria_id: 2, categoria_nome: "Falha de Rede"},
          {id: 101, titulo: "Falha", descricao: "Totem não conecta", status: "Novo", prioridade: "Alta", origem: "manual", criado_em: 1780000000000, ultima_atualizacao_em: 1780000001000, ativo_id: 1, ativo_nome: "Totem 01", categoria_id: 2, categoria_nome: "Falha de Rede"}
        ]
        "lista vazia sem chamados"     : []
      }
    } as $chamados

    var $items {
      value = $chamados|map:{
        id: $$.id,
        titulo: $$.titulo,
        descricao: $$.descricao,
        status: $$.status,
        prioridade: $$.prioridade,
        origem: $$.origem,
        criado_em: $$.criado_em,
        ultima_atualizacao_em: $$.ultima_atualizacao_em,
        ativo: {id: $$.ativo_id, nome_ativo: $$.ativo_nome},
        categoria: {id: $$.categoria_id, nome: $$.categoria_nome}
      }
    }
  }

  response = {items: $items}

  test "lista chamados do solicitante" {
    input = {usuarios_id: 8}

    expect.to_equal ($response.items) {
      value = [
        {id: 102, titulo: "Impressora", descricao: "Sem papel", status: "Resolvido", prioridade: "Média", origem: "manual", criado_em: 1780000000000, ultima_atualizacao_em: 1780000009000, ativo: {id: 3, nome_ativo: "Totem 03"}, categoria: {id: 2, nome: "Falha de Rede"}},
        {id: 101, titulo: "Falha", descricao: "Totem não conecta", status: "Novo", prioridade: "Alta", origem: "manual", criado_em: 1780000000000, ultima_atualizacao_em: 1780000001000, ativo: {id: 1, nome_ativo: "Totem 01"}, categoria: {id: 2, nome: "Falha de Rede"}}
      ]
    }
  }

  test "lista vazia sem chamados" {
    input = {usuarios_id: 12}

    expect.to_be_empty ($response.items)
  }

  guid = "miraChamadosSolicitante01"
}
