// Registra um comentário operacional sem acionar o Save de tratativa.
// A operação aceita chamados terminais, mas não escreve nenhum campo funcional.
function "service_desk/criar_comentario_operacional" {
  input {
    int usuarios_id {
      table = "usuarios"
    }
    int chamados_id
    text? conteudo? filters=trim
    text visibilidade filters=trim
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
        "cria comentário público": {id: 12, nome: "Técnico", role: "tecnico"}
        "cria comentário interno": {id: 13, nome: "Diretora", role: "diretoria"}
        "cria comentário em terminal": {id: 14, nome: "Administradora", role: "administrador"}
        "rejeita comentário vazio": {id: 12, nome: "Técnico", role: "tecnico"}
        "rejeita comentário com espaços": {id: 12, nome: "Técnico", role: "tecnico"}
      }
    } as $usuario

    conditional {
      if ($input.conteudo == null || $input.conteudo == "") {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }
        precondition (false) {
          error_type = "inputerror"
          error = "Comentário não pode estar vazio."
        }
      }
      elseif ($input.visibilidade != "publica" && $input.visibilidade != "interna") {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }
        precondition (false) {
          error_type = "inputerror"
          error = "Visibilidade do comentário inválida."
        }
      }
    }

    var $comentario_criado { value = null }
    var $instante {
      value = now
      mock = {
        "cria comentário público": 1780000001000
        "cria comentário interno": 1780000001100
        "cria comentário em terminal": 1780000001200
      }
    }

    db.transaction {
      stack {
        db.get chamados {
          field_name = "id"
          field_value = $input.chamados_id
          mock = {
            "cria comentário público": {id: 101, status: "Novo", prioridade: "Média", tecnico_id: null, categorias_servico_id: 2, sla_horas_aplicado: 8, atribuido_em: null, ultima_atualizacao_em: 1780000000000}
            "cria comentário interno": {id: 102, status: "Resolvido", prioridade: "Alta", tecnico_id: 12, categorias_servico_id: 2, sla_horas_aplicado: 8, atribuido_em: 1780000000000, ultima_atualizacao_em: 1780000000100}
            "cria comentário em terminal": {id: 103, status: "Encerrado", prioridade: "Alta", tecnico_id: 12, categorias_servico_id: 2, sla_horas_aplicado: 8, atribuido_em: 1780000000000, ultima_atualizacao_em: 1780000000200}
          }
        } as $chamado

        precondition ($chamado != null) {
          error_type = "notfound"
          error = "Recurso não encontrado."
        }

        db.add interacoes_chamado {
          data = {
            tipo_evento: "comentario"
            mensagem: $input.conteudo
            criado_em: $instante
            visibilidade: $input.visibilidade
            chamados_id: $chamado.id
            usuarios_id: $usuario.id
          }
          mock = {
            "cria comentário público": {id: 301, tipo_evento: "comentario", mensagem: "Atualização pública", criado_em: 1780000001000, visibilidade: "publica", chamados_id: 101, usuarios_id: 12}
            "cria comentário interno": {id: 302, tipo_evento: "comentario", mensagem: "Atualização interna", criado_em: 1780000001100, visibilidade: "interna", chamados_id: 102, usuarios_id: 13}
            "cria comentário em terminal": {id: 303, tipo_evento: "comentario", mensagem: "Registro após encerramento", criado_em: 1780000001200, visibilidade: "interna", chamados_id: 103, usuarios_id: 14}
          }
        } as $novo_comentario

        precondition ($novo_comentario != null) {
          error_type = "standard"
          error = "Não foi possível registrar o comentário."
        }

        db.patch chamados {
          field_name = "id"
          field_value = $chamado.id
          data = {ultima_atualizacao_em: $instante}
          mock = {
            "cria comentário público": {id: 101, ultima_atualizacao_em: 1780000001000}
            "cria comentário interno": {id: 102, ultima_atualizacao_em: 1780000001100}
            "cria comentário em terminal": {id: 103, ultima_atualizacao_em: 1780000001200}
          }
        } as $chamado_atualizado

        precondition ($chamado_atualizado != null) {
          error_type = "standard"
          error = "Não foi possível atualizar o chamado."
        }

        var.update $comentario_criado {
          value = $novo_comentario
        }
      }
    }

    function.run "service_desk/obter_chamado_tecnico" {
      input = {usuarios_id: $usuario.id, chamados_id: $input.chamados_id}
      mock = {
        "cria comentário público": {chamado: {id: 101, status: "Novo", prioridade: "Média", tecnico: null, atribuido_em: null, ultima_atualizacao_em: 1780000001000, categoria: {id: 2, nome: "Rede"}}, timeline: [{id: 301, tipo: "comentario", conteudo: "Atualização pública", alteracoes: null, visibilidade: "publica", criado_em: 1780000001000, autor: {id: 12, nome: "Técnico"}, tecnico_anterior: null, tecnico_novo: null}], tecnicos: []}
        "cria comentário interno": {chamado: {id: 102, status: "Resolvido", prioridade: "Alta", tecnico: {id: 12, nome: "Técnico"}, atribuido_em: 1780000000000, ultima_atualizacao_em: 1780000001100, categoria: {id: 2, nome: "Rede"}}, timeline: [{id: 302, tipo: "comentario", conteudo: "Atualização interna", alteracoes: null, visibilidade: "interna", criado_em: 1780000001100, autor: {id: 13, nome: "Diretora"}, tecnico_anterior: null, tecnico_novo: null}], tecnicos: []}
        "cria comentário em terminal": {chamado: {id: 103, status: "Encerrado", prioridade: "Alta", tecnico: {id: 12, nome: "Técnico"}, atribuido_em: 1780000000000, ultima_atualizacao_em: 1780000001200, categoria: {id: 2, nome: "Rede"}}, timeline: [{id: 303, tipo: "comentario", conteudo: "Registro após encerramento", alteracoes: null, visibilidade: "interna", criado_em: 1780000001200, autor: {id: 14, nome: "Administradora"}, tecnico_anterior: null, tecnico_novo: null}], tecnicos: []}
      }
    } as $detalhe
  }

  response = $detalhe

  test "cria comentário público" {
    input = {usuarios_id: 12, chamados_id: 101, conteudo: "Atualização pública", visibilidade: "publica"}
    expect.to_equal ($response.chamado.ultima_atualizacao_em) { value = 1780000001000 }
  }

  test "cria comentário interno" {
    input = {usuarios_id: 13, chamados_id: 102, conteudo: "Atualização interna", visibilidade: "interna"}
    expect.to_equal ($response.chamado.status) { value = "Resolvido" }
  }

  test "cria comentário em terminal" {
    input = {usuarios_id: 14, chamados_id: 103, conteudo: "Registro após encerramento", visibilidade: "interna"}
    expect.to_equal ($response.chamado.status) { value = "Encerrado" }
  }

  test "rejeita comentário vazio" {
    input = {usuarios_id: 12, chamados_id: 101, conteudo: "", visibilidade: "publica"}
    expect.to_throw { exception = "" }
  }

  test "rejeita comentário com espaços" {
    input = {usuarios_id: 12, chamados_id: 101, conteudo: "   ", visibilidade: "interna"}
    expect.to_throw { exception = "" }
  }

  guid = "miraCriarComentarioOperacional01"
}
