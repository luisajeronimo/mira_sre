// Fila global em tabela com filtros simples de atribuição.
query "tecnico/chamados" verb=GET {
  api_group = "MIRA Service Desk"
  auth = "usuarios"

  input {
    text numero? filters=trim
    text status?
    text ativo_ids?
    timestamp? data_inicio?
    timestamp? data_fim?
    timestamp? ultima_atualizacao_inicio?
    timestamp? ultima_atualizacao_fim?
    text loja_ids?
    text prioridades?
    text responsavel_ids?
    bool incluir_nao_atribuido?
    text ordenar_por? filters=trim
    text direcao? filters=trim
    bool somente_atribuidos_a_mim?
  }

  stack {
    var $status {
      value = $input.status == null ? [] : ($input.status|json_decode)
    }

    var $ativo_ids {
      value = $input.ativo_ids == null ? [] : ($input.ativo_ids|json_decode)
    }

    var $loja_ids {
      value = $input.loja_ids == null ? [] : ($input.loja_ids|json_decode)
    }

    var $prioridades {
      value = $input.prioridades == null ? [] : ($input.prioridades|json_decode)
    }

    var $responsavel_ids {
      value = $input.responsavel_ids == null ? [] : ($input.responsavel_ids|json_decode)
    }

    var $resultado {
      value = null
    }

    conditional {
      if (!(($status|is_array) && ($ativo_ids|is_array) && ($loja_ids|is_array) && ($prioridades|is_array) && ($responsavel_ids|is_array))) {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }

        var.update $resultado {
          value = {
            code   : "ERROR_CODE_INPUT_ERROR"
            message: "Filtros múltiplos inválidos."
            payload: {}
          }
        }
      }

      else {
        function.run "service_desk/listar_chamados_tecnico" {
          input = {
            usuarios_id              : $auth.id
            numero                   : $input.numero
            status                   : $status
            ativo_ids                : $ativo_ids
            data_inicio              : $input.data_inicio
            data_fim                 : $input.data_fim
            ultima_atualizacao_inicio: $input.ultima_atualizacao_inicio
            ultima_atualizacao_fim   : $input.ultima_atualizacao_fim
            loja_ids                 : $loja_ids
            prioridades              : $prioridades
            responsavel_ids          : $responsavel_ids
            incluir_nao_atribuido    : $input.incluir_nao_atribuido
            ordenar_por              : $input.ordenar_por
            direcao                  : $input.direcao
            somente_atribuidos_a_mim : $input.somente_atribuidos_a_mim
          }
        } as $lista

        var.update $resultado {
          value = $lista
        }
      }
    }
  }

  response = $resultado
  guid = "miraFilaTecnicoApi01"
}