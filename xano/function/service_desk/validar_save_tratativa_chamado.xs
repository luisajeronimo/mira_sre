// Salva a tratativa operacional como uma única transação. O cliente envia o
// rascunho completo; as diferenças e a auditoria são sempre calculadas aqui.
function "service_desk/validar_save_tratativa_chamado" {
  input {
    int usuarios_id { table = "usuarios" }
    int chamados_id
    int? tecnico_id?
    text status filters=trim
    text prioridade filters=trim
    int categorias_servico_id
    timestamp ultima_atualizacao_em
    text? comentario_status? filters=trim
    text? visibilidade_comentario_status? filters=trim
  }

  stack {
    function.run "autorizacao/exigir_perfil" {
      input = {usuarios_id: $input.usuarios_id, tecnico: true, diretoria: true, administrador: true}
      mock = {
        "salva alterações combinadas": {id: 12, nome: "Técnico", role: "tecnico"}
        "salva sem diferença": {id: 12, nome: "Técnico", role: "tecnico"}
        "preserva categoria inativa sem troca": {id: 12, nome: "Técnico", role: "tecnico"}
        "rejeita categoria inativa na troca": {id: 12, nome: "Técnico", role: "tecnico"}
        "rejeita comentário ausente": {id: 12, nome: "Técnico", role: "tecnico"}
        "rejeita versão desatualizada": {id: 12, nome: "Técnico", role: "tecnico"}
        "falha ao persistir chamado": {id: 12, nome: "Técnico", role: "tecnico"}
        "falha ao criar comentário de status": {id: 12, nome: "Técnico", role: "tecnico"}
        "falha ao criar auditoria": {id: 12, nome: "Técnico", role: "tecnico"}
        "encerra manualmente com alterações": {id: 12, nome: "Técnico", role: "tecnico"}
        "cancela com alterações combinadas": {id: 12, nome: "Técnico", role: "tecnico"}
        "rejeita aguardando terceiro": {id: 12, nome: "Técnico", role: "tecnico"}
        "rejeita terminal": {id: 13, nome: "Administradora", role: "administrador"}
        "libera responsável": {id: 12, nome: "Técnico", role: "tecnico"}
      }
    } as $usuario

    var $houve_diferenca_funcional { value = false }

    // Toda leitura do chamado, validação dependente do estado atual e escrita
    // acontecem no mesmo escopo transacional.
    db.transaction {
      stack {
        db.get chamados {
          field_name = "id"
          field_value = $input.chamados_id
          mock = {
            "salva alterações combinadas": {id: 101, status: "Novo", prioridade: "Média", tecnico_id: 12, categorias_servico_id: 2, sla_horas_aplicado: 8, atribuido_em: 1780000001000, ultima_atualizacao_em: 1780000000000}
            "salva sem diferença": {id: 101, status: "Novo", prioridade: "Média", tecnico_id: null, categorias_servico_id: 2, sla_horas_aplicado: 8, atribuido_em: null, ultima_atualizacao_em: 1780000000000}
            "preserva categoria inativa sem troca": {id: 101, status: "Novo", prioridade: "Média", tecnico_id: null, categorias_servico_id: 9, sla_horas_aplicado: 8, atribuido_em: null, ultima_atualizacao_em: 1780000000000}
            "rejeita categoria inativa na troca": {id: 101, status: "Novo", prioridade: "Média", tecnico_id: null, categorias_servico_id: 2, sla_horas_aplicado: 8, atribuido_em: null, ultima_atualizacao_em: 1780000000000}
            "rejeita comentário ausente": {id: 101, status: "Novo", prioridade: "Média", tecnico_id: null, categorias_servico_id: 2, sla_horas_aplicado: 8, atribuido_em: null, ultima_atualizacao_em: 1780000000000}
            "rejeita versão desatualizada": {id: 101, status: "Novo", prioridade: "Média", tecnico_id: null, categorias_servico_id: 2, sla_horas_aplicado: 8, atribuido_em: null, ultima_atualizacao_em: 1780000001000}
            "falha ao persistir chamado": {id: 101, status: "Novo", prioridade: "Média", tecnico_id: null, categorias_servico_id: 2, sla_horas_aplicado: 8, atribuido_em: null, ultima_atualizacao_em: 1780000000000}
            "falha ao criar comentário de status": {id: 101, status: "Novo", prioridade: "Média", tecnico_id: null, categorias_servico_id: 2, sla_horas_aplicado: 8, atribuido_em: null, ultima_atualizacao_em: 1780000000000}
            "falha ao criar auditoria": {id: 101, status: "Novo", prioridade: "Média", tecnico_id: null, categorias_servico_id: 2, sla_horas_aplicado: 8, atribuido_em: null, ultima_atualizacao_em: 1780000000000}
            "encerra manualmente com alterações": {id: 101, status: "Em Atendimento", prioridade: "Média", tecnico_id: 12, categorias_servico_id: 2, sla_horas_aplicado: 8, atribuido_em: 1780000001000, ultima_atualizacao_em: 1780000000000}
            "cancela com alterações combinadas": {id: 101, status: "Em Atendimento", prioridade: "Média", tecnico_id: 12, categorias_servico_id: 2, sla_horas_aplicado: 8, atribuido_em: 1780000001000, ultima_atualizacao_em: 1780000000000}
            "rejeita aguardando terceiro": {id: 101, status: "Novo", prioridade: "Média", tecnico_id: null, categorias_servico_id: 2, sla_horas_aplicado: 8, atribuido_em: null, ultima_atualizacao_em: 1780000000000}
            "rejeita terminal": {id: 101, status: "Encerrado", prioridade: "Média", tecnico_id: 12, categorias_servico_id: 2, sla_horas_aplicado: 8, atribuido_em: 1780000001000, ultima_atualizacao_em: 1780000000000}
            "libera responsável": {id: 101, status: "Em Atendimento", prioridade: "Média", tecnico_id: 12, categorias_servico_id: 2, sla_horas_aplicado: 8, atribuido_em: 1780000001000, ultima_atualizacao_em: 1780000000000}
          }
        } as $chamado

        precondition ($chamado != null) {
          error_type = "notfound"
          error = "Recurso não encontrado."
        }

        var $status_atual_valido {
          value = $chamado.status == "Novo" || $chamado.status == "Em Atendimento" || $chamado.status == "Aguardando Solicitante" || $chamado.status == "Aguardando Mudança" || $chamado.status == "Resolvido" || $chamado.status == "Solução Rejeitada" || $chamado.status == "Encerrado" || $chamado.status == "Cancelado"
        }
        var $status_resultante_valido {
          value = $input.status == "Novo" || $input.status == "Em Atendimento" || $input.status == "Aguardando Solicitante" || $input.status == "Aguardando Mudança" || $input.status == "Resolvido" || $input.status == "Solução Rejeitada" || $input.status == "Encerrado" || $input.status == "Cancelado"
        }
        var $prioridade_valida {
          value = $input.prioridade == "Baixa" || $input.prioridade == "Média" || $input.prioridade == "Alta" || $input.prioridade == "Urgente"
        }

        conditional {
          if (!$status_atual_valido || !$status_resultante_valido || !$prioridade_valida) {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }
            precondition (false) {
              error_type = "inputerror"
              error = "Status ou prioridade inválido para tratativa."
            }
          }
          elseif ($chamado.status == "Encerrado" || $chamado.status == "Cancelado") {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }
            precondition (false) {
              error_type = "inputerror"
              error = "Chamado terminal não permite edição funcional."
            }
          }
          elseif ($input.ultima_atualizacao_em != $chamado.ultima_atualizacao_em) {
            util.set_header {
              value = "HTTP/1.1 409 Conflict"
              duplicates = "replace"
            }
            precondition (false) {
              error_type = "inputerror"
              error = "O chamado foi atualizado por outra operação. Recarregue o detalhe."
            }
          }
          elseif ($input.tecnico_id != null && $input.tecnico_id < 1) {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }
            precondition (false) {
              error_type = "inputerror"
              error = "Responsável inválido."
            }
          }
        }

        var $tecnico_atual_id { value = ($chamado.tecnico_id == null || $chamado.tecnico_id == 0) ? null : $chamado.tecnico_id }
        var $responsavel_alterado { value = $input.tecnico_id != $tecnico_atual_id }
        var $status_alterado { value = $input.status != $chamado.status }
        var $prioridade_alterada { value = $input.prioridade != $chamado.prioridade }
        var $categoria_alterada { value = $input.categorias_servico_id != $chamado.categorias_servico_id }

        conditional {
          if ($status_alterado && ($input.comentario_status == null || $input.comentario_status == "")) {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }
            precondition (false) {
              error_type = "inputerror"
              error = "Mudança de Status exige comentário."
            }
          }
          elseif ($input.comentario_status != null && $input.comentario_status != "" && $input.visibilidade_comentario_status != "publica" && $input.visibilidade_comentario_status != "interna") {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }
            precondition (false) {
              error_type = "inputerror"
              error = "Visibilidade do comentário de Status inválida."
            }
          }
          elseif ($status_alterado && ($input.status == "Resolvido" || $input.status == "Aguardando Solicitante" || $input.status == "Cancelado") && $input.visibilidade_comentario_status != "publica") {
            util.set_header {
              value = "HTTP/1.1 422 Unprocessable Entity"
              duplicates = "replace"
            }
            precondition (false) {
              error_type = "inputerror"
              error = "Este Status exige comentário Público."
            }
          }
        }

        var $responsavel { value = null }
        var $comentario_criado { value = null }
        conditional {
          if ($input.tecnico_id != null && $responsavel_alterado) {
            db.get usuarios {
              field_name = "id"
              field_value = $input.tecnico_id
              mock = {
                "salva alterações combinadas": {id: 10, nome: "Outro Técnico", role: "tecnico"}
                "encerra manualmente com alterações": {id: 10, nome: "Outro Técnico", role: "tecnico"}
                "cancela com alterações combinadas": {id: 10, nome: "Outro Técnico", role: "tecnico"}
              }
            } as $usuario_responsavel
            var.update $responsavel { value = $usuario_responsavel }
            precondition ($responsavel != null && $responsavel.role == "tecnico") {
              error_type = "inputerror"
              error = "Responsável deve possuir perfil Técnico."
            }
          }
        }

        var $categoria { value = null }
        conditional {
          if ($categoria_alterada) {
            db.get categorias_servico {
              field_name = "id"
              field_value = $input.categorias_servico_id
              mock = {
                "salva alterações combinadas": {id: 3, nome: "Hardware", sla_horas: 4, ativo: true}
                "rejeita categoria inativa na troca": {id: 9, nome: "Legada", sla_horas: 8, ativo: false}
                "cancela com alterações combinadas": {id: 3, nome: "Hardware", sla_horas: 4, ativo: true}
              }
            } as $categoria_nova
            var.update $categoria { value = $categoria_nova }
            conditional {
              if ($categoria == null || $categoria.ativo == false) {
                util.set_header {
                  value = "HTTP/1.1 422 Unprocessable Entity"
                  duplicates = "replace"
                }
                precondition (false) {
                  error_type = "inputerror"
                  error = "A nova Categoria deve estar ativa."
                }
              }
            }
          }
        }

        var $instante {
          value = now
          mock = {
            "salva alterações combinadas": 1780000002000
            "preserva categoria inativa sem troca": 1780000002000
            "libera responsável": 1780000002000
            "falha ao persistir chamado": 1780000002000
            "falha ao criar comentário de status": 1780000002000
            "falha ao criar auditoria": 1780000002000
            "encerra manualmente com alterações": 1780000002000
            "cancela com alterações combinadas": 1780000002000
          }
        }
        var $atribuido_em_resultante {
          value = $responsavel_alterado ? (($input.tecnico_id == null) ? null : $instante) : $chamado.atribuido_em
        }
        var $sla_horas_resultante { value = $categoria_alterada ? $categoria.sla_horas : $chamado.sla_horas_aplicado }
        var $alteracoes { value = {} }

        conditional {
          if ($responsavel_alterado) {
            var.update $alteracoes { value = $alteracoes|set:"responsavel":{anterior: $tecnico_atual_id, resultante: $input.tecnico_id} }
          }
        }
        conditional {
          if ($status_alterado) {
            var.update $alteracoes { value = $alteracoes|set:"status":{anterior: $chamado.status, resultante: $input.status} }
          }
        }
        conditional {
          if ($prioridade_alterada) {
            var.update $alteracoes { value = $alteracoes|set:"prioridade":{anterior: $chamado.prioridade, resultante: $input.prioridade} }
          }
        }
        conditional {
          if ($categoria_alterada) {
            var.update $alteracoes { value = $alteracoes|set:"categoria":{anterior: $chamado.categorias_servico_id, resultante: $input.categorias_servico_id} }
            var.update $alteracoes { value = $alteracoes|set:"sla_horas_aplicado":{anterior: $chamado.sla_horas_aplicado, resultante: $categoria.sla_horas} }
          }
        }

        var.update $houve_diferenca_funcional {
          value = $responsavel_alterado || $status_alterado || $prioridade_alterada || $categoria_alterada
        }
        conditional {
          if ($houve_diferenca_funcional) {
            // db.patch preserva null explícito em liberações.
            db.patch chamados {
              field_name = "id"
              field_value = $chamado.id
              data = {
                tecnico_id: $input.tecnico_id
                atribuido_em: $atribuido_em_resultante
                status: $input.status
                prioridade: $input.prioridade
                categorias_servico_id: $input.categorias_servico_id
                sla_horas_aplicado: $sla_horas_resultante
                ultima_atualizacao_em: $instante
              }
              mock = {
                "salva alterações combinadas": {id: 101, tecnico_id: 10, atribuido_em: 1780000002000, status: "Em Atendimento", prioridade: "Alta", categorias_servico_id: 3, sla_horas_aplicado: 4, ultima_atualizacao_em: 1780000002000}
                "preserva categoria inativa sem troca": {id: 101, tecnico_id: null, atribuido_em: null, status: "Novo", prioridade: "Alta", categorias_servico_id: 9, sla_horas_aplicado: 8, ultima_atualizacao_em: 1780000002000}
                "libera responsável": {id: 101, tecnico_id: null, atribuido_em: null, status: "Em Atendimento", prioridade: "Média", categorias_servico_id: 2, sla_horas_aplicado: 8, ultima_atualizacao_em: 1780000002000}
                "falha ao persistir chamado": null
                "falha ao criar comentário de status": {id: 101, tecnico_id: null, atribuido_em: null, status: "Em Atendimento", prioridade: "Média", categorias_servico_id: 2, sla_horas_aplicado: 8, ultima_atualizacao_em: 1780000002000}
                "falha ao criar auditoria": {id: 101, tecnico_id: null, atribuido_em: null, status: "Novo", prioridade: "Alta", categorias_servico_id: 2, sla_horas_aplicado: 8, ultima_atualizacao_em: 1780000002000}
                "encerra manualmente com alterações": {id: 101, tecnico_id: 10, atribuido_em: 1780000002000, status: "Encerrado", prioridade: "Alta", categorias_servico_id: 2, sla_horas_aplicado: 8, ultima_atualizacao_em: 1780000002000}
                "cancela com alterações combinadas": {id: 101, tecnico_id: 10, atribuido_em: 1780000002000, status: "Cancelado", prioridade: "Alta", categorias_servico_id: 3, sla_horas_aplicado: 4, ultima_atualizacao_em: 1780000002000}
              }
            } as $chamado_atualizado
            precondition ($chamado_atualizado != null) {
              error_type = "standard"
              error = "Não foi possível persistir a tratativa do chamado."
            }

            // A escrita é confirmada antes de qualquer interação. Isto evita
            // registrar histórico de liberação/alteração quando o patch não
            // persistir nulos ou qualquer outro campo funcional.
            db.get chamados {
              field_name = "id"
              field_value = $chamado.id
              mock = {
                "salva alterações combinadas": {id: 101, tecnico_id: 10, atribuido_em: 1780000002000, status: "Em Atendimento", prioridade: "Alta", categorias_servico_id: 3, sla_horas_aplicado: 4, ultima_atualizacao_em: 1780000002000}
                "preserva categoria inativa sem troca": {id: 101, tecnico_id: null, atribuido_em: null, status: "Novo", prioridade: "Alta", categorias_servico_id: 9, sla_horas_aplicado: 8, ultima_atualizacao_em: 1780000002000}
                "libera responsável": {id: 101, tecnico_id: null, atribuido_em: null, status: "Em Atendimento", prioridade: "Média", categorias_servico_id: 2, sla_horas_aplicado: 8, ultima_atualizacao_em: 1780000002000}
                "encerra manualmente com alterações": {id: 101, tecnico_id: 10, atribuido_em: 1780000002000, status: "Encerrado", prioridade: "Alta", categorias_servico_id: 2, sla_horas_aplicado: 8, ultima_atualizacao_em: 1780000002000}
                "cancela com alterações combinadas": {id: 101, tecnico_id: 10, atribuido_em: 1780000002000, status: "Cancelado", prioridade: "Alta", categorias_servico_id: 3, sla_horas_aplicado: 4, ultima_atualizacao_em: 1780000002000}
              }
            } as $chamado_persistido

            precondition ($chamado_persistido != null) {
              error_type = "standard"
              error = "Não foi possível confirmar a persistência da tratativa."
            }

            var $tecnico_persistido_id {
              value = ($chamado_persistido.tecnico_id == null || $chamado_persistido.tecnico_id == 0) ? null : $chamado_persistido.tecnico_id
            }

            precondition ($tecnico_persistido_id == $input.tecnico_id && $chamado_persistido.atribuido_em == $atribuido_em_resultante && $chamado_persistido.status == $input.status && $chamado_persistido.prioridade == $input.prioridade && $chamado_persistido.categorias_servico_id == $input.categorias_servico_id && $chamado_persistido.sla_horas_aplicado == $sla_horas_resultante && $chamado_persistido.ultima_atualizacao_em == $instante) {
              error_type = "standard"
              error = "Não foi possível confirmar a persistência da tratativa."
            }

            conditional {
              if ($input.comentario_status != null && $input.comentario_status != "") {
                db.add interacoes_chamado {
                  data = {tipo_evento: "comentario", mensagem: $input.comentario_status, criado_em: $instante, visibilidade: $input.visibilidade_comentario_status, chamados_id: $chamado.id, usuarios_id: $usuario.id}
                  mock = {
                    "salva alterações combinadas": {id: 201, tipo_evento: "comentario", mensagem: "Início do atendimento", criado_em: 1780000002000, visibilidade: "interna", chamados_id: 101, usuarios_id: 12}
                    "encerra manualmente com alterações": {id: 201, tipo_evento: "comentario", mensagem: "Encerramento validado", criado_em: 1780000002000, visibilidade: "interna", chamados_id: 101, usuarios_id: 12}
                    "cancela com alterações combinadas": {id: 201, tipo_evento: "comentario", mensagem: "Cancelamento validado", criado_em: 1780000002000, visibilidade: "publica", chamados_id: 101, usuarios_id: 12}
                    "falha ao criar comentário de status": null
                  }
                } as $comentario_status_criado
                precondition ($comentario_status_criado != null) {
                  error_type = "standard"
                  error = "Não foi possível registrar o comentário da mudança de Status."
                }
                var.update $comentario_criado {
                  value = $comentario_status_criado
                }
              }
            }

            conditional {
              if ($comentario_criado != null) {
                var.update $alteracoes {
                  value = $alteracoes|set:"comentario_interacao_id":$comentario_criado.id
                }
              }
            }

            // Um Save efetivo gera uma única auditoria, mesmo se vários campos mudarem.
            db.add interacoes_chamado {
              data = {tipo_evento: "alteracao_chamado", alteracoes: $alteracoes, criado_em: $instante, visibilidade: "interna", chamados_id: $chamado.id, usuarios_id: $usuario.id}
              mock = {
                "salva alterações combinadas": {id: 202, tipo_evento: "alteracao_chamado", alteracoes: {responsavel: {anterior: 12, resultante: 10}, status: {anterior: "Novo", resultante: "Em Atendimento"}, prioridade: {anterior: "Média", resultante: "Alta"}, categoria: {anterior: 2, resultante: 3}, sla_horas_aplicado: {anterior: 8, resultante: 4}}, criado_em: 1780000002000, visibilidade: "interna", chamados_id: 101, usuarios_id: 12}
                "preserva categoria inativa sem troca": {id: 202, tipo_evento: "alteracao_chamado", alteracoes: {prioridade: {anterior: "Média", resultante: "Alta"}}, criado_em: 1780000002000, visibilidade: "interna", chamados_id: 101, usuarios_id: 12}
                "libera responsável": {id: 202, tipo_evento: "alteracao_chamado", alteracoes: {responsavel: {anterior: 12, resultante: null}}, criado_em: 1780000002000, visibilidade: "interna", chamados_id: 101, usuarios_id: 12}
                "encerra manualmente com alterações": {id: 202, tipo_evento: "alteracao_chamado", alteracoes: {responsavel: {anterior: 12, resultante: 10}, status: {anterior: "Em Atendimento", resultante: "Encerrado"}, prioridade: {anterior: "Média", resultante: "Alta"}}, criado_em: 1780000002000, visibilidade: "interna", chamados_id: 101, usuarios_id: 12}
                "cancela com alterações combinadas": {id: 202, tipo_evento: "alteracao_chamado", alteracoes: {responsavel: {anterior: 12, resultante: 10}, status: {anterior: "Em Atendimento", resultante: "Cancelado"}, prioridade: {anterior: "Média", resultante: "Alta"}, categoria: {anterior: 2, resultante: 3}, sla_horas_aplicado: {anterior: 8, resultante: 4}}, criado_em: 1780000002000, visibilidade: "interna", chamados_id: 101, usuarios_id: 12}
                "falha ao criar auditoria": null
              }
            } as $evento_alteracao
            precondition ($evento_alteracao != null) {
              error_type = "standard"
              error = "Não foi possível registrar a auditoria da tratativa."
            }
          }
        }
      }
    }

    function.run "service_desk/obter_chamado_tecnico" {
      input = {usuarios_id: $usuario.id, chamados_id: $input.chamados_id}
      mock = {
        "salva alterações combinadas": {chamado: {id: 101, status: "Em Atendimento", prioridade: "Alta", sla_horas_aplicado: 4, tecnico: {id: 10, nome: "Outro Técnico"}, atribuido_em: 1780000002000, ultima_atualizacao_em: 1780000002000, categoria: {id: 3, nome: "Hardware"}}, timeline: [], tecnicos: [{id: 10, nome: "Outro Técnico"}]}
        "salva sem diferença": {chamado: {id: 101, status: "Novo", prioridade: "Média", sla_horas_aplicado: 8, tecnico: null, atribuido_em: null, ultima_atualizacao_em: 1780000000000, categoria: {id: 2, nome: "Rede"}}, timeline: [], tecnicos: []}
        "preserva categoria inativa sem troca": {chamado: {id: 101, status: "Novo", prioridade: "Alta", sla_horas_aplicado: 8, tecnico: null, atribuido_em: null, ultima_atualizacao_em: 1780000002000, categoria: {id: 9, nome: "Legada"}}, timeline: [], tecnicos: []}
        "libera responsável": {chamado: {id: 101, status: "Em Atendimento", prioridade: "Média", sla_horas_aplicado: 8, tecnico: null, atribuido_em: null, ultima_atualizacao_em: 1780000002000, categoria: {id: 2, nome: "Rede"}}, timeline: [], tecnicos: []}
        "encerra manualmente com alterações": {chamado: {id: 101, status: "Encerrado", prioridade: "Alta", sla_horas_aplicado: 8, tecnico: {id: 10, nome: "Outro Técnico"}, atribuido_em: 1780000002000, ultima_atualizacao_em: 1780000002000, categoria: {id: 2, nome: "Rede"}}, timeline: [], tecnicos: [{id: 10, nome: "Outro Técnico"}]}
        "cancela com alterações combinadas": {chamado: {id: 101, status: "Cancelado", prioridade: "Alta", sla_horas_aplicado: 4, tecnico: {id: 10, nome: "Outro Técnico"}, atribuido_em: 1780000002000, ultima_atualizacao_em: 1780000002000, categoria: {id: 3, nome: "Hardware"}}, timeline: [], tecnicos: [{id: 10, nome: "Outro Técnico"}]}
      }
    } as $detalhe
  }

  response = $detalhe

  test "salva alterações combinadas" {
    input = {usuarios_id: 12, chamados_id: 101, tecnico_id: 10, status: "Em Atendimento", prioridade: "Alta", categorias_servico_id: 3, ultima_atualizacao_em: 1780000000000, comentario_status: "Início do atendimento", visibilidade_comentario_status: "interna"}
    expect.to_equal ($response.chamado.status) { value = "Em Atendimento" }
    expect.to_equal ($response.chamado.prioridade) { value = "Alta" }
    expect.to_equal ($response.chamado.tecnico.id) { value = 10 }
    expect.to_equal ($response.chamado.sla_horas_aplicado) { value = 4 }
  }
  test "salva sem diferença" {
    input = {usuarios_id: 12, chamados_id: 101, tecnico_id: null, status: "Novo", prioridade: "Média", categorias_servico_id: 2, ultima_atualizacao_em: 1780000000000}
    expect.to_equal ($response.chamado.ultima_atualizacao_em) { value = 1780000000000 }
  }
  test "preserva categoria inativa sem troca" {
    input = {usuarios_id: 12, chamados_id: 101, tecnico_id: null, status: "Novo", prioridade: "Alta", categorias_servico_id: 9, ultima_atualizacao_em: 1780000000000}
    expect.to_equal ($response.chamado.categoria.id) { value = 9 }
  }
  test "rejeita categoria inativa na troca" {
    input = {usuarios_id: 12, chamados_id: 101, tecnico_id: null, status: "Novo", prioridade: "Média", categorias_servico_id: 9, ultima_atualizacao_em: 1780000000000}
    expect.to_throw { exception = "" }
  }
  test "rejeita comentário ausente" {
    input = {usuarios_id: 12, chamados_id: 101, tecnico_id: null, status: "Em Atendimento", prioridade: "Média", categorias_servico_id: 2, ultima_atualizacao_em: 1780000000000, comentario_status: "   ", visibilidade_comentario_status: "interna"}
    expect.to_throw { exception = "" }
  }
  test "rejeita versão desatualizada" {
    input = {usuarios_id: 12, chamados_id: 101, tecnico_id: null, status: "Novo", prioridade: "Média", categorias_servico_id: 2, ultima_atualizacao_em: 1780000000000}
    expect.to_throw { exception = "" }
  }
  test "falha ao persistir chamado" {
    input = {usuarios_id: 12, chamados_id: 101, tecnico_id: null, status: "Novo", prioridade: "Alta", categorias_servico_id: 2, ultima_atualizacao_em: 1780000000000}
    expect.to_throw { exception = "" }
  }
  test "falha ao criar comentário de status" {
    input = {usuarios_id: 12, chamados_id: 101, tecnico_id: null, status: "Em Atendimento", prioridade: "Média", categorias_servico_id: 2, ultima_atualizacao_em: 1780000000000, comentario_status: "Início validado", visibilidade_comentario_status: "interna"}
    expect.to_throw { exception = "" }
  }
  test "falha ao criar auditoria" {
    input = {usuarios_id: 12, chamados_id: 101, tecnico_id: null, status: "Novo", prioridade: "Alta", categorias_servico_id: 2, ultima_atualizacao_em: 1780000000000}
    expect.to_throw { exception = "" }
  }
  test "encerra manualmente com alterações" {
    input = {usuarios_id: 12, chamados_id: 101, tecnico_id: 10, status: "Encerrado", prioridade: "Alta", categorias_servico_id: 2, ultima_atualizacao_em: 1780000000000, comentario_status: "Encerramento validado", visibilidade_comentario_status: "interna"}
    expect.to_equal ($response.chamado.status) { value = "Encerrado" }
    expect.to_equal ($response.chamado.prioridade) { value = "Alta" }
    expect.to_equal ($response.chamado.tecnico.id) { value = 10 }
  }
  test "cancela com alterações combinadas" {
    input = {usuarios_id: 12, chamados_id: 101, tecnico_id: 10, status: "Cancelado", prioridade: "Alta", categorias_servico_id: 3, ultima_atualizacao_em: 1780000000000, comentario_status: "Cancelamento validado", visibilidade_comentario_status: "publica"}
    expect.to_equal ($response.chamado.status) { value = "Cancelado" }
    expect.to_equal ($response.chamado.prioridade) { value = "Alta" }
    expect.to_equal ($response.chamado.categoria.id) { value = 3 }
    expect.to_equal ($response.chamado.sla_horas_aplicado) { value = 4 }
  }
  test "rejeita aguardando terceiro" {
    input = {usuarios_id: 12, chamados_id: 101, tecnico_id: null, status: "Aguardando Terceiro", prioridade: "Média", categorias_servico_id: 2, ultima_atualizacao_em: 1780000000000, comentario_status: "Não deve salvar", visibilidade_comentario_status: "interna"}
    expect.to_throw { exception = "" }
  }
  test "rejeita terminal" {
    input = {usuarios_id: 13, chamados_id: 101, tecnico_id: 12, status: "Encerrado", prioridade: "Média", categorias_servico_id: 2, ultima_atualizacao_em: 1780000000000}
    expect.to_throw { exception = "" }
  }
  test "libera responsável" {
    input = {usuarios_id: 12, chamados_id: 101, tecnico_id: null, status: "Em Atendimento", prioridade: "Média", categorias_servico_id: 2, ultima_atualizacao_em: 1780000000000}
    expect.to_be_null ($response.chamado.tecnico)
    expect.to_be_null ($response.chamado.atribuido_em)
    expect.to_equal ($response.chamado.status) { value = "Em Atendimento" }
  }
  guid = "miraValidarSaveTratativa01"
}
