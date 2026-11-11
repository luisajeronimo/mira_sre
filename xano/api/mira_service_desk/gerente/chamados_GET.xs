// Lista funcional de chamados da Loja do Gerente.
query "gerente/chamados" verb=GET {
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
    text ordenar_por? filters=trim
    text direcao? filters=trim
    int[]? loja_ids?
    text[]? prioridades?
    int[]? responsavel_ids?
    bool? incluir_nao_atribuido?
  }

  stack {
    var $status {
      value = $input.status == null ? [] : ($input.status|json_decode)
    }

    var $ativo_ids {
      value = $input.ativo_ids == null ? [] : ($input.ativo_ids|json_decode)
    }

    var $resultado {
      value = null
    }

    conditional {
      if (!(($status|is_array) && ($ativo_ids|is_array))) {
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

      elseif ($input.loja_ids != null || $input.prioridades != null || $input.responsavel_ids != null || $input.incluir_nao_atribuido != null) {
        util.set_header {
          value = "HTTP/1.1 422 Unprocessable Entity"
          duplicates = "replace"
        }

        var.update $resultado {
          value = {
            code   : "ERROR_CODE_INPUT_ERROR"
            message: "Filtro não permitido."
            payload: {}
          }
        }
      }

      else {
        function.run "service_desk/listar_chamados_gerente" {
          input = {
            usuarios_id              : $auth.id
            numero                   : $input.numero
            status                   : $status
            ativo_ids                : $ativo_ids
            data_inicio              : $input.data_inicio
            data_fim                 : $input.data_fim
            ultima_atualizacao_inicio: $input.ultima_atualizacao_inicio
            ultima_atualizacao_fim   : $input.ultima_atualizacao_fim
            ordenar_por              : $input.ordenar_por
            direcao                  : $input.direcao
          }
        } as $lista

        var.update $resultado {
          value = $lista
        }
      }
    }
  }

  response = $resultado
  guid = "6h4T1Nwn7Coht05btWyScvCe-K8"
}